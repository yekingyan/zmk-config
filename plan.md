# ZMK Config 计划

## 项目背景

Lily58 上实现"双核驱动"过渡方案，最终目标迁移到 Corne 36 键。

- 详细键位设计文档：[docs/keymap-design.md](docs/keymap-design.md)

## 设计原则

- Callum-style OSM（一次性修饰键），不用 Home Row Mods / Hold-Tap
- 3 拇指硬约束：4 个多余键 `&none`，强制适应 Corne 手型
- 外围保留冗余常规键（Shift/Ctrl/数字行），作为过渡期安全网

## 四层架构

- **Base**：QWERTY + 外围冗余
- **Nav**：左手 OSM 修饰 + 编辑兜底，右手 Vim HJKL + 按词操作
- **Sym**：左手九宫格数字，右手程序员符号
- **Sys**：F 键（与九宫格对齐）+ 蓝牙 + 媒体 + Bootloader

## 已完成

- [x] Callum-style `skq` 行为定义（快速释放 OSM）
- [x] JK Combo = Escape
- [x] Conditional Layer: NAV + SYM = SYS（Tri-layer）
- [x] Base 层：外围冗余 + 3 拇指 + 4 个 &none
- [x] Sym 层：九宫格数字 + 符号阵列
- [x] Sys 层：F 键对齐九宫格 + BT + 媒体 + Bootloader
- [x] GitHub Actions 编译验证通过

## 进行中

- [x] 拇指层键添加 One-Shot 支持 (Hold = mo, Tap = sl)
- [ ] Nav 层最终布局确认（按词移动/删除、剪贴板、编辑兜底）
- [ ] 合并 `test/callum-osm` → `main`

## 待办

- [ ] 上板实测 + 手感反馈迭代
- [ ] Caps Word 触发方式优化（当前在 Sys 层）
- [ ] 适应期后评估：是否可以开始"封印"外围冗余键
- [ ] Corne 36 键 keymap 移植
