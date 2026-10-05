"""宠物词条抽取：按权重轮盘抽词条，连续没出稀有就保底。

轮盘在初始化时预处理成前缀和，单次抽取摊还 O(1)；随机源只用 seed，
同一个 req_id 只抽一次，重复调用返回上次结果且不推进保底计数。
"""

import bisect
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
        self._prefix = []
        self._rare_prefix = []
        total = 0
        rare_total = 0
        for item in traits:
            self.scanned += 1
            total += int(item["weight"])
            self._prefix.append(total)
            if int(item["rare"]):
                rare_total += int(item["weight"])
            self._rare_prefix.append(rare_total)
        self._total = total
        self._rare_total = rare_total

    def _draw(self, prefix, total):
        return bisect.bisect_right(prefix, self._rng.randrange(total))

    def roll(self, req_id):
        """抽一条词条：权重轮盘 + 保底 + req_id 幂等。"""
        if req_id in self.seen:
            return self.seen[req_id]
        self.scanned += 1
        if self.miss >= self.pity_limit and self._rare_total > 0:
            index = self._draw(self._rare_prefix, self._rare_total)
        else:
            index = self._draw(self._prefix, self._total)
        item = self.traits[index]
        picked = item["trait"]
        if int(item["rare"]):
            self.miss = 0
        else:
            self.miss += 1
        self.seen[req_id] = picked
        return picked
