# ZMK Config 计划

## 项目背景

Lily58 上实现"双核驱动"过渡方案，最终目标迁移到 Corne 36 键。

- 详细键位设计文档：[docs/keymap-design.md](docs/keymap-design.md)

## 设计原则

- Callum-style OSM（一次性修饰键），不用 Home Row Mods / Hold-Tap
- 3 拇指硬约束：4 个多余键 `&none`，强制适应 Corne 手型
- 外围保留冗余常规键（Shift/Ctrl/数字行），作为过渡期安全网

## 七层架构

- **Base**：QWERTY + 外围冗余
- **Nav**：左手 OSM 修饰 + 编辑兜底，右手 Vim HJKL + 按词操作
- **Num**：左手算术运算符，右手纯数字九宫格
- **Sym**：左手高频符号（括号/特殊字符），右手 OSM 修饰 + 副标点
- **Fun**：左手 OSM/BT/Bootloader，右手 F 键九宫格（与 Num 对齐）
- **Mouse**：左手鼠标移动/滚轮/点击，右手 OSM
- **Media**：左手媒体/音量/亮度，右手 OSM

## 已完成

- [x] Callum-style `skq` 行为定义（快速释放 OSM）
- [x] JK Combo = Escape
- [x] Conditional Layer: NAV + SYM = SYS（Tri-layer）
- [x] Base 层：外围冗余 + 3 拇指 + 4 个 &none
- [x] Sym 层：九宫格数字 + 符号阵列
- [x] Sys 层：F 键对齐九宫格 + BT + 媒体 + Bootloader
- [x] GitHub Actions 编译验证通过

## 进行中

- [x] 拇指层键添加 One-Shot 支持 (Hold = mo, Tap = sl)（已废弃，改用纯 Tap-Hold）
- [x] Layer 2 & 3 分隔重排：NUM 层定于左拇指 SPACE 触发，SYM 层移至右拇指 ENTER 触发
- [x] Nav 层收纳优化：解决 C(→) 超格，收纳至 3x5 核心区
- [x] Nav 层 GUI↔BSPC 互换：GUI 移至 R 位（食指本列），BSPC 降级至 T 位（拇指已有）
- [x] Caps Word：Nav 层 G 位独立键（不依赖外围键，兼容 Corne 迁移）
- [ ] 合并 `test/callum-osm` → `main`

## 待办

- [ ] 上板实测 + 手感反馈迭代
- [ ] 适应期后评估：是否可以开始"封印"外围冗余键
- [ ] Corne 36 键 keymap 移植
