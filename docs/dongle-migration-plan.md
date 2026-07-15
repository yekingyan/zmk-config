# ZMK Sweep (cradio) Dongle 三模改造指南（已落地实施）

> 状态：✅ 已落地实施（2026-07-15）
> 关联：[plan.md § 已完成归档](../plan.md#已完成归档)

## 一、项目背景与核心逻辑

**目标**：复用一块坏引脚的 nRF52840 主控作为独立接收器（Dongle），将现有双模 Sweep (cradio) 键盘（蓝牙 + 有线）升级为 **Dongle 三模（伪 2.4G + 蓝牙 + 有线）**，换取更低延迟、更长续航、以及多设备切换能力。

**架构变更**：

| | 原架构（双模） | 新架构（Dongle 三模） |
|---|---|---|
| 主机（Central） | 左手（直连电脑/手机） | Dongle（独立接收端主控） |
| 左手 | Central（主机） | 降级为 Peripheral（从机） |
| 右手 | Peripheral（从机） | Peripheral（从机，保持不变） |

**⚠️ 限制须知**：
- 刷入此固件后，键盘本体插线电脑**只能充电**，所有按键信号必须经由 Dongle 接收器转发。
- 无法与现有双模固件热切换，回退需重新刷回旧的双模固件 + `settings_reset.uf2` 清空配对。
- 该方案与原有的双模架构互斥。我们通过新建独立的编译产物（左右手机身 + dongle 共三份固件）来实现，完全不改动原本双模版 `cradio_left.conf` 配置，确保两种方案完美共存。

---

## 二、硬件排查（坏引脚主控复用为 Dongle）

组装前硬件自查三项：
1. **USB 数据链路正常**：能进入 Bootloader（U 盘模式），可拷入 `.uf2` 文件。
2. **复位功能正常**：短接 Reset 或双击按钮可正常重启进入刷机模式。
3. **无严重内部短路**：通电后主控芯片不发热/不烫手；若发热明显应废弃，避免损坏电脑 USB 接口。

---

## 三、代码仓改动清单（以 Sweep cradio 为例）

自定义 shield 统一放在根目录 `boards/shields/<name>/`。由于 Dongle 接收端没有物理键盘矩阵，我们利用虚拟扫描器接管输入，屏蔽坏主控的悬空引脚。

### 1. 左手降级为纯从机

新建 [`config/cradio_left_dongle.conf`](../config/cradio_left_dongle.conf)（隔离原双模配置）：

```ini
# 强制左手降级为从机 (Peripheral)
CONFIG_ZMK_SPLIT_ROLE_CENTRAL=n

# 降级为从机后功耗极低，开启 15 分钟无操作深度休眠
CONFIG_ZMK_SLEEP=y
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000 # 15分钟休眠

# 从机端不需要开启 ZMK Studio 
CONFIG_ZMK_STUDIO=n
```

新建 [`config/cradio_right_dongle.conf`](../config/cradio_right_dongle.conf) 用以在 Dongle 模式下为右手机身开启休眠（原双模普通模式下右手因电池大保持不休眠，而在从机模式下开启休眠可节省电量）：

```ini
# 降级为从机后开启深度休眠（从机端休眠能极大省电）
CONFIG_ZMK_SLEEP=y
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000 # 15分钟休眠
```

### 2. 新建 Dongle Shield 盾板

目录：`boards/shields/cradio_dongle/`

**文件 A：`Kconfig.shield`**
```text
# Copyright (c) 2026 The ZMK Contributors
# SPDX-License-Identifier: MIT

config SHIELD_CRADIO_DONGLE
    def_bool $(shields_list_contains,cradio_dongle)
    select ZMK_SPLIT
```
*注：必须 `select ZMK_SPLIT` 以确保构建系统引入 ZMK 分体键盘所需的底层蓝牙通信协议及选择依赖。*

**文件 B：`Kconfig.defconfig`**
```text
if SHIELD_CRADIO_DONGLE

config ZMK_KEYBOARD_NAME
    default "Dolphin Dongle"

config ZMK_SPLIT_ROLE_CENTRAL
    def_bool y

endif # SHIELD_CRADIO_DONGLE
```
*注：直接在 Kconfig 层级定义默认键盘名称为 `"Dolphin Dongle"` 并强制开启主机（Central）角色。*

**文件 C：`cradio_dongle.zmk.yml`**（盾板元数据）
```yaml
file_format: "1"
id: cradio_dongle
name: Dolphin Dongle
type: shield
requires: [pro_micro]
features:
  - keys
```

**文件 D：`cradio_dongle.conf`**
```ini
# 强制设置为主机 (Central)
CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y

# Dongle 需要连接左手和右手两个从机
CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS=2

# 最大蓝牙连接数：5个主机连接 + 2个分体连接 = 7
CONFIG_BT_MAX_CONN=7
CONFIG_BT_MAX_PAIRED=7

# 增加蓝牙发射功率，提升信号稳定性
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y

# 启用 ZMK Studio 支持（供 Dongle 接收器免 PIN 改键）
CONFIG_ZMK_STUDIO=y
CONFIG_ZMK_STUDIO_LOCKING=n
```

**文件 E：`cradio_dongle.overlay`**
```dts
#include <dt-bindings/zmk/matrix_transform.h>

/ {
    chosen {
        zmk,kscan = &mock_kscan;
        zmk,matrix-transform = &default_transform;
    };

    default_transform: keymap_transform_0 {
        compatible = "zmk,matrix-transform";
        columns = <34>;
        rows = <1>;
        map = <
        RC(0,0)  RC(0,1)  RC(0,2)  RC(0,3)  RC(0,4)    RC(0,21) RC(0,20) RC(0,19) RC(0,18) RC(0,17)
        RC(0,5)  RC(0,6)  RC(0,7)  RC(0,8)  RC(0,9)    RC(0,26) RC(0,25) RC(0,24) RC(0,23) RC(0,22)
        RC(0,10) RC(0,11) RC(0,12) RC(0,13) RC(0,14)   RC(0,31) RC(0,30) RC(0,29) RC(0,28) RC(0,27)
                                   RC(0,15) RC(0,16)   RC(0,33) RC(0,32)
        >;
    };

    mock_kscan: mock_kscan_0 {
        compatible = "zmk,kscan-mock";
        columns = <0>;
        rows = <0>;
        events = <0>;
    };
};
```
*注：`events = <0>;` 在 `zmk,kscan-mock` 中必须声明，用以满足 ZMK 底层 `kscan_mock.c` 驱动初始化时对事件大小定义的检测，否则会发生编译阶段数组大小未定义的报错。*

### 3. 修改构建矩阵

在 [`build.yaml`](../build.yaml) 中追加编译项：

```yaml
  # sweep (cradio) dongle 三模改造
  - board: nice_nano//zmk
    shield: cradio_dongle
    snippet: studio-rpc-usb-uart
    artifact-name: sweep_dongle
  - board: nice_nano//zmk
    shield: cradio_left
    cmake-args: -DEXTRA_CONF_FILE="${GITHUB_WORKSPACE}/config/cradio_left_dongle.conf"
    artifact-name: sweep_left_dongle_mode
  - board: nice_nano//zmk
    shield: cradio_right
    cmake-args: -DEXTRA_CONF_FILE="${GITHUB_WORKSPACE}/config/cradio_right_dongle.conf"
    artifact-name: sweep_right_dongle_mode
```

---

## 四、烧录与配对 SOP

因蓝牙主从关系彻底重构，旧配对缓存会导致设备无法互连，**必须严格按顺序执行**：

### 步骤 1：全盘清除配对记忆
1. Dongle、左手、右手 3 个主控分别双击 Reset 进入 U 盘模式（弹出 `NICENANO` 磁盘）。
2. 依次拖入 `settings_reset.uf2`。
3. 刷入后主控自动重启闪烁，并自动再次进入 U 盘模式，表示清空完成。

### 步骤 2：烧录新固件
1. 再次依次使主控进入 U 盘模式，并拖入对应的正式固件：
   - `sweep_dongle.uf2` → 坏引脚主控（Dongle）。
   - `sweep_left_dongle_mode.uf2` → 左手键盘主控。
   - `sweep_right_dongle_mode.uf2` → 右手键盘主控。

### 步骤 3：建立配对通道
1. 先给 Dongle 通电（插入电脑 USB 接口，确认常亮）。
2. 将左手键盘开机（开启电池开关，**并且必须拔掉 USB 数据线**），靠近 Dongle，几秒内自动连上。
3. 将右手键盘开机（开启电池开关，**拔掉 USB 数据线**），自动连上 Dongle。
4. 按键验证：左右手输入能在电脑上正常输出字符即为成功。

---

## 五、日常使用说明

- **2.4G 模式（即插即用）**：Dongle 插入电脑，即插即用，可进 BIOS。
- **有线模式**：等同于 2.4G 模式；键盘机身接线仅充电。
- **蓝牙模式**：
  1. Dongle 必须通电（USB 供电口或充电宝）。
  2. 键盘上按 `BT 1`~`BT 5` 切换 Dongle 对应的主机蓝牙连接通道。
  3. 电脑/平板搜索到的蓝牙设备是 **`Dolphin Dongle`**，而不是键盘机身。
