# pet-trait-roll

宠物词条抽取：按权重轮盘抽词条，连续没出稀有就保底，结果写一行 JSON，只用 Python 标准库。

```
python3 main.py --sample=pity
python3 main.py --sample=seed
python3 main.py --sample=dup
python3 main.py --sample=weight
python3 main.py --sample=work
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **权重轮盘**：每条词条按 `weight` 占比被抽到，权重更大的更容易出，但仍要能出到小权重词条。
- **确定性**：同一个 `seed` 加同一串请求，抽出的词条序列逐条一致（不许用时间戳当随机源）。
- **保底**：连续 `pity_limit` 次没抽到 `rare=1` 的词条时，下一次必定抽到稀有词条，抽出后计数清零。
- **幂等**：同一个 `req_id` 只抽一次，重复调用返回上次结果且不推进保底计数。
- **代价**：抽取摊还 O(词条数)，`scanned` 不随抽取次数乘词条数增长；每秒 10 万次抽取。

## 输出契约（不改格式）

```
{"picks": [..], "last": ".."}
{"same": ..}
{"miss": .., "again": ..}
{"kinds": ..}
{"scanned": ..}
```

## 目录

```
data/traits.csv     词条权重表
pettrait/roller.py  轮盘、保底与幂等
main.py             命令行入口与 JSON 报告
tests/test_roller.py unittest 用例
```
