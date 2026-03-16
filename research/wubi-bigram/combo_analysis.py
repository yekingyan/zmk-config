#!/usr/bin/env python3
"""
五笔 Combo Key 第一性原理分析
目标：手指不移动 + 同时双击 + 最小误触 → 最优组合键方案
"""
import csv
import json
import re
from collections import Counter
from itertools import combinations

# ============================================================
# 1. 数据准备
# ============================================================

# 权威字频表
freq_chars = {}  # {char: rank}
with open('/tmp/hanzi_freq.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        freq_chars[row['character']] = i + 1

# 五笔词库
dict_path = "/tmp/rime-wubi-86-single/wubi86.dict.yaml"
all_entries = []
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
            if re.match(r'^[a-z]+$', code) and len(char) == 1:
                all_entries.append((char, code))

# 每字取最短码
char_best_code = {}
for char, code in all_entries:
    if char not in char_best_code or len(code) < len(char_best_code[char]):
        char_best_code[char] = code

# 按不同频率段统计 bigram
tiers = [300, 500, 1000, 2000, 99999]  # 99999 = 全量
tier_labels = ['top300', 'top500', 'top1000', 'top2000', '全量']

tier_bigrams = {}
for tier, label in zip(tiers, tier_labels):
    bg = Counter()
    count = 0
    for char, rank in freq_chars.items():
        if rank > tier and tier != 99999:
            continue
        if char in char_best_code:
            code = char_best_code[char]
            for i in range(len(code) - 1):
                bg[code[i] + code[i+1]] += 1
            count += 1
    # 全量用所有编码
    if tier == 99999:
        bg = Counter()
        for _, code in all_entries:
            for i in range(len(code) - 1):
                bg[code[i] + code[i+1]] += 1
        count = len(all_entries)
    tier_bigrams[label] = bg
    print(f"{label}: {count} 字/编码, {len(bg)} 种 bigram, {sum(bg.values())} 次")

# ============================================================
# 2. 键盘物理模型
# ============================================================

# QWERTY home row 手指分配
finger_map = {
    'a':0, 's':1, 'd':2, 'f':3, 'g':3,
    'h':4, 'j':4, 'k':5, 'l':6, ';':7,
}
finger_name = ['左小指','左无名','左中指','左食指','右食指','右中指','右无名','右小指']

# Home row 键位坐标（相对位置，单位：1u）
key_pos = {
    'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 4,
    'h': 5, 'j': 6, 'k': 7, 'l': 8,
}

# 手指静息位（自然放置）
rest_pos = {'a':0, 's':1, 'd':2, 'f':3, 'j':6, 'k':7, 'l':8}
# g(4) 和 h(5) 需要食指移动

def comfort_score(k1, k2):
    """
    舒适度评分（0-100），越高越好
    考虑因素：
    1. 手指是否需要移动（离开静息位）
    2. 同手 vs 跨手（combo 是同时按，同手更容易协调）
    3. 相邻手指 vs 间隔手指
    4. 小指参与的惩罚
    5. 同一手指的不同键（物理上不可能同时按）
    """
    f1, f2 = finger_map[k1], finger_map[k2]
    
    # 同一手指 → 不可能同时按（除非是同一个键）
    if f1 == f2:
        return -1  # 物理不可能
    
    score = 50  # 基础分
    
    # 是否需要离开静息位
    needs_move = k1 not in rest_pos or k2 not in rest_pos
    if needs_move:
        score -= 15  # 需要移动手指
    
    # 同手 vs 跨手
    left1 = f1 <= 3
    left2 = f2 <= 3
    same_hand = left1 == left2
    
    if same_hand:
        score += 20  # 同手更容易同时按
        # 相邻手指加分
        if abs(f1 - f2) == 1:
            score += 20  # 相邻手指最自然
        elif abs(f1 - f2) == 2:
            score += 10  # 隔一个手指也行
    else:
        score += 5  # 跨手也可以，但协调性差一点
    
    # 小指惩罚
    if f1 in (0, 7) or f2 in (0, 7):
        score -= 20
    
    # 物理距离（键位间距）
    dist = abs(key_pos[k1] - key_pos[k2])
    if dist <= 1:
        score += 10
    elif dist >= 4:
        score -= 10
    
    return score

# ============================================================
# 3. 评估所有 home row 组合
# =====================================================

candidates = list('asdfghjkl')
results = []

for k1, k2 in combinations(candidates, 2):
    cs = comfort_score(k1, k2)
    if cs < 0:
        continue  # 同手指，物理不可能
    
    # 各频率段的 bigram 频率（双向合并，因为 combo 不分先后）
    freqs = {}
    for label in tier_labels:
        bg = tier_bigrams[label]
        freqs[label] = bg.get(k1+k2, 0) + bg.get(k2+k1, 0)
    
    f1, f2 = finger_map[k1], finger_map[k2]
    results.append({
        'combo': k1+k2,
        'comfort': cs,
        'freqs': freqs,
        'fingers': f"{finger_name[f1]}({k1})+{finger_name[f2]}({k2})",
        'same_hand': (f1 <= 3) == (f2 <= 3),
        'needs_move': k1 not in rest_pos or k2 not in rest_pos,
    })

# ========================================================
# 4. 综合评分与方案生成
# ============================================================

# 综合评分 = comfort * 2 - top300_freq * 5 - top500_freq * 3 - top1000_freq * 2 - top2000_freq
for r in results:
    r['score'] = (
        r['comfort'] * 2
        - r['freqs']['top300'] * 5
        - r['freqs']['top500'] * 3
        - r['freqs']['top1000'] * 2
        - r['freqs']['top2000'] * 1
    )

results.sort(key=lambda x: -x['score'])

print("\n" + "=" * 90)
print("全量候选排名（综合评分 = 舒适度×2 - 加权频率惩罚）")
print("=" * 90)
print(f"{'排名':<4} {'组合':<6} {'评分':>6} {'舒适':>4} {'top300':>7} {'top500':>7} {'top1000':>8} {'top2000':>8} {'全量':>8}  {'手指'}")
print("-" * 90)
for i, r in enumerate(results):
    f = r['freqs']
    marker = ""
    if r['score'] >= 140:
        marker = " ⭐⭐⭐"
    elif r['score'] >= 100:
        marker = " ⭐⭐"
    elif r['score'] >= 60:
        marker = " ⭐"
    print(f"{i+1:<4} {r['combo']:<6} {r['score']:>6} {r['comfort']:>4} {f['top300']:>7} {f['top500']:>7} {f['top1000']:>8} {f['top2000']:>8} {f['全量']:>8}  {r['fingers']}{marker}")

# ============================================================
# 5. 生成方案
# ============================================================

print("\n" + "=" * 90)
print("方案对比")
print("=" * 90)

# 方案 A：纯右手（不含小指）
print("\n【方案 A】纯右手同手组合（不含小指，不需移动手指）")
plan_a = [r for r in results if r['same_hand'] and not r['needs_move'] 
          and finger_map[r['combo'][0]] >= 4 and finger_map[r['combo'][1]] >= 4
          and finger_map[r['combo'][0]] not in (7,) and finger_map[r['combo'][1]] not in (7,)]
for i, r in enumerate(plan_a[:5]):
    f = r['freqs']
    print(f"  {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, {r['fingers']}")

# 方案 B：左右对称（左手 + 右手各取最优）
print("\n【方案 B】左右对称（每手各取最优，不含小指）")
left_best = [r for r in results if r['same_hand'] and not r['needs_move']
             and finger_map[r['combo'][0]] <= 3 and finger_map[r['combo'][1]] <= 3
             and finger_map[r['combo'][0]] not in (0,) and finger_map[r['combo'][1]] not in (0,)]
right_best = [r for r in results if r['same_hand'] and not r['needs_move']
              and finger_map[r['combo'][0]] >= 4 and finger_map[r['combo'][1]] >= 4
              and finger_map[r['combo'][0]] not in (7,) and finger_map[r['combo'][1]] not in (7,)]
print("  左手:")
for i, r in enumerate(left_best[:3]):
    f = r['freqs']
    print(f"    {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, {r['fingers']}")
print("  右手:")
for i, r in enumerate(right_best[:3]):
    f = r['freqs']
    print(f"    {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, {r['fingers']}")

# 方案 C：全局最优 top 5（不限手，不含小指）
print("\n【方案 C】全局最优 Top 5（不限手，不含小指）")
no_pinky = [r for r in results 
            if finger_map[r['combo'][0]] not in (0, 7) 
            and finger_map[r['combo'][1]] not in (0, 7)]
for i, r in enumerate(no_pinky[:5]):
    f = r['freqs']
    print(f"  {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, 舒适:{r['comfort']}, {r['fingers']}")

# 方案 D：允许小指的全局最优 top 5
print("\n【方案 D】全局最优 Top 5（允许小指）")
for i, r in enumerate(results[:5]):
    f = r['freqs']
    print(f"  {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, 舒适:{r['comfort']}, {r['fingers']}")

# 方案 E：含 g/h 扩展键的最优
print("\n【方案 E】含食指扩展键(g/h)的最优 Top 5")
with_extend = [r for r in results if r['needs_move']]
for i, r in enumerate(with_extend[:5]):
    f = r['freqs']
    print(f"  {i+1}. {r['combo']} — 评分:{r['score']}, top300:{f['top300']}, top1000:{f['top1000']}, 舒适:{r['comfort']}, {r['fingers']}")

