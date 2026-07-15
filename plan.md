# ZMK Config 计划

> `plan.md` 是项目的**驾驶舱**：当前任务 + 设计约束 + 配置导航。
> 详细键位设计文档 → [docs/keymap-design.md](docs/keymap-design.md)

## 🎯 当前聚焦：阶段三 - 极客常态期（2026-03-16 起）

> 外围键已恢复，Legacy 层已移除，不再误触。
> 训练目标：Ctrl+S 等组合键全部走 OSM 路径，小拇指彻底解放。

- **当前痛点**：标点符号层（Sym 层）键位记不住，需要反复练习

### 进行中

> 开发前在此写详细规划，完成后清除并归档。

#### 蓝牙频繁断联问题排查及配置调优

- 详见：[ZMK 固件底层调试与断联排查指南](docs/debug-guide.md)
- **真凶发现**：原因 0x22 (LMP Response Timeout) 是由于 SuperMini 等克隆板缺少外部晶振，刷入官方固件后导致时钟漂移
- **终极方案**：强制启用内部 RC 振荡器 (`CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y`)，并撤销之前的临时超时补救措施
  - 已应用于 → [`config_silakka54/lily58.conf:10-11`](config_silakka54/lily58.conf)
  - Lily58 主配置切换为外部晶振 → [`config/lily58.conf:24`](config/lily58.conf)
- **二轮优化（针对克隆板握手崩溃）**：针对 `Err 9 (Security failed)` 拒绝连接问题
  - `CONFIG_BT_CTLR_PHY_2M=n`（强制降级 1M PHY）→ [`config/lily58.conf:12`](config/lily58.conf)
  - `CONFIG_ZMK_BLE_EXPERIMENTAL_SEC=y` → [`config/lily58.conf:32`](config/lily58.conf)
- [x] 初始排查与临时补救
- [x] 根因确认（时钟漂移）
- [x] 终极方案实施（RC 振荡器 / 外部晶振切换）
- [x] 二轮优化（1M PHY 降级 + 实验性安全配对）
- [x] 三轮优化（核动力防卡死满血版：1000mAh永不休眠、放宽晶振 250PPM 容差、队列拓宽、接入官方实验性调度）
- [ ] 长期稳定性观察（持续监控中）

### 规划

#### Combo 系统演进

> 为 Sweep 风格布局（每侧仅 2 拇指键）做准备，将当前依赖第 3 拇指键的功能迁移到 Combo 触发。

**约束**：
- 五笔输入法用户，Combo 键位必须避开高频 bigram（数据见 `research/wubi-bigram-analysis.md`）
- 需要 Combo 替代的功能：ESC、Shift（原第 3 拇指键承载）

**现有 Combo 清单**（含 keymap 源码位置）：

| Combo | 键位 | 功能 | 层 | 状态 | 源码位置 |
|-------|------|------|----|------|---------|
| `S+D` | pos 26+27 (L58) / 11+12 (34k) | ESC | Base | ✅ | [`config/lily58.keymap:123-129`](config/lily58.keymap) |
| `F+J` | pos 28+31 (L58) / 13+16 (34k) | Caps Word | Base | ✅ | [`config/lily58.keymap:132-138`](config/lily58.keymap) |
| `J+K` | pos 31+32 (L58) / 16+17 (34k) | LSHFT | Base | ✅ | [`config/lily58.keymap:141-147`](config/lily58.keymap) |
| 左双拇指 | pos 52+53 (L58) / 30+31 (34k) | FUN 层 | Base | ✅ | [`config/lily58.keymap:150-155`](config/lily58.keymap) |
| 右双拇指 | pos 54+55 (L58) / 32+33 (34k) | MEDIA 层 | Base | ✅ | [`config/lily58.keymap:158-163`](config/lily58.keymap) |

**Sweep 拇指区降维变化**：

```
Lily58 (4 拇指，3 核心):  none │ ESC(FUN) │ SPACE(NAV) │ TAB(NUM)     ← 左手
                          ENTER(SYM) │ BSPC(MOU) │ LSHFT(MED) │ none  ← 右手

Sweep  (2 拇指):          SPACE(NAV) │ TAB(NUM)     ← 左手
                          ENTER(SYM) │ BSPC(MOU)    ← 右手
                          FUN = 左双拇指 combo, MEDIA = 右双拇指 combo
```

**待决事项**：

- [x] 确定 Sweep 拇指区 2 键各自承载什么功能
- [x] 确定需要 Combo 化的完整功能清单
- [x] 从安全组合池中为单次 Shift 选定最佳按键 `S+D`
- [x] 增加 Sweep 拇指同按 Combo
- [ ] 评估是否需要跨层 Combo

**选键数据基础**：五笔 Bigram 频率分析已完成（`research/`），top300 零命中的安全组合：`sd`（167）、`jk`（166）、`as`（134）、`sf`（132）— 共 103 个候选。

---

## 📐 设计约束

| 编号 | 规则 |
|------|------|
| KEY-01 | Callum-style OSM：不用 Home Row Mods / Hold-Tap，独立层 + Sticky Keys |
| KEY-02 | 对侧控制：左手拇指切层 → 右手执行功能，反之亦然 |
| KEY-03 | 3x5 核心区跨硬件完全一致，差异仅在拇指键数量和降维策略 |
| KEY-04 | `skq`（quick-release）仅限 Shift；`skn`（无 quick-release）给 Ctrl/Alt/GUI |
| KEY-05 | 所有涉及中英文切换的 Shift 均使用 `LSHFT`（Windows 输入法钩子限制） |
| KEY-06 | `tlt` 必须移除 `require-prior-idle-ms`（防止长按被吃掉） |
| BLE-01 | 克隆板必须启用 RC 振荡器或外部晶振校准，防止时钟漂移断连 |
| BLE-02 | `CONFIG_BT_CTLR_PHY_2M=n`，强制 1M PHY 保证信号稳定 |

> 完整键位设计哲学 → [docs/keymap-design.md § 设计哲学](docs/keymap-design.md#设计哲学双核驱动过渡方案)

---

## 🗺️ 配置文件导航

### 项目结构

```
zmk-config/
├── config/                    # 主配置目录（Lily58 / Sweep / Dolphin1 / BGKeeB）
│   ├── lily58.keymap          # 58 键主力配置（9 层，含 Snipe/Turbo 影子层）
│   ├── lily58.conf            # 58 键蓝牙/功能开关
│   ├── cradio.keymap          # Sweep 34 键配置（7 层）
│   ├── cradio.conf            # Sweep 蓝牙配置
│   ├── dolphin1.keymap        # Dolphin1 自制 PCB 34 键（= cradio 布局）
│   ├── dolphin1.conf          # Dolphin1 蓝牙配置
│   ├── bgkeeb.keymap          # BGKeeB 38 键（3x5+4 拇指 + 旋钮，含 Snipe/Turbo）
│   └── bgkeeb.conf            # BGKeeB 蓝牙配置
├── config_silakka54/          # Silakka54 独立配置（通过 cmake-args 切换）
│   ├── lily58.keymap          # Silakka54 版 58 键（拇指区 3+1 布局）
│   └── lily58.conf            # Silakka54 蓝牙（RC 振荡器）
├── boards/shields/            # 自定义 Shield 定义（dolphin1, bgkeeb）
├── build.yaml                 # GitHub Actions 构建矩阵
├── docs/                      # 文档
│   ├── keymap-design.md       # 键位设计体系（真相源，ZMK + RMK 跨平台）
│   ├── debug-guide.md         # 固件调试与断联排查
│   ├── bluetooth-troubleshooting.md
│   ├── deploy.md              # 部署说明
│   └── ...
└── research/                  # 数据分析（五笔 bigram 等）
```

### Keymap 配置对照

> 所有分支的 3×5 核心区（字母、符号、功能层）**完全相同**，差异仅在拇指键。

| 硬件 | 键数 | 拇指键/侧 | Keymap 文件 | Conf 文件 | 层数 | 特殊功能 |
|------|------|-----------|-------------|-----------|------|---------|
| Lily58 | 58 | 4（3 核心 + 1 冗余） | [`config/lily58.keymap`](config/lily58.keymap) | [`config/lily58.conf`](config/lily58.conf) | 9 | Snipe/Turbo 影子层、ZMK Studio |
| Silakka54 | 58 | 4（3 核心 + 1 辅助） | [`config_silakka54/lily58.keymap`](config_silakka54/lily58.keymap) | [`config_silakka54/lily58.conf`](config_silakka54/lily58.conf) | 9 | RC 振荡器、平滑滚动 |
| Sweep | 34 | 2 | [`config/cradio.keymap`](config/cradio.keymap) | [`config/cradio.conf`](config/cradio.conf) | 7 | 双拇指 Combo 切层、支持 Dongle 模式 |
| Dolphin1 | 34 | 2 | [`config/dolphin1.keymap`](config/dolphin1.keymap) | [`config/dolphin1.conf`](config/dolphin1.conf) | 7 | 自制 PCB，= Sweep 布局，[RMK 固件](https://github.com/haobogu/rmk) keymap: [`~/projects/rmk-dolphin/nrf52840_split/keyboard.toml`](../rmk-dolphin/nrf52840_split/keyboard.toml) |
| BGKeeB | 38 | 4 | [`config/bgkeeb.keymap`](config/bgkeeb.keymap) | [`config/bgkeeb.conf`](config/bgkeeb.conf) | 9 | 旋钮、Snipe/Turbo |

### 设计变更时需同步的文件清单

> 3×5 核心区（字母、符号、功能层）跨所有硬件 + 固件平台保持一致。
> 修改键位设计时，以下文件**全部需要同步更新**：

| # | 文件 | 说明 |
|---|------|------|
| 1 | `docs/keymap-design.md` | 键位设计真相源（ZMK + RMK 跨平台） |
| 2 | `config/lily58.keymap` | Lily58 (58键, 9层) |
| 3 | `config_silakka54/lily58.keymap` | Silakka54 (58键, 9层) |
| 4 | `config/cradio.keymap` | Sweep (34键, 7层) |
| 5 | `config/dolphin1.keymap` | Dolphin1 ZMK (34键, 7层) |
| 6 | `config/bgkeeb.keymap` | BGKeeB (38键, 9层) |
| 7 | `~/projects/rmk-dolphin/nrf52840_split/keyboard.toml` | Dolphin1 RMK 固件 |

### 核心 Behavior 定义（各 keymap 共享）

| Behavior | 标签 | 用途 | 定义位置示例 |
|----------|------|------|-------------|
| `skq` | `sticky_key_quick_release` | Shift 专用 OSM（快速释放） | [`config/lily58.keymap:76-83`](config/lily58.keymap) |
| `skn` | `sticky_key_normal` | Ctrl/Alt/GUI OSM（支持链式组合） | [`config/lily58.keymap:86-92`](config/lily58.keymap) |
| `tlt` | `thumb_layer_tap` | 拇指 Layer-Tap（balanced，无 idle 保护） | [`config/lily58.keymap:95-102`](config/lily58.keymap) |
| `swapper` | Alt-Tab 宏 | Nav 层窗口切换 | [`config/lily58.keymap:106-117`](config/lily58.keymap) |

### 蓝牙配置对比

| 配置项 | Lily58 | Silakka54 | 说明 |
|--------|--------|-----------|------|
| 时钟源 | 外部晶振 (`XTAL`) | 内部 RC (`RC`) | 克隆板用 RC 更稳定 |
| 晶振精度 | `50PPM` | `500PPM` | RC 振荡器精度低需放宽 |
| 2M PHY | `n` | `n` | 强制 1M 保信号 |
| 发射功率 | `+8 dBm` | `+8 dBm` | 自制 PCB 天线补偿 |
| ZMK Studio | `y` | — | Lily58 开启实时调键 |
| Studio 锁 | `n` | — | 免 PIN 码解锁 |
| 实验性 BLE | `y` | 已禁用 | Zephyr 4.1+ 部分已合入主线 |
| 休眠超时 | 15 min | 15 min | `CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000` |

> 完整蓝牙配置 → [`config/lily58.conf`](config/lily58.conf) / [`config_silakka54/lily58.conf`](config_silakka54/lily58.conf)

---

## 七层架构总览

| 层号 | 名称 | 激活方式 | 功能手 | 控制手 |
|------|------|---------|-------|-------|
| 0 | Base | 默认层 | 双手 | — |
| 1 | Nav & Mods | 左拇指 SPACE 长按 | 右手 | 左手 |
| 2 | Numpad | 左拇指 TAB 长按 | 右手 | 左手 |
| 3 | Symbols | 右拇指 ENTER 长按 | 左手 | 右手 |
| 4 | Function | 左拇指 ESC 长按 / 左双拇指 Combo | 右手 | 左手 |
| 5 | Mouse | 右拇指 BSPC 长按 | 左手 | 右手 |
| 6 | Media | 右拇指 LSHFT 长按 / 右双拇指 Combo | 左手 | 右手 |

> Lily58 额外包含 Layer 7 (M_SNIPE) 和 Layer 8 (M_TURBO) 影子层
> 完整键位布局图 → [docs/keymap-design.md § 键位布局总览](docs/keymap-design.md#键位布局总览)

---

## 🔧 快速命令

```bash
# GitHub Actions 自动构建（push 触发）
git push origin main

# 本地构建（需要 west + Zephyr SDK）
west build -b nice_nano -- -DSHIELD=lily58_left

# Silakka54 构建（指定独立配置目录）
west build -b nice_nano -- -DSHIELD=lily58_left -DZMK_CONFIG="config_silakka54"

# 烧录固件（双击 RESET 进入 UF2 模式后拖入）
cp build/zephyr/zmk.uf2 /media/$USER/NICENANO/
```

> 构建矩阵定义 → [`build.yaml`](build.yaml)
> 部署说明 → [docs/deploy.md](docs/deploy.md)

---

## 📚 文档导航

- [键位设计体系](docs/keymap-design.md) — 34/36/58 键统一架构、层布局图、ZMK + RMK 跨平台实现要点（**真相源**）
- [固件调试与断联排查](docs/debug-guide.md) — USB 日志、蓝牙断连 debug 流程
- [蓝牙故障排除](docs/bluetooth-troubleshooting.md) — 断联排查专题
- [硬件引脚映射](docs/hardware-pin-mapping.md) — MCU 引脚与矩阵位置对应
- [MCU 参考](docs/mcu-reference.md) — nRF52840 / Nice!Nano 技术细节
- [专家咨询记录](docs/expert-consultation.md) — 社区咨询与方案讨论
- [部署说明](docs/deploy.md) — 固件烧录与 OTA 流程
- [Dongle 三模改造方案](docs/dongle-migration-plan.md) — 📋 Lily58 待定；已于 2026-07-15 完成 Sweep (cradio) 的 Dongle 固件改造，参见 `boards/shields/cradio_dongle` 盾板定义。

---

## 进化路线图

- **阶段一：安全感过渡期**（第 1-2 周）→ ✅ 已毕业
- **阶段二：Callum 觉醒期**（第 3-4 周）→ ✅ 已毕业
- **阶段三：极客常态期**（第 2 个月后）→ 🔄 当前阶段
- **阶段四：Corne/Dolphin 迁移** → 📋 待定

> 详细路线图 → [docs/keymap-design.md § 进化路线图](docs/keymap-design.md#进化路线图)

---

## 已完成归档

### Sweep (cradio) Dongle 接收器固件支持（2026-07-15）

- [x] 创建 `cradio_dongle` 接收器 Shield 并在 overlay 中配置 `zmk,kscan-mock` 过滤幽灵按键，蓝牙广播名称设置为 `"Dolphin Dongle"`
- [x] 新增 `config/cradio_left_dongle.conf` 配置，通过 `cmake-args` 覆盖将左手强制降级为 Peripheral 从机角色，同时开启休眠、关闭 Studio
- [x] 更新 `build.yaml` 矩阵，追加 `sweep_dongle`、`sweep_left_dongle_mode` 以及 `sweep_right_dongle_mode` 构建目标

### Dolphin1 Shield 对比审查与修复（2026-04-01）

- [x] 对比 `cradio` 与 `dolphin1` 的定义差异
- [x] 修复 `dolphin1.dtsi` 中漏掉的 `zmk,matrix-transform = &default_transform;` 的致命错误
- [x] 确认其它 overlay，Kconfig 及 build.yaml 均正确对应

### bgkeeb 仓库配置合并（2026-04-01）

- [x] 将 zmk-bgkeeb 仓库中的配置迁移至 [`config/bgkeeb.keymap`](config/bgkeeb.keymap) + [`config/bgkeeb.conf`](config/bgkeeb.conf)
- [x] 将 shield 定义移动至 `boards/shields/`
- [x] 更新 [`build.yaml`](build.yaml) 构建矩阵

### Corne 36 键 keymap 移植（2026-04-01）

- [x] 在 `config` 中创建 `corne.keymap`，摘取 Lily58 的 Callum-OSM 精华
- [x] 利用 `&none` 屏蔽 Corne 42 键最外围 6 列，实现 36 键纯净约束
- [x] 基于 Corne 42 键矩阵坐标系重算所有 Combo `key-positions`
- [x] 更新 [`build.yaml`](build.yaml) 矩阵

### 双方案共存配置（2026-03-10）

- [x] [`build.yaml`](build.yaml) 增加 `cmake-args: -DZMK_CONFIG` 支持
- [x] `silakka54` 分支键映射平移到 [`config_silakka54/`](config_silakka54/) 文件夹

### 上板实测与阶段一毕业（2026-03-05）

- [x] 固件烧录实际使用
- [x] 物理冗余键已完全封印，3 拇指分工已适应
- [x] Mouse 层优化：移除冗余剪贴板/CAPS/INS，新增撤销/重做与虚拟桌面切换

### 高级功能与局部强化（2026-03-04）

- [x] Nav 层 Alt-Tab Swapper（`&swapper` 宏）→ [`config/lily58.keymap:106-117`](config/lily58.keymap)
- [x] 鼠标层 Snipe/Turbo 模式 → [`config/lily58.keymap:31-43`](config/lily58.keymap)（速度宏定义）
- [x] 拇指键 `&tlt MEDIA LSHFT` 精简 + 去除 idle 保护 → [`config/lily58.keymap:95-102`](config/lily58.keymap)
- [x] 废弃 `D+F` 组合键，采用独立拇指 Shift 替代

### 鼠标层指针速度优化（2026-03-04）

- [x] 覆写 `&mmv` 和 `&msc` 默认属性 → [`config/lily58.keymap:56-66`](config/lily58.keymap)
- [x] `ZMK_POINTING_DEFAULT_MOVE_VAL 1500` / `SCRL_VAL 20` → [`config/lily58.keymap:27-28`](config/lily58.keymap)

### 双核 36 键改造（2026-03-03）

- [x] Base 层外围全 `&none`，模拟 Corne 36 键约束
- [x] 拇指 `tlt` 防误触行为 + OSM 分离（`skq` / `skn`）
- [x] K_CANCEL 后悔药、鼠标层点击下放、Sym 层补 `'`

### 层架构重构（2026-03-02）

- [x] NUM/SYM 层分离重排、Nav 层收纳优化
- [x] Caps Word 双触发（F+J Combo + Nav 层 G 位）

### 初始实现（2026-03-01）

- [x] Callum-style `skq` 行为定义 + JK Combo
- [x] 全 7 层架构 + GitHub Actions 编译验证通过
