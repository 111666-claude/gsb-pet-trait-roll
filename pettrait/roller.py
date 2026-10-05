"""宠物词条抽取：按权重轮盘抽词条，连续没出稀有就保底。

实现要点：
- 权重轮盘用 Vose 别名表预处理，单次抽取摊还 O(1)，小权重词条也能出。
- 随机源只用构造时传入的 seed（random.Random），不碰时间戳，序列可复现。
- 连续 pity_limit 次没出 rare=1 词条后，下一次从稀有词条子表里必出一条，抽出后计数清零。
- 同一个 req_id 只抽一次，重复调用直接返回上次结果，不推进保底计数。
"""

import random


def load_traits(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        header = handle.readline().strip().split(",")
        for line in handle:
            line = line.strip()
            if line:
                rows.append(dict(zip(header, line.split(","))))
    return rows


def _build_alias(weights):
    """Vose 别名表：O(n) 预处理，之后每次抽取 O(1)。"""
    size = len(weights)
    total = sum(weights)
    prob = [0.0] * size
    alias = [0] * size
    scaled = [weight / total * size for weight in weights]
    small = [index for index, value in enumerate(scaled) if value < 1.0]
    large = [index for index, value in enumerate(scaled) if value >= 1.0]
    while small and large:
        low = small.pop()
        high = large[-1]
        prob[low] = scaled[low]
        alias[low] = high
        scaled[high] = scaled[high] + scaled[low] - 1.0
        if scaled[high] < 1.0:
            large.pop()
            small.append(high)
    for index in small + large:
        prob[index] = 1.0
    return prob, alias


class Roller:
    """词条抽取台账。"""

    def __init__(self, traits, seed, pity_limit):
        self.traits = traits
        self.seed = seed
        self.pity_limit = pity_limit
        self.miss = 0
        self.seen = {}
        self.scanned = 0
        self._rng = random.Random(seed)
        self._names = [item["trait"] for item in traits]
        self._weights = [float(item["weight"]) for item in traits]
        self._indexes = list(range(len(traits)))
        self._rare = [index for index, item in enumerate(traits) if int(item["rare"])]
        self.scanned += len(traits)
        self._prob, self._alias = _build_alias(self._weights)
        if self._rare:
            rare_weights = [self._weights[index] for index in self._rare]
            self._rare_prob, self._rare_alias = _build_alias(rare_weights)
            self.scanned += len(self._rare)
        else:
            self._rare_prob, self._rare_alias = None, None

    def _draw(self, prob, alias, indexes):
        column = self._rng.randrange(len(prob))
        if self._rng.random() < prob[column]:
            return indexes[column]
        return indexes[alias[column]]

    def roll(self, req_id):
        """抽一条词条：同一 req_id 幂等，保底到点必出稀有。"""
        if req_id in self.seen:
            return self.seen[req_id]
        self.scanned += 1
        if self.miss >= self.pity_limit and self._rare:
            index = self._draw(self._rare_prob, self._rare_alias, self._rare)
        else:
            index = self._draw(self._prob, self._alias, self._indexes)
        picked = self._names[index]
        if int(self.traits[index]["rare"]):
            self.miss = 0
        else:
            self.miss += 1
        self.seen[req_id] = picked
        return picked
