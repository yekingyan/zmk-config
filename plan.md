# ZMK Config 计划

## 项目背景

Lily58 上实现"双核驱动"过渡方案，最终目标迁移到 Corne 36 键。

- 详细键位设计文档：[docs/keymap-design.md](docs/keymap-design.md)

## 设计原则

- Callum-style OSM（一次性修饰键），不用 Home Row Mods / Hold-Tap
- 3 拇指核心键（Lily58）→ 目标 2 拇指核心键（Sweep 适配）
- 外围保留冗余常规键（Shift/Ctrl/数字行），作为过渡期安全网
- 对侧控制（Contralateral Control）：左手拇指切层时右手执行功能，反之亦然

## 七层架构

- **Base (0)**：QWERTY + 外围冗余键（数字行/物理 Shift/Ctrl）
- **Nav (1)**：左手 OSM 修饰 + 编辑快捷键，右手 Vim HJKL + 按词跳跃 + 翻页
- **Num (2)**：左手算术运算符，右手纯数字九宫格
- **Sym (3)**：左手高频符号（括号/特殊字符），右手 OSM 修饰 + 副标点
- **Fun (4)**：左手 OSM/BT/Bootloader/K_CANCEL，右手 F 键九宫格（与 Num 对齐）
- **Mouse (5)**：左手鼠标移动/滚轮/剪贴板，右手 OSM + 鼠标点击
- **Media (6)**：左手媒体/音量/亮度，右手 OSM

## 当前阶段：阶段三 - 极客常态期（2026-03-16 起）

- 外围键已恢复，Legacy 层已移除，不再误触
- **当前痛点**：标点符号层（Sym 层）键位记不住，需要反复练习
- 训练目标：Ctrl+S 等组合键全部走 OSM 路径，小拇指彻底解放

## 进行中

- [x] 蓝牙频繁断联问题排查及配置调优（现状：已破案，确认为克隆板时钟漂移）
  - 详见：[ZMK 固件底层调试与断联排查指南](docs/debug-guide.md)
  - **真凶发现**：原因 0x22 (LMP Response Timeout) 是由于 SuperMini 等克隆板缺少外部晶振，刷入官方固件后导致时钟漂移。
  - **终极方案**：强制启用内部 RC 振荡器 (`CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y`)，并撤销之前的临时超时补救措施。
  - **二轮优化（针对克隆板握手崩溃）**：针对 `Err 9 (Security failed)` 拒绝连接问题，将 `CONFIG_BT_CTLR_PHY_2M` 设为 `n`（强制降级 1M PHY），并开启实验性安全配对选项 (`CONFIG_ZMK_BLE_EXPERIMENTAL_SEC=y`)。


## Combo 规划

### 目标

为 Sweep 风格布局（每侧仅 2 拇指键）做准备，将当前依赖第 3 拇指键的功能迁移到 Combo 触发，同时系统化梳理所有 Combo 需求。

### 约束

- 五笔输入法用户，Combo 键位必须避开高频 bigram（数据见 `research/wubi-bigram-analysis.md`）
- 需要 Combo 替代的功能：ESC、Shift（原第 3 拇指键承载）
- 可能还需要 Combo 的功能：Caps Word、输入法切换、待定...

### 现有 Combo

| Combo | 键位 | 功能 | 层 | 状态 |
|-------|------|------|----|------|
| `J+K` | pos 31+32 | ESC | Base | ✅ 保留 |
| `F+J` | pos 28+31 | Caps Word | Base | ✅ 保留 |
| `S+D` | pos 26+27 | LSHFT(单次切换/长按) | Base | ✅ 新增（最优安全位） |
| 左双拇指 | 52+53(L)/51+52(S) | 切 FUN 层 | Base | ✅ 新增（Sweep适配）|
| 右双拇指 | 54+55(L)/55+56(S) | 切 MEDIA 层 | Base | ✅ 新增（Sweep适配）|

### Sweep 拇指区变化

```
Lily58 (3 拇指核心):  [Nav/SPACE] [Num/TAB] [Shift/Media]  ← 右手示例
Sweep  (2 拇指核心):  左侧 [SPACE/NAV] [TAB/NUM]   右侧 [ENTER/SYM] [BSPC/MOU] 
```

**被移除功能的安置方案：**
**被移除功能的安置方案：**
- **Fun 层**：左侧双拇指同按（SPACE + TAB）长按触发 Combo
- **Media 层**：右侧双拇指同按（ENTER + BSPC）长按触发 Combo
- **ESC 单按**：目前主区已有 `J+K` Combo 承载
- **LSHFT(单次/中英切换)**：S+D（左手中指+无名指，基于数据证明的最强安全位）
- **Caps Word**：保留 `F+J`

### 选键数据基础

五笔 Bigram 频率分析已完成（`research/`），top300 零命中的安全组合：
- `sd`（评分 167）、`jk`（166）、`as`（134）、`sf`（132） — 最优候选
- 全键盘共 103 个 top300 零命中组合可选

### 待决事项

- [x] 确定 Sweep 拇指区 2 键各自承载什么功能：左 `SPACE(NAV) | TAB(NUM)`；右 `ENTER(SYM) | BSPC(MOU)`
- [x] 确定需要 Combo 化的完整功能清单：Fun 层、Media 层、ESC、单次 Shift (中英切换)、Caps Word
- [x] 从安全组合池中为单次 Shift 选定最佳按键 `S+D`
- [x] 增加 Sweep 拇指同按Combo (左拇指 `SPACE+TAB`, 右拇指 `ENTER+BSPC`)
- [ ] 评估是否需要跨层 Combo

## 已完成

### 双方案共存配置（2026-03-10）

- [x] 在 `build.yaml` 中增加通过 `cmake-args: -DZMK_CONFIG` 对新配置目录的支持
- [x] 将 `silakka54` 分支原有的键映射文件平移到本分支 `config_silakka54` 文件夹，实现共存构建

## 待办

- [ ] Corne 36 键 keymap 移植

## 已完成

### 上板实测与阶段一毕业（2026-03-05）

- [x] **上板实测**：固件已烧录，实际使用中
- [x] **阶段一毕业**：物理冗余键已完全封印（仅游戏场景使用 Legacy 层），3 拇指分工已适应
- [x] 优化 Mouse 层布局：移除冗余的剪贴板快捷键与 CAPS，贯彻极简首选项
- [x] Mouse 层优化：移除底部无用的 INS 键，纯净操作区
- [x] Mouse 层功能重构：新增撤销/重做与虚拟桌面切换，优化单手浏览流

### 高级功能与局部强化（2026-03-04）

- [x] **Z键长按修饰**：将 Base 层的 Z 键更换为 `&mt LCTRL Z`，补充了 Uro's Timeless 理念中的局部按压特性。
- [x] **Nav 层 Alt-Tab Swapper**：在 Nav 层 Q 位添加了名为 `&swapper` 的宏，实现基于 ZMK 原生宏（macro）的快速窗口切换体验。
- [x] **鼠标层疾/缓模式**：结合 input processors scaler 的特性在文件顶端新增 `zip_snipe` 和 `zip_turbo` 调节器。构建并引用 `M_SNIPE` 和 `M_TURBO` 双层图层，布置在右手侧底层 `N` 与 `M` 位置，允许微操“防手抖”慢移与大跨度瞬移。

### 右外侧拇指键精简与切层优化（2026-03-04）

- [x] **恢复核心区 OSM Shift**：测试确认 `&skq LSHFT` 实际上单点时会向 Windows 完美发送孤立的 Shift 按键，因此撤回之前错误的全局替换操作，恢复左右手中行的 `&skq LSHFT`（OSM），维持 Callum-style 设计的完整性。
- [x] **拇指键采用纯切层修饰 tlt**：利用现有的拇指切层行为，将右外侧拇指键配置为 `&tlt MEDIA LSHFT`。实现单点精准输出 LSHFT（切中英文），长按触发切层 MO（进入 Media 层），彻底解决单按和长按的需求痛点。
- [x] **去除 tlt 的空闲保护**：从 `thumb_layer_tap` 行为中彻底移除 `require-prior-idle-ms` 参数。以防在输入字母后马上长按拇指（因触发 idle 保护导致长按被吃掉）从而意外发送单次敲击的问题。
- [x] **移除废弃组合键**：废弃 `D+F` 切换输入法组合键设计，采用独立的拇指 Shift 替代。

### 鼠标层指针速度优化（2026-03-04）

- [x] **ZMK 鼠标层的指针速度优化**：在 `lily58.keymap` 中覆写 `&mmv` 和 `&msc` 默认属性，并使用正确的 `ZMK_POINTING_DEFAULT_MOVE_VAL` 增加基础移动速度和滚轮速度，解决原生鼠标移动过慢痛点。

### 双核 36 键改造（2026-03-03）

- [x] **Base 层外围全置空**：数字行 + 外侧列全部 `&none`，模拟 Corne 36 键物理约束
- [x] **Legacy 层兜底**：新增 Layer 7 完整 QWERTY（右 SHIFT 位 = `&to BASE`），Fun 层热键切换
- [x] **拇指 Layer-Tap 防误触 (tlt)**：新建 behavior（tap-preferred + require-prior-idle-ms 125ms），替换所有 `&lt`
- [x] **OSM 分离**：`skq`（quick-release）仅保留 Shift，新建 `sk`（无 quick-release）给 Ctrl/Alt/GUI
- [x] **K_CANCEL 后悔药**：Fun 层 Q 位，一键清除误按的 Sticky Key
- [x] **鼠标层点击下放**：右手下行 M/,/. 改为 LCLK/MCLK/RCLK，对侧解耦
- [x] **Sym 层补 `'`**：P 位加入单引号（外侧列屏蔽后的唯一入口）
- [x] **Combo D+F 放宽**：timeout 70ms + require-prior-idle-ms 150ms（防 `default` 等误触）

### 层架构重构（2026-03-02）

- [x] Layer 2 & 3 分隔重排：NUM 层定于左拇指 SPACE 触发，SYM 层移至右拇指 ENTER 触发
- [x] Nav 层收纳优化：解决 C(→) 超格，收纳至 3x5 核心区
- [x] Nav 层 GUI↔BSPC 互换：GUI 移至 R 位，BSPC 降级至 T 位
- [x] Caps Word：Nav 层 G 位独立键 + F+J Combo 双触发

### 初始实现（2026-03-01）

- [x] Callum-style `skq` 行为定义（快速释放 OSM）
- [x] JK Combo = Escape
- [x] Base 层：QWERTY 核心 + 3 拇指分工
- [x] Num 层：右手纯数字九宫格 + 左手算术运算符
- [x] Sym 层：左手符号阵列 + 右手 OSM 修饰
- [x] Fun 层：F 键对齐九宫格 + BT + Bootloader
- [x] GitHub Actions 编译验证通过
