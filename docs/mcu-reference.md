# 主控参考手册 (MCU Reference)

> nice!nano v2 / Supermini NRF52840 — 基于 Nordic nRF52840 SoC 的 Pro Micro 兼容主控

## 它到底是个啥？

nice!nano 是一块自带蓝牙和电池充电功能的「进阶版」Pro Micro 主控。

- 尺寸与 Pro Micro 完全兼容：24 个主引脚（左右各 12 个）排列一致
- Sweep、Corne、Lily58 等基于 Pro Micro 设计的键盘可以直接插上 nice!nano，配合电池从有线升级为无线
- Supermini NRF52840 是 nice!nano v2 的低成本克隆，引脚布局与分区兼容

## 芯片概览

- SoC: Nordic nRF52840 (ARM Cortex-M4F, 64MHz)
- 无线: BLE 5.0
- Flash: 1MB / RAM: 256KB（对键盘固件非常富裕，复杂层级和宏命令随便塞）
- 工作电压: 3.3V（GPIO 均为 3.3V 逻辑）
- USB: 原生 Type-C（有线打字 / 充电 / 刷固件）
- Bootloader: Adafruit nRF52 (UF2)
- 分区布局: Supermini NRF52840 兼容 `nice_nano_v2`

## ZMK Board 命名

| ZMK 版本 | V1 | V2 (默认) |
|----------|-----|-----------|
| 旧版 (Zephyr <4.1) | `nice_nano` | `nice_nano_v2` |
| 新版 (Zephyr 4.1+) | `nice_nano@1//zmk` | `nice_nano//zmk` |

- 新 Fork 的仓库必须用 `nice_nano//zmk`
- 旧仓库继续用 `nice_nano_v2` 即可

## GPIO 引脚映射

nice!nano v2 共 21 个可用 GPIO，完全兼容 Pro Micro 引脚编号。

### Pro Micro 引脚 → nRF52840 GPIO 对照表

| Pro Micro Pin | nRF52840 GPIO | Arduino 别名 | 备注 |
|:---:|:---:|:---:|:---|
| 0 | P0.08 | D0 / TX | |
| 1 | P0.06 | D1 / RX | |
| 2 | P0.15 | D2 | |
| 3 | P0.17 | D3 | |
| 4 | P0.20 | D4 | |
| 5 | P0.13 | D5 | |
| 6 | P0.24 | D6 | |
| 7 | P0.09 | D7 | |
| 8 | P0.10 | D8 | |
| 9 | P1.06 | D9 | |
| 10 | P1.11 | D10 | |
| 14 | P0.08 | D14 / MISO | 与 pin 0 共享 |
| 15 | P0.17 | D15 / SCK | 与 pin 3 共享 |
| 16 | P0.25 | D16 / MOSI | |
| 18 | P0.02 | A0 / D18 | |
| 19 | P0.29 | A1 / D19 | |
| 20 | P0.31 | A2 / D20 | |
| 21 | P0.04 | A3 / D21 | |

> ⚠️ 上表为 nice!nano v2 官方定义。Supermini NRF52840 克隆板引脚布局相同，但建议首次使用时用万用表验证关键引脚。

### bgkeeb 实际引脚分配

bgkeeb PCB 为 4 行 × 5 列矩阵，col2row 方向，每半边 20 键（去旋钮位 = 18 键，双手共 36 键）。

**行 (Row) — 输出引脚：**

| Row | Pro Micro Pin | nRF52840 GPIO | 对应按键行 |
|:---:|:---:|:---:|:---|
| 0 | 19 | P0.29 (A1) | Q W E R T |
| 1 | 6 | P0.24 (D6) | A S D F G |
| 2 | 14 | P0.08 (MISO) | Z X C V B |
| 3 | 7 | P0.09 (D7) | 拇指行 |

**列 (Col) — 输入引脚：**

| Col | Pro Micro Pin | nRF52840 GPIO | 对应按键列 |
|:---:|:---:|:---:|:---|
| 0 | 21 | P0.04 (A3) | Q A Z ... |
| 1 | 4 | P0.20 (D4) | W S X ... |
| 2 | 20 | P0.31 (A2) | E D C ... |
| 3 | 15 | P0.17 (SCK) | R F V ... |
| 4 | 16 | P0.25 (MOSI) | T G B ... |

> 来源: `ezxzeng/zmk-bgkeeb` shield dtsi + 2026-03-21 硬件调试实测验证

### Direct Pin 方案 (Ferris Sweep / cradio)

Sweep 每半边 17 键，不使用矩阵，每个按键直连一个 GPIO + GND。

- 扫描方式: `kscan-gpio-direct`（非 `kscan-gpio-matrix`）
- 17 键占用 17 个 GPIO，nice!nano 21 个可用，剩余 4 个备用
- 无需二极管
- 参考实现: ZMK 官方 `app/boards/shields/cradio/`

**ZMK Kconfig 要点：**
```ini
# 左手 (Central)
CONFIG_ZMK_SPLIT=y
CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y

# 右手 (Peripheral)
CONFIG_ZMK_SPLIT=y
```

分体通信由 ZMK split 层自动处理，kscan 无需感知对端。

## 供电与电池

新手最容易迷糊的地方。nice!nano v2 内置电源管理和充电芯片，接电池有两种方式：

### 接法 A：走键盘底板

电池接在键盘底板上，通过引脚 `RAW` 和主排针 `GND` 给 nice!nano 供电。

- 如果底板有物理开关，可以真正切断电源
- ⚠️ 坑点：充电时必须打开物理开关，否则充不进电

### 接法 B：主控直连

电池直接焊在 nice!nano 顶部专属的 `B+` 和 `GND` 焊盘上。

- 简单粗暴，插上线必能充电
- ⚠️ 坑点：底板物理开关失效，关机全靠固件深度休眠 (Deep Sleep)

### EXT_VCC (P0.13) — RGB 杀手

v2 新增的功能引脚。无线键盘用 RGB 灯非常耗电，通过 `EXT_VCC` 可以在休眠时彻底切断 RGB 供电，极大延长续航。

### 充电电流

- 默认充电电流 100mA
- 背面有 `BOOST` 焊盘可短接提升到 500mA
- ⚠️ 只有电池容量 >500mAh 时才可以短接 BOOST，否则电池有膨胀/爆炸风险
- 分体键盘一般塞不下大电池，**不要短接 BOOST 焊盘**

## 刷写流程

1. USB 连接目标半边
2. 快速短接两次 `RST` 和 `GND`（或双击 Reset 按钮，间隔 <500ms）→ 弹出 `NICENANO` U 盘
3. 把 `.uf2` 固件文件拖进去，U 盘自动弹出，刷机完成。不需要任何刷机软件
4. 建议顺序：先刷右手（从端），再刷左手（主端）

**Supermini 注意事项：** 若刷入后蓝牙/设置异常，需先刷入 `settings_reset.uf2` 清除 NVS 分区，再刷正式固件。

## ⚠️ 新手血泪保命建议

1. **正负极是底线**：电池正负极千万不能接反！一旦接反，瞬间烧毁充电芯片，主控直接报废
2. **强烈建议用母座（热插拔）**：不要把 nice!nano 直接焊死在底板上。使用排母或 Mill-Max 针，万一排错/主板坏了/想换键盘，热插拔能救命。吸锡器拆主控是新手噩梦
3. **不要盲目短接 BOOST 焊盘**：见上方「充电电流」章节
4. **克隆板首次使用验证引脚**：Supermini 等克隆板引脚布局理论相同，但建议用万用表验证关键引脚

## 常见硬件问题

### 热插拔座接触不良

**症状：** 某列按键整列失效或同列按键串扰连击（如 T/G 同时触发）

**根因：** Pro Micro 排针与热插拔座弹片接触不良，导致列引脚信号浮动

**诊断：**
- 时好时坏 → 接触问题（非固件）
- 整列失效 → 对应列引脚
- 同列连击 → 行引脚浮动导致串扰

**修复：** 拔出主控 → 收紧热插拔座弹片 → 清理排针氧化层 → 重新插入

### 固件 Panic（蓝灯闪烁）

**常见根因：** ZMK 构建系统只在 `config/` 根目录搜索 `<shield>.conf` 和 `<shield>.keymap`，放在子目录（如 `config/boards/shields/`）不会被识别，导致关键 Kconfig 未生效。

**修复：** 确保 `.conf` 和 `.keymap` 在 `config/` 根目录下。

## 案例复盘：按键反转悬案与引脚命名避坑指南

### 1. 前因：硬件走线与原理图的“脱节”
* **历史遗留：** Ferris Sweep 是一款支持正反贴的对称（Reversible）分体键盘。在衍生版本（如 Sweep Bling MX）的 PCB 布线过程中，作者为了让实物走线更顺畅、避免过孔或交叉，**直接在 PCB 画板阶段将 Q 键和 B 键对应的引脚（Pad 9 和 Pad 10）进行了对调**。
* **图纸未更新：** 作者修改了实物 PCB 走线，却**没有同步修改原理图**。导致原理图上标示的引脚映射与实际打板出来的物理连接是相反的。

### 2. 后果：软硬件映射错位
* ZMK 官方仓库中的 `cradio`（Sweep 原版方案）默认配置是**严格按照旧版原理图**编写的。
* 当你使用 Bling MX 的板子刷入官方默认固件时，由于物理硬件的线被调换了，导致固件识别错乱：**按 Q 出 B，按 B 出 Q**。
* 由于左右板是对称翻转的，右手通常也会出现同样的镜像问题：**按 P 出 N，按 N 出 P**。

### 3. 解决方式：软件层覆盖（无需改硬件）
无需重新修改图纸或重新打板，直接利用 ZMK 的设备树覆盖（Overlay）功能在代码层把引脚“骗”回来即可。
* **左手配置 (`cradio_left.overlay`)：** 在 `kscan` 节点中，将 `<&pro_micro 6>` 和 `<&pro_micro 7>` 的位置互换。
* **右手配置 (`cradio_right.overlay`)：** 同理，检查并互换右手对应 P 和 N 的引脚定义。

---

### 4. 注意事项与核心概念避坑

在后续画板子或写固件时，理清以下三套**“引脚命名体系”**，就能避免被各种文档绕晕：

* **体系 A：物理引脚 (Pad 1, Pad 2... Pad 24)**
  * **场景：** EDA 画图、PCB 走线、万用表测通断。
  * **逻辑：** 纯粹的物理位置，从板子上往下数，包含电源和接地。**固件代码里绝对不用这个。**

* **体系 B：MCU 真实引脚 (如 D7, E6 或 P0.09)**
  * **场景：** 编写 QMK 固件底层。
  * **逻辑：** 芯片主控的真实命名。Pro Micro (ATmega32u4芯片) 叫 `D7`；nice!nano / Supermini (nRF52840芯片) 叫 `P0.09`。换主控就得换名字。

* **体系 C：ZMK 抽象接口 (`&pro_micro X`)**
  * **场景：** 编写 ZMK 固件（你当前的环境）。
  * **逻辑：** ZMK 为了实现“一套配置兼容多种主控”，把标准的 Pro Micro 尺寸做成了一个虚拟插槽。只给可编程 IO 口编号（0-20）。
  * **结论：** 无论你插的是几十块钱的 **Pro Micro**、上百块的 **nice!nano v2**，还是国产平替 **Supermini nRF52840**，只要它们的物理尺寸兼容，**在 ZMK 的引脚映射里一律写 `<&pro_micro X>`**。编译时只要选对 Board，ZMK 底层会自动把它们翻译成真实的 MCU 引脚。

## 参考链接

- [nice!nano v2 官方文档](https://nicekeyboards.com/nice-nano/)
- [ZMK 官方 cradio shield](https://github.com/zmkfirmware/zmk/tree/main/app/boards/shields/cradio)
- [bgkeeb ZMK 固件](https://github.com/yekingyan/zmk-bgkeeb)
- [主 ZMK 配置仓库](https://github.com/yekingyan/zmk-config)
