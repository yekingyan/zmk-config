#!/usr/bin/env python3
"""统计五笔单字词库 bigram 频率，重点标注 home row 组合"""
import json
import re
from collections import Counter

dict_path = "/tmp/rime-wubi-86-single/wubi86.dict.yaml"

# 解析词库，提取编码
codes = []
in_body = False
with open(dict_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line == '...':
            in_body = True
            continue
        if not in_body:
            continue
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            code = parts[1].strip()
            if re.match(r'^[a-z]+$', code):
                codes.append(code)

# 统计 bigram
bigram_counter = Counter()
for code in codes:
    for i in range(len(code) - 1):
        bg = code[i] + code[i+1]
        bigram_counter[bg] += 1

# 全量排序（升序）
all_bigrams = sorted(bigram_counter.items(), key=lambda x: x[1])

# 输出全量 JSON
bigram_dict = {bg: cnt for bg, cnt in all_bigrams}
with open('/tmp/wubi_bigram_all.json', 'w') as f:
    json.dump(bigram_dict, f, indent=2)

# Home row 分析: a s d f j k l (不含分号，五笔不用)
home_keys = set('asdfjkl')
home_bigrams = []
for bg, cnt in all_bigrams:
    if bg[0] in home_keys and bg[1] in home_keys:
        home_bigrams.append((bg, cnt))

# 所有可能的 home row 双键组合（含方向）
all_possible = []
for a in sorted(home_keys):
    for b in sorted(home_keys):
        if a != b:
            cnt = bigram_counter.get(a+b, 0)
            all_possible.append((a+b, cnt))
all_possible.sort(key=lambda x: x[1])

print(f"=== 词库统计 ===")
print(f"总编码数: {len(codes)}")
print(f"总 bigram 种类: {len(bigram_counter)}")
print(f"总 bigram 次数: {sum(bigram_counter.values())}")
print()
print(f"=== Home Row (asdfjkl) 双键组合 - 按频率升序 ===")
print(f"{'bigram':<8} {'频率':>8}  {'占比':>8}")
print("-" * 28)
for bg, cnt in all_possible:
    total = sum(bigram_counter.values())
    pct = cnt / total * 100 if total else 0
    marker = " ⭐" if cnt == 0 else ""
    print(f"{bg:<8} {cnt:>8}  {pct:>7.3f}%{marker}")

print()
print(f"全量 bigram 已写入 /tmp/wubi_bigram_all.json ({len(bigram_dict)} 种)")
