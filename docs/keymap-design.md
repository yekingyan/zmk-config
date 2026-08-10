# 34 / 36 / 58 键位设计体系（跨平台统一架构：ZMK + RMK）

> 本方案是跨硬件阵列、跨固件平台的终极键位设计。同时维护 ZMK（`lily58`, `silakka54`, `cradio`, `dolphin1`, `dolphin36`, `bgkeeb`）和 RMK（`dolphin1`）两套固件实现。设计以两平台**能力交集**为基线，ZMK 独有能力作为可选的增强项（不影响 RMK 核心体验）。
> 
> 当前实现文件：[`config/dolphin1.keymap`](../config/dolphin1.keymap) (ZMK) · [`~/projects/rmk-dolphin/nrf52840_split/keyboard.toml`](../../rmk-dolphin/nrf52840_split/keyboard.toml) (RMK)

### 34 vs 36 vs 58 键：硬件拇指键差异与降维映射

所有分支的 3×5 核心区（字母、符号、功能层）**完全相同**，各键盘之间的**唯一区别在于每侧拇指键的物理数量和布局降维策略**：

- **Dolphin1 / Sweep (34 键)**（每侧 **2 个**拇指键）：
  最极致的妥协，砍掉所有外侧按键。最外侧第3个拇指键功能（左 Esc_FUN，右 LShift_MED）通过本配置底部的“双拇指同时按压 Combo”（或主键区 S+D / J+K）完美兼容。
  ```text
  左拇指：            SPACE(NAV) │ TAB(NUM)
  右拇指：ENTER(SYM) │ BSPC(MOU)
  ```

- **Silakka54 / Corne / Dolphin36 (36 键核心)**（每侧 **3 个**拇指键）：
  黄金标准 `3x5+3` 布局，保留三个核心切层键。
  ```text
  左拇指：ESC(FUN) │ SPACE(NAV) │ TAB(NUM)
  右拇指：ENTER(SYM) │ BSPC(MOU) │ LSHFT(MED)
  ```
  > Dolphin36 / Corne 就是纯粹的 3 拇指；Silakka54 物理上多一颗外侧键，置 `&none` 封印，
  > 因此排布写成 `ESC │ SPACE │ TAB │ none` 与 `none │ ENTER │ BSPC │ LSHFT`。
  > Dolphin36 另外保留双拇指 Combo（左 SPACE+TAB → FUN，右 ENTER+BSPC → MEDIA）作为冗余触发，
  > 与 34 键的肌肉记忆完全兼容。

- **Lily58 (58 键)**（每侧 **4 个**拇指键）：
  在拥有 3 个核心切层键的基础上，利用物理冗余空间提供容错率，整体**右移一位**，外侧放假键 `&none` 以逼迫手指内收。
  ```text
  左拇指：none │ ESC(FUN) │ SPACE(NAV) │ TAB(NUM)
  右拇指：ENTER(SYM) │ BSPC(MOU) │ LSHFT(MED) │ none
  ```

> 非 Base 层中拇指键上的功能绑定（如 Num 层的 `N0`、Mouse 层的鼠标按键）也严格遵循同样的对齐/右移规则。使用这套方案，你可以随意在 34 键、36 键乃至传统的 58 键分体键盘之间无缝切换。

## 社区最佳实践溯源

> 本方案集成了近几年 r/ErgoMechKeyboards 和 ZMK 社区几大流派的精髓。

- **Callum-style OSM 流派**（Callum Oakley）：摒弃 Home Row Mods（HRM，主行长按触发修饰键）。HRM 在快速打字（特别是 Roll 连击）时极易误触（Tapping Term 冲突）。Callum 引入独立层 + Sticky Keys（OSM），实现基础层 0 延迟、0 误触，完美契合 Vim 的"顺序输入"哲学
- **Miryoku 对侧控制 + 3x5+3 黄金法则**（Manna Harbour）：36/34 键配列的绝对真理——按住左手拇指切层，右手执行功能；反之亦然。本配置的 Numpad、Nav 等层完全继承此理念
- **"双核驱动"渐进式降级**（分体键盘社区常见建议）：在 58 键上保留物理冗余作为安全网，核心区通过代码强制塑形（如置空 4 个拇指键），是克服大脑抗拒并最终过渡到 34 键 Dolphin 的最高效手段
- **ZMK Caps Word**（ZMK 官方 Behaviors，借鉴自 QMK）：彻底淘汰 Caps Lock，通过 Combo 触发，遇到空格自动解除，专为 `SNAKE_CASE` 设计。`continue-list = <UNDERSCORE MINUS>` 确保连字符也不会中断大写

## 设计哲学："双核驱动"过渡方案

从 104/87 键直接跳到 36 键认知陡坡太大。"双核驱动"化解了这个问题：

1. **物理冗余核（兜底）**：保留数字行、物理 Esc/Tab/Shift/Ctrl/-/'，打游戏、单手操作、大脑疲劳时提供 100% 传统肌肉记忆支持
2. **极客逻辑核（Callum-style OSM）**：核心区 3x5 隐藏了基于分层和 OSM 的终极代码输入方案
3. **3 拇指核心键**：拇指区域保留核心 Layer-Tap 功能键，外围拇指键放置 CTRL / MINUS / EQUAL 等辅助键

### 哲学与约束

- Tap（短按）输出核心控制字符，Hold（长按）作为切层离合
  - 左手拇指（从外到内）：CTRL, Esc(长按 function 层), Space(长按 nav 层), Tab(长按 num 层)
  - 右手拇指（从内到外）：Enter(长按 sym 层), Backspace(长按 mouse 层), L-SHIFT(长按 Media 层，单发切输入法), CTRL

- 核心逻辑：对侧控制（主要原则）。
  - 按住左手拇指
    - 左手中行变成控制区：GUI(A), ALT(S), CTRL(D), SHIFT(F)
    - 右手变成功能区（如导航、数字）
    - 注：左手上/下行可放置辅助功能键（如 Nav 层的编辑键、剪贴板操作）
  - 按住右手拇指
    - 右手中行变成控制区：SHIFT(J), CTRL(K), ALT(L), GUI(;)
    - 左手变成功能区



## 层总览

| 层号 | 名称 | 激活方式 | 功能手 | 控制手 |
|------|------|---------|-------|-------|
| 0 | Base | 默认层 | 双手 | — |
| 1 | Nav & Mods | 左拇指 TAB 长按 | 右手 | 左手 |
| 2 | Numpad | 左拇指 SPACE 长按 | 右手 | 左手 |
| 3 | Symbols | 右拇指 ENTER 长按 | 左手 | 右手 |
| 4 | Function | 左拇指 ESC 长按 | 右手 | 左手 |
| 5 | Mouse | 右拇指 BSPC 长按 | 左手 | 右手 |
| 6 | Media | 右拇指 LSHFT 长按 | 左手 | 右手 |

## 键位布局总览

### Layer 0: Base（QWERTY + 外围冗余键）

```
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│  `  │  1  │  2  │  3  │  4  │  5  │               │  6  │  7  │  8  │  9  │  0  │  ~  │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│ TAB │  Q  │  W  │  E  │  R  │  T  │               │  Y  │  U  │  I  │  O  │  P  │  -  │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│LSHFT│  A  │  S  │  D  │  F  │  G  │               │  H  │  J  │  K  │  L  │  ;  │  '  │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│CTRL │  Z  │  X  │  C  │  V  │  B  │  -  │   │  =  │  N  │  M  │  ,  │  .  │  /  │RSHFT│
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │CTRL │ ESC │SPACE│ TAB │   │ENTER│BSPC │LSHFT│CTRL │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- **外围冗余键位**：数字行 + 外侧列 + 拇指外侧键保留完整的传统键位，方便过渡期和游戏场景
- 核心 3x5 区域和 3 拇指 Layer-Tap 键保持 Callum-style 设计不变

### Layer 1: Nav & Mods（左拇指按住 NAV 激活）

```
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│none │none │none │none │none │none │               │none │none │none │none │none │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │SWAPP│S-TAB│none │L-SHIFT│none │             │C(←) │ C-D │ C-U │C(→) │ DEL │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │ GUI │ ALT │CTRL │LSHFT│CAPW │               │  ←  │  ↓  │  ↑  │  →  │ C(DEL)│none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │C(Z) │C(X) │C(C) │C(V) │     │none │   │none │HOME│PgDn│ PgUp│ END │ C(BS)│none │
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │     │▓▓▓▓▓│     │   │     │     │     │none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- **左手上行**（编辑快捷区）：`SWAPP | S-TAB | L-SHIFT`
  - `SWAPP`（`&swapper` 宏）：位于原 `Q` 键位，轻点切换应用（同 Alt-Tab），按住不放可保留 Alt 状态并通过连续轻点快速遍历窗口。
  - `L-SHIFT`（`&kp LSHFT`）：**普通 hold 型 Shift**，按住不放配合右手方向键，实现 Shift+方向键连续选中文本
  - 与中行的 `&skq LSHFT`（OSM 点击型）**用途不同**：上行适合连续选中，中行适合单次大写或单次 Shift 组合
  - `RET` 和 `BSPC` 已移除（冗余：Nav 层右拇指键已对侧解耦为纯 `&kp RET` / `&kp BSPC`，可直接长按连发）
- **左手中行**（OSM 修饰键 + Caps Word）：`GUI | ALT | CTRL | SHIFT | CAPW`
- **左手下行**（剪贴板区）：`C(Z) | C(X) | C(C) | C(V)`，与 Base 层位置一致，零记忆成本
- **右手上行**（跳跃线）：`C(←) | C-D | C-U | C(→) | DEL`，按词跳跃 + Vim 半页翻页
- **右手中行**（方向键）：`← | ↓ | ↑ | → | C(DEL)`，HJKL 映射
- **右手下行**（行级导航）：`HOME | PgDn | PgUp | END | C(BS)`，行首行尾 + 整页翻页

### Layer 2: Numpad（左拇指 SPACE 长按激活）

```text
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│none │none │none │none │none │none │               │none │none │none │none │none │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │     │     │     │     │               │  .  │  7  │  8  │  9  │  -  │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │ GUI │ ALT │CTRL │LSHFT│BSPC │               │     │  4  │  5  │  6  │  +  │none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │  /  │  *  │  =  │     │none │   │none │   │  1  │  2  │  3  │     │none │
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │     │     │▓▓▓▓▓│   │     │  0  │     │none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- 左手 = 算术运算符（避免污染纯数字的右手），中行 G 位放置 BSPC 方便数字输入纠错。
- 右手 = 纯数字九宫格（含小数点）：`.`7 89 (UIO 前), 456 (JKL), 123 (M,.)；`.` 紧靠 `7` 左侧，符合九宫格使用直觉。
- 逻辑：完美的“对侧控制”，左手拇指按住，右手主行飞速盲打数字，手感绝佳。

### Layer 3: Symbols（右拇指 ENTER 长按激活）

```text
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│none │none │none │none │none │none │               │none │none │none │none │none │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │  !  │  @  │  #  │  $  │  %  │               │  ^  │  &  │  *  │  =  │  '  │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │  (  │  {  │  [  │  <  │  _  │               │  |  │LSHFT│CTRL │ ALT │ GUI │none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │  )  │  }  │  ]  │  >  │  `  │none │   │none │ \ │  ~  │  :  │  "  │  ?  │none │
└─────┴─────┴─────┼─────┼─────┴─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │     │     │     │   │▓▓▓▓▓│     │     │none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- 左手 = 核心符号区（按功能分行）：
  - 上行 `! @ # $ %`：Shift+1~5 的符号，严格对应数字行位置，零记忆成本
  - 中行 `( { [ <` + `_`：四种左括号从外到内排列，右列为高频 `_`（snake_case 核心键，食指内侧主行黄金位）
  - 下行 `) } ] >` + `` ` ``：四种右括号与上方左括号垂直配对，右列补 `` ` ``
  - 右手拇指长按 ENTER 激活，左手在核心区飞速输出一切符号
- 右手 = 控制区与副标点：
  - 上行 `^ & *` + `=` + `'`：`^ & *` 与数字行 `6 7 8` 严格对齐；`=` 填入空位（赋值/比较高频，避免跨层到 Num）；`'` 为单引号唯一入口
  - 主行 `|` + 修饰键 `LSHFT | CTRL | ALT | GUI`：管道符放 home row 食指内侧，高频易触；修饰键与 Nav 层左手 OSM 呈完美镜像
  - 下行 `\ ~ : " ?`：`\` 与上方 `|` 垂直配对（斜杠家族）；`~` 低频降级自左手主行


### Layer 4: Function（左拇指 ESC 长按激活）

```text
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│none │none │none │none │none │none │               │none │none │none │none │none │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │CANCL│ BLE │ USB │     │BTCLR│               │     │ F7  │ F8  │ F9  │ F12 │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │ GUI │ ALT │CTRL │LSHFT│     │               │     │ F4  │ F5  │ F6  │ F11 │none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │ BT0 │ BT1 │ BT2 │ BT3 │     │none │   │none │     │ F1  │ F2  │ F3  │ F10 │none │
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │▓▓▓▓▓│     │     │   │     │     │     │none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- 左手 = 系统工具 + OSM 修饰键 + 蓝牙操作：
  - 上行 `BTCLR`：蓝牙绑定清除
  - 中行 `GUI | ALT | CTRL | LSHFT`（与 Nav/Num 层一致）
  - 下行 `BT0 | BT1 | BT2 | BT3`（蓝牙通道选择）
- 右手 = F 键九宫格（与 Num 层数字严格对齐）：
  - F7/F8/F9 = 7/8/9 位，F4/F5/F6 = 4/5/6 位，F1/F2/F3 = 1/2/3 位
  - F10/F11/F12 补在右列（与 Num 层的 `-` `+` 同位置）

### Layer 5: Mouse（右拇指 BSPC 长按激活）

```text
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│none │none │none │none │none │none │               │none │none │none │none │none │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │UNDO │REDO │VD_L │VD_R │     │               │     │     │     │     │     │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │ ML  │ MU  │ MD  │ MR  │               │     │LSHFT│CTRL │ ALT │ GUI │none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │WH_L │WH_U │WH_D │WH_R │none │   │none │SNIPE│TURBO│     │     │     │none │
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │MCLK │RCLK │LCLK │   │     │▓▓▓▓▓│     │none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- 左手 = 鼠标移动 + 滚轮 + 鼠标按键（右拇指激活，左手主导操作）：
  - 上行 `UNDO | REDO | VD_L | VD_R`（撤销，重做，向左/右切换虚拟桌面）
  - 中行 `ML | MU | MD | MR`（纯鼠标移动）
  - 下行 `WH_L | WH_U | WH_D | WH_R`（四方向滚轮）
  - 拇指键 `MCLK | RCLK | LCLK`（舒适度优先：Space自然位为左键，向外依次为右键、中键）
- 右手 = OSM 修饰键（对侧解耦）与疾缓图层离合：
  - 中行 `LSHFT | CTRL | ALT | GUI`（OSM 修饰键）
  - 下行 `SNIPE | TURBO`：分别为1/4减速模式（微调狙击）与双倍加速模式（疾风穿梭）。采用离合键（`&mo`）激活影子层实现。

### Layer 6: Media（右拇指 DEL 长按激活）

```text
┌─────┬─────┬─────┬─────┬─────┬─────┐               ┌─────┬─────┬─────┬─────┬─────┬─────┐
│BOOT │none │none │none │none │none │               │none │none │none │none │none │BOOT │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │     │     │     │     │               │     │     │     │     │     │none │
├─────┼─────┼─────┼─────┼─────┼─────┤               ├─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │PREV │VOL_D│VOL_U│NEXT │               │     │LSHFT│CTRL │ ALT │ GUI │none │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┐   ┌─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│none │     │MUTE │BRI_D│BRI_U│PLAY │none │   │none │     │     │     │     │     │none │
└─────┴─────┴─────┼─────┼─────┼─────┼─────┤   ├─────┼─────┼─────┼─────┴─────┴─────┴─────┘
                  │none │     │     │     │   │     │     │▓▓▓▓▓│none │
                  └─────┴─────┴─────┴─────┘   └─────┴─────┴─────┴─────┘
```

- **左上/右上角 = `&bootloader`**（进入 UF2 刷机模式）：
  - 源端生效（source-specific）：按哪半边的键，就那半边进入 bootloader
  - 放在 Media 层角落防误触，需要刷固件时激活 Media 层后按对应侧角键即可
- 左手 = 媒体 + 音量 + 亮度（右拇指激活，左手为功能区）：
  - 中行 `PREV | VOL_D | VOL_U | NEXT`（媒体控制 + 音量调节）
  - 下行 `MUTE | BRI_D | BRI_U | PLAY`（静音 + 亮度 + 播放/暂停）
- 右手 = OSM 修饰键（与 Sym 层一致）：
  - 中行 `LSHFT | CTRL | ALT | GUI`


## 跨平台兼容性设计

> 键位设计以 ZMK 和 RMK 的**能力交集**为基线，确保核心体验两个平台一致。
> ZMK 独有能力作为**可选增强项**，不影响 RMK 用户正常使用。

### 平台能力对照

| 能力 | ZMK | RMK | 兼容策略 |
|------|-----|-----|---------|
| Layer-Tap | `&tlt` balanced | `LT(layer,key)` + flow_tap | 等价，参数独立调优 |
| OSM 修饰键 | `skq` (quick-release) / `skn` (chain) | `OSM(mod)` 统一行为，chain 模式（下一个键 RELEASE 时释放） | 核心行为一致；quick-release 仅 Shift 用，RMK 缺此机制但实践中差异小。如需可 patch `update_osm` |
| Combo | per-combo `require-prior-idle-ms` 冷却 | 全局 `require_prior_idle_ms` 冷却窗口（patch） | 行为等价，RMK 为全局配置（非 per-combo） |
| Caps Word | `&caps_word` + `continue-list` | `CapsWordToggle`（无 continue-list 配置） | continue-list 是 ZMK 增强 |
| 鼠标移动 | `&mmv` + 加速曲线 | `Mouse*` + `MouseKeyConfig` 加速参数 | 两平台均有加速，参数独立调优 |
| 鼠标滚轮 | `&msc` + 加速曲线 | `MouseWheel*` + `MouseKeyConfig` 加速参数 | 同上 |
| Snipe / Turbo | 影子层 + 自定义速度宏 | **不支持**（无鼠标速度分级） | ZMK 独占 |
| K_CANCEL | 支持（已从 keymap 移除） | **不支持** | 已移除；RMK Fun 层 Q 位用 `ClearEeprom` |
| 长按连发 | `&kp` 对侧解耦后自动连发 | 同机制，`Enter`/`Backspace` 等覆写为裸键码 | 完全等价 |
| BLE 控制 | `BT0-3`, `BT_CLR`, `BT_PRV` 等 | `User0-8`（按公式映射） | 键位相同，底层映射不同 |

### 设计约束（平台兼容）

| 编号 | 约束 | 原因 |
|------|------|------|
| XPLAT-01 | 核心层键位两平台行为一致 | 切换固件零适应成本 |
| XPLAT-02 | Combo 冷却两平台均已支持 | RMK 通过 patch 实现全局 `require_prior_idle_ms` |
| XPLAT-03 | ZMK 增强项不依赖，RMK 用户不受影响 | Snipe/Turbo、鼠标加速等属于锦上添花 |
| XPLAT-04 | 对侧解耦键位两平台完全对齐 | 确保长按连发体验一致 |


## 固件实现要点

### `&trans` / `_` 透传机制

非 Base 层中，**仅拇指键**使用透传符号（ZMK: `&trans`, RMK: `_`），确保跨层切换和基本功能键（Enter/Backspace/Space/Tab）可用。其余未分配功能的字母区位置统一使用屏蔽符号（ZMK: `&none`），防止误触时打出意外字符。

### OSM 行为（Sticky Key）

> **ZMK**：区分 `skq`（quick-release，下一个键按下时释放）和 `skn`（chain，下一个键松开时释放）两种行为。
> **RMK**：统一 `OSM(mod)`，当前**只支持 chain 模式**（下一个键 RELEASE 时释放 OSM），无 `quick-release` 概念。全局超时 `timeout = “1s”` 防止 OSM 卡住。
>
> quick-release 的核心区别：按下 Shift → 按 a → Shift 在 a 按下的瞬间释放。如果按住 a 不放，连发的是小写 `aaaa...`。RMK 的 chain 模式则是 Shift 在 a 松开时才释放，按住 a 连发的是大写 `AAAA...`。实际使用中差异很小。
>
> 如需让 RMK 支持 quick-release，只需将 `oneshot.rs` 中 `update_osm` 的 `!event.pressed` 改为 `event.pressed`。
>
> **【特别注意】关于中英文切换与 LSHFT 的硬性绑定**：
> 在 Windows 环境（如微信输入法、微软拼音等）下，中英文切换的钩子往往只识别 **左 Shift (`LSHFT`)**。因此在本配置中，即使是在属于”右手操作区”的拇指键或镜像层（如 Sym/Mouse 层的右侧修饰区域），涉及单次 Shift 触发的地方均使用了 `LSHFT` 而不是 `RSHFT`，彻底拔除输入法无法识别中文切换钩子的隐患。

```dts
// ZMK: behaviors 定义
behaviors {
    // 快速释放型 OSM（仅用于 Shift）
    skq: sticky_key_quick_release {
        compatible = “zmk,behavior-sticky-key”;
        label = “STICKY_KEY_QUICK_RELEASE”;
        #binding-cells = <1>;
        bindings = <&kp>;
        release-after-ms = <1000>;
        quick-release;              // Shift 专用：按下一个键后立刻释放
        ignore-modifiers;
    };

    // 普通 OSM（用于 Ctrl/Alt/GUI，支持链式组合）
    skn: sticky_key_normal {
        compatible = “zmk,behavior-sticky-key”;
        label = “STICKY_KEY_NORMAL”;
        #binding-cells = <1>;
        bindings = <&kp>;
        release-after-ms = <1000>;
        // 不带 quick-release，允许从容按出链式组合键
        ignore-modifiers;
    };
};
```

```toml
# RMK: keyboard.toml 对应配置
[behavior.one_shot]
timeout = “1s”
# 使用: OSM(LShift), OSM(LCtrl), OSM(LAlt), OSM(LGui)
# 无 quick-release 区分，所有 OSM 行为统一
```

### 拇指 Layer-Tap

> **ZMK**：`&tlt` 替代默认 `&lt`，使用 `balanced` 风味。`balanced`：按住拇指后对侧手有任何按键动作即判定为 Hold（切层），比 `tap-preferred` 响应更快、更符合跨手切层意图。**⚠️ 必须移除 `require-prior-idle-ms`**：由于我们在右外侧拇指使用了 `&tlt MEDIA LSHFT`（长按切层/单击 Shift 切输入法），若加上 idle 保护延迟，在快速敲击字母后立刻按下拇指准备切层时，ZMK 会将长按状态”没收”并强制输出点击，导致意外输出 Shift 把输入法切断！
> **RMK**：`LT(layer,key)` + `[behavior.morse]` flow_tap 机制。`hold_on_other_press = true` 等同于 ZMK 的 balanced 逻辑。

```dts
// ZMK
behaviors {
    tlt: thumb_layer_tap {
        compatible = “zmk,behavior-hold-tap”;
        label = “THUMB_LAYER_TAP”;
        #binding-cells = <2>;
        flavor = “balanced”;
        tapping-term-ms = <200>;
        quick-tap-ms = <150>;              // 短时间内再次按下自动走 Tap
        bindings = <&mo>, <&kp>;
    };
};
```

```toml
# RMK
[behavior.morse]
enable_flow_tap = true
prior_idle_time = “180ms”
hold_on_other_press = true
hold_timeout = “200ms”
gap_timeout = “150ms”
```

### 拇指对侧解耦与长按续发 (Hold-to-Repeat)

> **痛点**：对于设置了 `Layer-Tap`（如 `&tlt MOUSE BSPC` / `LT(4,Backspace)`）的拇指键，如果想要连续删除文字，必须”双击并长按”才能触发自带的连发（Auto-Repeat）机制，这在日常使用中不够顺手。

**解决方案：对侧切层解耦**。在各个功能层（如 Nav、Num、Sym、Fun 层）中，我们不再保留另一侧拇指键的透传符号（ZMK: `&trans`, RMK: `_`），而是**显式地将其替换为对应的普通按键**（ZMK: `&kp XXX`, RMK: 裸键码）。
例如，在按住左手拇指进入 `Nav` 层时，原本在 Base 层的右拇指 `BSPC` (ZMK) / `Backspace` (RMK) 会由透传被覆写为纯粹的按键。
这样一来，**按住左拇指（切层）的同时，按住右拇指就可以直接触发系统级别的长按续发（连续删除）**，极大提升了退格、空格、回车等高频按键的长按连发体验！此方案不影响 Num 层中原本已经是 `&kp N0` / `Kc0` 的正常连发功能。

> 两平台实现完全等价，仅符号不同。

### K_CANCEL 后悔药（已移除）

~~在 Function 层 Q 位（ZMK: `&kp K_CANCEL`），一键清除误按的 Sticky Key 状态。~~ 已从所有 keymap 移除——OSM 修饰键超时（1s）后自动释放，实际影响有限。RMK Fun 层 Q 位为 `ClearEeprom`。

### Combo 系统

> **ZMK**：per-combo `key-positions` + `require-prior-idle-ms` 冷却窗口（150-200ms），在该窗口内按键不会触发 Combo，有效防止快速打字时的误触。
> **RMK**：无 per-combo 冷却机制，仅全局 `timeout = “50ms”`。因此 RMK 下 Combo 更敏感，**选键必须保守**。

#### S + D = Escape

同时按下 `S` 和 `D` 触发 `Escape`。此组合键利用五笔高频数据分析得出（Top300 零命中），占据着绝对的安全区，退出 Insert 模式变成潜意识动作。

```dts
// ZMK: key-positions <26 27>（Lily58 矩阵）
s_d_esc: s_d_esc {
    timeout-ms = <50>;
    require-prior-idle-ms = <200>;
    key-positions = <26 27>;
    bindings = <&kp ESC>;
};
```

```toml
# RMK
{ actions = [“S”, “D”], output = “Escape”, layer = 0 }
```

#### J + K = LSHFT

同时按下 `J` 和 `K` 触发 `LSHFT`，既可以用作快速切换中英文输入法的单点按键，也可通过长按来作为普通的 Shift 使用，彻底解放左手小指。

```dts
// ZMK: key-positions <31 32>（Lily58 矩阵）
j_k_lsft: j_k_lsft {
    timeout-ms = <50>;
    require-prior-idle-ms = <150>;
    key-positions = <31 32>;
    bindings = <&kp LSHFT>;
};
```

```toml
# RMK
{ actions = [“J”, “K”], output = “LShift”, layer = 0 }
```

#### 双拇指 Combo (34键适配)

为彻底适应 34 键只有 2 个拇指键的极简配列，将原本在 36 键体系里位于”第三个拇指键”的外侧功能，完美收容到内侧两个拇指键的 Combo 触发中：
- **左手（SPACE + TAB）同按**：仅触发 `Fun` 层切换（因 `ESC` 单按已由 `S+D` Combo 完美承载）
- **右手（ENTER + BSPC）同按**：仅触发 `Media` 层切换（因 `LSHFT` 单按已由 `J+K` Combo 完美承载）

```dts
// ZMK
left_combo: left_combo {
    timeout-ms = <50>;
    require-prior-idle-ms = <150>;
    key-positions = <52 53>;
    bindings = <&mo FUN>;
};
right_combo: right_combo {
    timeout-ms = <50>;
    require-prior-idle-ms = <150>;
    key-positions = <54 55>;
    bindings = <&mo MEDIA>;
};
```

```toml
# RMK: 使用 LT 键名而非矩阵位置
{ actions = [“LT(1,Space)”, “LT(2,Tab)”], output = “MO(5)” }
{ actions = [“LT(3,Enter)”, “LT(4,Backspace)”], output = “MO(6)” }
```

### Caps Word（F + J Combo / Nav 层左手原 G 键位）

两种触发方式：
- **F + J 同时按**（Combo）：双手食指归位键（Home Row），Base 层直接触发，最快捷
- **Nav 层食指内侧（左手原 G 键位处）**：按住左手拇指（系统 Nav 层）后，用左手食指点击内侧按键触发。

激活后输入的字母自动大写，遇到非字母/数字/下划线时自动取消。非常适合输入 `CONST_VALUE`、`MY_VARIABLE` 等蛇形命名。

ZMK 额外配置了 `continue-list = <UNDERSCORE MINUS>`，连字符 `-` 也不会中断大写，支持 `MY-CONST` 风格命名。
> **RMK** 使用 `CapsWordToggle`，目前无 `continue-list` 等效配置。

### 鼠标层指针速度

两平台均有加速能力，参数独立调优。

**ZMK**：通过 `&mmv` / `&msc` 覆写 `acceleration-exponent`、`time-to-max-speed-ms` 实现。

```dts
#define ZMK_POINTING_DEFAULT_MOVE_VAL 1500
#define ZMK_POINTING_DEFAULT_SCRL_VAL 20
#include <dt-bindings/zmk/pointing.h>

&mmv {
    acceleration-exponent = <1>;
    time-to-max-speed-ms = <500>;
    delay-ms = <0>;
};
```

**RMK**：通过 `MouseKeyConfig` 控制加速（默认 `repeat_interval_ms = 20ms`, `move_delta = 5`, `max_speed = 3x`, `ticks_to_max = 50`）。

```toml
# RMK 鼠标键加速参数（默认值，可在 keyboard.toml 中覆写部分）
# initial_delay_ms = 100      # 按下后首次移动延迟
# repeat_interval_ms = 20     # 连续移动间隔
# move_delta = 5              # 每步像素
# max_speed = 3               # 最大速度倍率
# ticks_to_max = 50           # 达到最大速度的步数
```

### 瞬时速度降维/升维：Snipe & Turbo（ZMK 独占）

为满足细致微操（如 IDE 内代码断点或设计软件里的像素推拉）的需求，右手手指按住离合键触发"影子图层"（Shadow layers），让指针以 1/4 慢速（Snipe）或 2倍 高速（Turbo）位移。

> **实现原理**：利用 ZMK `pointing.h` 中的 `MOVE_X()`/`MOVE_Y()` 宏定义不同速度值，在影子层中直接绑定到 `&mmv`，覆写 Mouse 层的移动键位。

> **RMK 不支持**：无鼠标速度分级能力，Mouse 层移动速度固定。Snipe/Turbo 可视为 ZMK 的增强功能，不影响 RMK 日常使用。

### ZMK Studio（ZMK 独占）

为了方便随时调整键位配置，ZMK 开启了 ZMK Studio 支持并关闭了 PIN 码验证：

- `CONFIG_ZMK_STUDIO=y` — 允许浏览器中实时调键，无需重新编译
- `CONFIG_ZMK_STUDIO_LOCKING=n` — 免 PIN 码解锁
- 关闭 `CONFIG_ZMK_BLE_PASSKEY_ENTRY=y` — 蓝牙配对无需盲打 6 位 PIN 码

> **RMK** 不支持 ZMK Studio。RMK 改键需直接编辑 `keyboard.toml` 重新编译。

## 进化路线图

### 阶段一：安全感过渡期（第 1-2 周）
- 打字时可依赖物理 Shift/Ctrl 和数字行
- 训练目标：适应 3 拇指分工，永远不按 4 个置空键
- 尝试遇到数字时用左拇指 SPACE(NUM) + 右手九宫格

### 阶段二：Callum 觉醒期（第 3-4 周）
- 主动"封印"物理冗余键
- 遇到 Ctrl+S 不再用小拇指，改用"按住左拇指 → 点 D(Ctrl) → 松拇指 → 点 S"
- 体验变化：小拇指前所未有的轻松

### 阶段三：化蛹成蝶（第 2 个月后）
- 连续几天没碰过外围一圈（数字/Shift/Ctrl/Esc）时，已具备驾驭 36 键 Corne 的全部肌肉记忆
- 随时可换 Corne

## 附录：设计历史

### 拇指键 One-Shot Layer 方案（已废弃）

> 此方案已废弃，当前拇指键采用纯 Tap-Hold 设计（Tap 输出字符，Hold 切层 MO）。

曾考虑在拇指层键上采用 `Hold = MO, Tap = One-Shot (SL)` 的混合设计：

- **按住 (Hold)**: 持续切换到目标层（如连续输入多个数字/符号）
- **轻点 (Tap)**: One-Shot 激活目标层，按下下一个键后自动退出（适用于单次符号输入）

**废弃原因**：最终选择更简洁的纯 Tap-Hold 方案，降低认知负担。
