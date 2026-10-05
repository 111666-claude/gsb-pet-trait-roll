"""宠物词条抽取：按权重轮盘抽词条，连续没出稀有就保底。

缺陷：权重不参与（永远取权重最大的那一条）、保底不生效、种子被时间戳顶掉（不可复现）、
同一个 req_id 重复生效、每次抽取全扫词条表。
"""

import time


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

    def roll(self, req_id):
        """抽一条词条。缺陷：权重不参与、保底不生效、种子换成时间戳、不查 req、全扫词条表。"""
        self.scanned += len(self.traits)
        best = None
        for item in self.traits:
            if best is None or int(item["weight"]) > int(best["weight"]):
                best = item
        picked = best["trait"]
        if int(best["rare"]):
            self.miss = 0
        else:
            self.miss += 1
        self.seed = int(time.time() * 1000) % 100000
        self.seen[req_id] = picked
        return picked
