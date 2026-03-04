# ZMK Config 计划

## 项目背景

Lily58 上实现"双核驱动"过渡方案，最终目标迁移到 Corne 36 键。

- 详细键位设计文档：[docs/keymap-design.md](docs/keymap-design.md)

## 设计原则

- Callum-style OSM（一次性修饰键），不用 Home Row Mods / Hold-Tap
- 3 拇指硬约束：4 个多余键 `&none`，强制适应 Corne 手型
- 外围保留冗余常规键（Shift/Ctrl/数字行），作为过渡期安全网
- 对侧控制（Contralateral Control）：左手拇指切层时右手执行功能，反之亦然

## 八层架构

- **Base (0)**：QWERTY + 外围 `&none`（模拟 36 键物理约束）
- **Nav (1)**：左手 OSM 修饰 + 编辑快捷键，右手 Vim HJKL + 按词跳跃 + 翻页
- **Num (2)**：左手算术运算符，右手纯数字九宫格
- **Sym (3)**：左手高频符号（括号/特殊字符），右手 OSM 修饰 + 副标点
- **Fun (4)**：左手 OSM/BT/Bootloader/K_CANCEL，右手 F 键九宫格（与 Num 对齐）
- **Mouse (5)**：左手鼠标移动/滚轮/剪贴板，右手 OSM + 鼠标点击
- **Media (6)**：左手媒体/音量/亮度，右手 OSM
- **Legacy (7)**：完整 QWERTY 兜底层（Fun 层热键 `&to` 切换）

## 进行中

- [ ] 合并 `test/callum-osm` → `main`

## 待办

- [x] 优化 Mouse 层布局：移除冗余的剪贴板快捷键与 CAPS，贯彻极简首选项
- [x] Mouse 层优化：移除底部无用的 INS 键，纯净操作区
- [x] Mouse 层功能重构：新增撤销/重做与虚拟桌面切换，优化单手浏览流
- [ ] 上板实测 + 手感反馈迭代
- [ ] Corne 36 键 keymap 移植

## 已完成

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
