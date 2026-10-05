"""词条抽取入口：跑样例并输出一行 JSON 报告。"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pettrait.roller import Roller, load_traits  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def main(argv=None):
    name = (argv or sys.argv[1:])[:1]
    sample = name[0] if name else "--sample=pity"
    traits = load_traits(os.path.join(HERE, "data", "traits.csv"))
    if sample == "--sample=pity":
        book = Roller(traits, 7, 3)
        picks = [book.roll("r-%d" % index) for index in range(4)]
        emit({"picks": picks, "last": picks[-1]})
    elif sample == "--sample=seed":
        left = Roller(traits, 7, 100)
        right = Roller(traits, 7, 100)
        emit({"same": [left.roll("r1")] == [right.roll("r1")]})
    elif sample == "--sample=dup":
        book = Roller(traits, 7, 100)
        book.roll("r1")
        before = book.miss
        book.roll("r1")
        emit({"miss": before, "again": book.miss})
    elif sample == "--sample=weight":
        book = Roller(traits, 7, 100)
        counts = {}
        for index in range(1000):
            counts[book.roll("r-%d" % index)] = counts.get(book.roll("r-%d" % index), 0) + 1
        emit({"kinds": len(counts)})
    elif sample == "--sample=work":
        book = Roller([{"trait": "t-%d" % index, "weight": "1", "rare": "0"} for index in range(3000)], 7, 100)
        for index in range(3000):
            book.roll("r-%d" % index)
        emit({"scanned": book.scanned})
    else:
        raise SystemExit("需要 --sample=pity|seed|dup|weight|work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
