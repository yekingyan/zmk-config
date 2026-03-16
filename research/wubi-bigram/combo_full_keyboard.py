#!/usr/bin/env python3
"""全键盘 combo 分析（排除 z，含所有字母键 a-y）"""
import csv
import re
from collections import Counter
from itertools import combinations

# 数据加载
freq_chars = {}
with open('/tmp/hanzi_freq.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        freq_chars[row['character']] = i + 1

dict_path = "/tmp/rime-wubi-86-single/wubi86.dict.yaml"
all_entries = []
in_body = False
with open(dict_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line == '...':
            in_body = True
            continue
        if not in_body or not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            char, code = parts[0].strip(), parts[1].strip()
            if re.match(r'^[a-z]+$', code) and len(char) == 1:
                all_entries.append((char, code))

char_best = {}
for char, code in all_entries:
    if char not in char_best or len(code) < len(char_best[char]):
        char_best[char] = code

# QWERTY 手指分配（标准指法）
finger_map = {
    'q':0, 'a':0, # 左小指 (z 排除)
    'w':1, 's':1, 'x':1,  # 左无名
    'e':2, 'd':2, 'c':2,  # 左中指
    'r':3, 'f':3, 'v':3, 't':3, 'g':3, 'b':3,  # 左食指
    'y':4, 'h':4, 'n':4, 'u':4, 'j':4, 'm':4,  # 右食指
    'i':5, 'k':5,  # 右中指
    'o':6, 'l':6,  # 右无名
    'p':7,  # 右小指
}
finger_name = ['左小指','左无名','左中指','左食指','右食指','右中指','右无名','右小指']

# 键位行列坐标 (row, col) 用于距离计算
key_pos = {
    'q':(0,0),'w':(0,1),'e':(0,2),'r':(0,3),'t':(0,4),'y':(0,5),'u':(0,6),'i':(0,7),'o':(0,8),'p':(0,9),
    'a':(1,0),'s':(1,1),'d':(1,2),'f':(1,3),'g':(1,4),'h':(1,5),'j':(1,6),'k':(1,7),'l':(1,8),
    'x':(2,1),'c':(2,2),'v':(2,3),'b':(2,4),'n':(2,5),'m':(2,6),
}

# 静息位
rest_keys = set('asdfjkl')

# 所有候选键（排除 z）
all_keys = [c for c in 'qwertyuiopasdfghjklxcvbnm' if c != 'z']

def comfort_score(k1, k2):
    f1, f2 = finger_map[k1], finger_map[k2]
    if f1 == f2:
        return -999  # 同手指
    
    score = 50
    
    # 静息位
    moves = (k1 not in rest_keys) + (k2 not in rest_keys)
    score -= moves * 12
    
    # 同手 vs 跨手
    left1, left2 = f1 <= 3, f2 <= 3
    same_hand = left1 == left2
    if same_hand:
        score += 20
        if abs(f1 - f2) == 1: score += 20
        elif abs(f1 - f2) == 2: score += 10
    else:
        score += 5
    
    # 小指
    if f1 in (0,7) or f2 in (0,7):
        score -= 20
    
    # 同行加分（更容易同时按）
    r1, c1 = key_pos[k1]
    r2, c2 = key_pos[k2]
    if r1 == r2:
        score += 5
    
    # 物理距离惩罚
    dist = ((r1-r2)**2 + (c1-c2)**2) ** 0.5
    if dist > 3:
        score -= 10
    
    return score

# 评估所有组合
results = []
for k1, k2 in combinations(all_keys, 2):
    cs = comfort_score(k1, k2)
    if cs <= -900:
        continue
    
    c1, c2 = k1+k2, k2+k1
    hits = {300:[], 500:[], 1000:[], 2000:[]}
    total = 0
    for char, code in char_best.items():
        for i in range(len(code) - 1):
            bg = code[i] + code[i+1]
            if bg == c1 or bg == c2:
                rank = freq_chars.get(char, 99999)
                total += 1
                for t in [300,500,1000,2000]:
                    if rank <= t:
                        hits[t].append((char, code, rank))
                break
    
    score = cs * 2 - len(hits[300])*5 - len(hits[500])*3 - len(hits[1000])*2 - len(hits[2000])*1
    
    f1, f2 = finger_map[k1], finger_map[k2]
    results.append({
        'combo': k1+k2,
        'score': score,
        'comfort': cs,
        'hits': hits,
        'total': total,
        'fingers': f"{finger_name[f1]}({k1})+{finger_name[f2]}({k2})",
        'home': k1 in rest_keys and k2 in rest_keys,
    })

results.sort(key=lambda x: -x['score'])

# Top 30
print("=" * 100)
print("全键盘 Combo 候选 Top 30（排除 z）")
print("=" * 100)
print(f"{'#':<3} {'组合':<5} {'评分':>5} {'舒适':>4} {'t300':>5} {'t500':>5} {'t1k':>5} {'t2k':>5} {'全量':>5} {'home':>5} {'手指'}")
print("-" * 100)
for i, r in enumerate(results[:30]):
    home = "✓" if r['home'] else ""
    star = ""
    if len(r['hits'][300]) == 0 and r['comfort'] >= 60: star = " ⭐⭐⭐"
    elif len(r['hits'][300]) == 0 and r['comfort'] >= 30: star = " ⭐⭐"
    elif len(r['hits'][300]) == 0: star = " ⭐"
    print(f"{i+1:<3} {r['combo']:<5} {r['score']:>5} {r['comfort']:>4} {len(r['hits'][300]):>5} {len(r['hits'][500]):>5} {len(r['hits'][1000]):>5} {len(r['hits'][2000]):>5} {r['total']:>5} {home:>5} {r['fingers']}{star}")

# Top 30 命中字详情
print("\n" + "=" * 100)
print("Top 30 命中汉字详情")
print("=" * 100)
for i, r in enumerate(results[:30]):
    t3 = sorted(r['hits'][300], key=lambda x: x[2])
    t10 = sorted(r['hits'][1000], key=lambda x: x[2])
    t3_str = ' '.join([f"{ch}#{rk}" for ch,co,rk in t3]) if t3 else "无"
    # 只显示 top1000 中不在 top300 的
    t10_extra = [x for x in t10 if x[2] > 300]
    t10_str = ' '.join([f"{ch}#{rk}" for ch,co,rk in t10_extra[:8]]) if t10_extra else ""
    print(f"{i+1:>2}. {r['combo']} | top300: {t3_str}" + (f" | top1000额外: {t10_str}" if t10_str else ""))

# 全部 top300 零命中的组合
print("\n" + "=" * 100)
print("所有 top300 零命中的组合（按评分降序）")
print("=" * 100)
zero300 = [r for r in results if len(r['hits'][300]) == 0]
print(f"共 {len(zero300)} 个\n")
print(f"{'#':<3} {'组合':<5} {'评分':>5} {'舒适':>4} {'t500':>5} {'t1k':>5} {'t2k':>5} {'全量':>5} {'手指'}")
print("-" * 85)
for i, r in enumerate(zero300[:40]):
    print(f"{i+1:<3} {r['combo']:<5} {r['score']:>5} {r['comfort']:>4} {len(r['hits'][500]):>5} {len(r['hits'][1000]):>5} {len(r['hits'][2000]):>5} {r['total']:>5} {r['fingers']}")

