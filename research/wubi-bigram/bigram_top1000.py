#!/usr/bin/env python3
"""用权威字频表 top 1000 常用字统计五笔 bigram"""
import csv
import json
import re
from collections import Counter

# 1. 读取权威字频表前 1000 字
top1000_chars = set()
with open('/tmp/hanzi_freq.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 1000:
            break
        top1000_chars.add(row['character'])

print(f"权威字频表 top 1000 字已加载: {len(top1000_chars)} 字")
print(f"前10: 的一是不了在人有我他")

# 2. 读取五笔词库，匹配 top 1000 字的编码
dict_path = "/tmp/rime-wubi-86-single/wubi86.dict.yaml"
matched = []
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
            char = parts[0].strip()
            code = parts[1].strip()
            if char in top1000_chars and re.match(r'^[a-z]+$', code):
                matched.append((char, code))

print(f"匹配到编码: {len(matched)} 条（含一字多码）")

# 去重：每个字只取最短编码（简码优先，这是实际打字习惯）
char_codes = {}
for char, code in matched:
    if char not in char_codes or len(code) < len(char_codes[char]):
        char_codes[char] = code

print(f"去重后（每字取最短码）: {len(char_codes)} 字")
unmatched = top1000_chars - set(char_codes.keys())
if unmatched:
    print(f"未匹配: {len(unmatched)} 字: {''.join(list(unmatched)[:20])}")

# 3. 统计 bigram
bigram_counter = Counter()
for char, code in char_codes.items():
    for i in range(len(code) - 1):
        bg = code[i] + code[i+1]
        bigram_counter[bg] += 1

all_bigrams = sorted(bigram_counter.items(), key=lambda x: x[1])
bigram_dict = {bg: cnt for bg, cnt in all_bigrams}

with open('/tmp/wubi_bigram_top1000_authoritative.json', 'w') as f:
    json.dump(bigram_dict, f, indent=2)

# 4. Home row 分析
home_keys = set('asdfjkl')
all_possible = []
for a in sorted(home_keys):
    for b in sorted(home_keys):
        if a != b:
            cnt = bigram_counter.get(a+b, 0)
            all_possible.append((a+b, cnt))
all_possible.sort(key=lambda x: x[1])

# 加载之前的全量数据做对比
with open('/tmp/wubi_bigram_all.json', 'r') as f:
    all_data = json.load(f)

total = sum(bigram_counter.values())
print(f"\nbigram 种类: {len(bigram_counter)}, 总次数: {total}")
print(f"\n=== Home Row (asdfjkl) - 权威 Top1000 vs 全量对比 ===")
print(f"{'bigram':<8} {'top1000':>8} {'全量':>8} {'占比':>10}")
print("-" * 38)
for bg, cnt in all_possible:
    all_cnt = all_data.get(bg, 0)
    pct = cnt / total * 100 if total else 0
    marker = " ⭐" if cnt <= 2 else ""
    print(f"{bg:<8} {cnt:>8} {all_cnt:>8} {pct:>9.3f}%{marker}")

