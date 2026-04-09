#!/usr/bin/env python3
"""键盘按键物理距离计算器（Sweep 风格，每侧 2 拇指键）

打印所有键的绝对坐标，以及到参考点的 Δx / Δy / 直线距离。

键盘参数：
  - 水平键间距: 19mm
  - 列错位（相邻列高度差，以 e/i 列为 y=0 基准）:
      q→w: 12mm  |  w→e: 6.14mm  |  e→r: 4.572mm  |  r→t: 2.568mm
  - 行间距: 19mm（向下为负 y）
  - 拇指键: LT1/LT2（左）、RT1/RT2（右），坐标已手动标定

用法：
  python key_distance.py           # 参考点默认为 e 键坐标
  python key_distance.py 50 -15   # 参考点为 (50, -15)
"""

import argparse
import math

# ─── 键盘物理参数 ─────────────────────────────────────────────────────────────

KEY_SPACING    = 19.0    # 水平 / 垂直键间距 (mm)

# 相邻列高度差 (mm)
STAGGER_QW     = 12.0    # q→w 列差
STAGGER_WE     =  6.14   # w→e 列差
STAGGER_ER     =  4.572  # e→r 列差
STAGGER_RT     =  2.568  # r→t 列差

# 拇指键相对 b 键的偏移 (mm)
THUMB1_DX      = -9.708
THUMB1_DY      = -20.280
THUMB2_DX      =  9.970
THUMB2_DY      = -28.496

# 打孔圆心相对参考键的偏移 (mm)
HOLE1_DX       = -11.803   # 相对 w 键
HOLE1_DY       =  -1.294
HOLE2_DX       =  12.404   # 相对 z 键
HOLE2_DY       =   1.462
HOLE3_DX       =   9.538   # 相对 e 键
HOLE3_DY       =  -4.513
HOLE4_DX       =  -9.544   # 相对 v 键
HOLE4_DY       =  -4.577
HOLE5_DX       =  10.782   # 相对 r 键
HOLE5_DY       =  7.044

# 列错位（以 e/i 列为基准 y=0，正值=偏高）
COL_STAGGER: dict[int, float] = {
    0: -(STAGGER_QW + STAGGER_WE),   # q/a/z 列
    1: -STAGGER_WE,                  # w/s/x 列
    2:  0.0,                         # e/d/c 列（基准）
    3: -STAGGER_ER,                  # r/f/v 列
    4: -(STAGGER_ER + STAGGER_RT),   # t/g/b 列
    5: -(STAGGER_ER + STAGGER_RT),   # y/h/n 列（右手镜像）
    6: -STAGGER_ER,                  # u/j/m 列
    7:  0.0,                         # i/k/, 列
    8: -STAGGER_WE,                  # o/l/. 列
    9: -(STAGGER_QW + STAGGER_WE),   # p/;// 列
}

# QWERTY 3 行（行 0=上行，行 1=主行，行 2=下行）
ROWS: list[list[tuple[int, int, str]]] = [
    [(0,0,'q'),(0,1,'w'),(0,2,'e'),(0,3,'r'),(0,4,'t'),
     (0,5,'y'),(0,6,'u'),(0,7,'i'),(0,8,'o'),(0,9,'p')],
    [(1,0,'a'),(1,1,'s'),(1,2,'d'),(1,3,'f'),(1,4,'g'),
     (1,5,'h'),(1,6,'j'),(1,7,'k'),(1,8,'l'),(1,9,';')],
    [(2,0,'z'),(2,1,'x'),(2,2,'c'),(2,3,'v'),(2,4,'b'),
     (2,5,'n'),(2,6,'m'),(2,7,','),(2,8,'.'),(2,9,'/')],
]

# ─── 构建坐标表 ───────────────────────────────────────────────────────────────

KEY_POS: dict[str, tuple[float, float]] = {}

# 普通键
for row_keys in ROWS:
    for (row, col, key) in row_keys:
        KEY_POS[key] = (col * KEY_SPACING,
                        COL_STAGGER[col] - row * KEY_SPACING)

# 拇指键坐标基于 b 键 + 实测偏移量
_bx, _by = 4 * KEY_SPACING, COL_STAGGER[4] - 2 * KEY_SPACING  # b 键坐标
THUMB_KEYS: dict[str, tuple[float, float]] = {
    'LT1': (_bx + THUMB1_DX, _by + THUMB1_DY),
    'LT2': (_bx + THUMB2_DX, _by + THUMB2_DY),
}
KEY_POS.update(THUMB_KEYS)

# 打孔圆心坐标
_wx, _wy = KEY_POS['w']
_zx, _zy = KEY_POS['z']
_ex, _ey = KEY_POS['e']
_vx, _vy = KEY_POS['v']
_rx, _ry = KEY_POS['r']
HOLE_POS: dict[str, tuple[float, float]] = {
    'H1': (_wx + HOLE1_DX, _wy + HOLE1_DY),
    'H2': (_zx + HOLE2_DX, _zy + HOLE2_DY),
    'H3': (_ex + HOLE3_DX, _ey + HOLE3_DY),
    'H4': (_vx + HOLE4_DX, _vy + HOLE4_DY),
    'H5': (_rx + HOLE5_DX, _ry + HOLE5_DY),
}

# ─── 打印全部键位 + 到参考点的距离 ────────────────────────────────────────────

def print_all(ref_x: float, ref_y: float) -> None:
    print(f"\n参考点: ({ref_x:.3f}, {ref_y:.3f}) mm\n")
    print(f"  {'键':<5} {'绝对x':>7}  {'绝对y':>7}  {'Δx':>7}  {'Δy':>7}  {'距离':>8}")
    print("  " + "─" * 50)

    # 左手全部（上→主→下→拇指）
    layout_order = (
        ['q','w','e','r','t'] +
        ['a','s','d','f','g'] +
        ['z','x','c','v','b'] +
        ['LT1','LT2']
    )

    for key in layout_order:
        x, y = KEY_POS[key]
        dx, dy = x - ref_x, y - ref_y
        dist = math.hypot(dx, dy)
        print(f"  {key:<5} {x:>7.3f}  {y:>7.3f}  {dx:>7.3f}  {dy:>7.3f}  {dist:>8.3f}")

    print()
    print(f"  {'孔':<5} {'绝对x':>7}  {'绝对y':>7}  {'Δx':>7}  {'Δy':>7}  {'距离':>8}")
    print("  " + "─" * 50)
    for key in ['H1', 'H2', 'H3', 'H4', 'H5']:
        x, y = HOLE_POS[key]
        dx, dy = x - ref_x, y - ref_y
        dist = math.hypot(dx, dy)
        print(f"  {key:<5} {x:>7.3f}  {y:>7.3f}  {dx:>7.3f}  {dy:>7.3f}  {dist:>8.3f}")
    print()


def print_spatial_map() -> None:
    """打印键盘空间布局图（左手 → 右手），每个键显示名称和 (x, y) 坐标。"""
    CELL_W = 14  # 单元格内容宽度

    def _pos(k: str) -> tuple[float, float]:
        return KEY_POS.get(k) or HOLE_POS[k]

    def _print_key_row(keys: list[str], col_offset: int) -> None:
        pad = " " * (col_offset * (CELL_W + 2))
        border = pad + " ".join("┌" + "─" * CELL_W + "┐" for _ in keys)
        names  = pad + " ".join("│" + k.center(CELL_W) + "│" for k in keys)
        coords = pad + " ".join(
            "│" + f"{_pos(k)[0]:.3f}, {_pos(k)[1]:.3f}".center(CELL_W) + "│"
            for k in keys)
        bottom = pad + " ".join("└" + "─" * CELL_W + "┘" for _ in keys)
        print(border)
        print(names)
        print(coords)
        print(bottom)

    def _print_hand(title: str,
                    rows: list[list[str]],
                    thumb: list[str],
                    thumb_col_offset: int) -> None:
        print(f"\n{'═' * 3} {title} {'═' * 3}\n")
        for row_keys in rows:
            _print_key_row(row_keys, 0)
        if thumb:
            _print_key_row(thumb, thumb_col_offset)
        print()

    _print_hand("左手 (Left)",
                [['q','w','e','r','t'],
                 ['a','s','d','f','g'],
                 ['z','x','c','v','b']],
                ['LT1','LT2'], thumb_col_offset=3)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="打印所有键位坐标及到 e 键的距离")
    parser.add_argument("x", nargs="?", type=float, default=None,
                        help="e 键的绝对 x 坐标（mm）。省略则用默认布局")
    parser.add_argument("y", nargs="?", type=float, default=None,
                        help="e 键的绝对 y 坐标（mm）")
    args = parser.parse_args()

    # 将整个键盘平移，使 e 键落在指定绝对坐标
    if args.x is not None:
        ex, ey = KEY_POS['e']
        dx, dy = args.x - ex, args.y - ey
        for k in KEY_POS:
            KEY_POS[k] = (KEY_POS[k][0] + dx, KEY_POS[k][1] + dy)
        for k in HOLE_POS:
            HOLE_POS[k] = (HOLE_POS[k][0] + dx, HOLE_POS[k][1] + dy)

    ref_x, ref_y = KEY_POS['e']
    print_all(ref_x, ref_y)
    print_spatial_map()
