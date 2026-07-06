# ZMK Lily58 Dongle 三模改造方案（规划中，未实施）

> 状态：📋 待定 — 记录方案供后续评估/实施参考，尚未动工。
> 关联：[plan.md § 阶段四：Corne/Dolphin 迁移](../plan.md)

## 一、项目背景与核心逻辑

**目标**：复用一块坏引脚的 nRF52840 主控作为独立接收器（Dongle），将现有双模 Lily58（蓝牙 + 有线）升级为 **Dongle 三模（伪 2.4G + 蓝牙 + 有线）**，换取更低延迟、更长续航、多设备切换能力。

**架构变更**：

| | 原架构（双模） | 新架构（Dongle 三模） |
|---|---|---|
| 主机（Central） | 左手（直连电脑/手机） | Dongle（独立主控） |
| 左手 | Central | 降级为 Peripheral |
| 右手 | Peripheral | Peripheral（不变） |

**⚠️ 限制须知**：
- 刷入此固件后，键盘本体插线电脑**只能充电**，所有信号必须经 Dongle 转发。
- 无法与现有双模固件热切换，回退需重新刷回旧固件 + `settings_reset`。
- 该方案与现有 [`config/lily58.conf`](../config/lily58.conf) 的双模架构互斥，需要新建独立的编译产物（左右手 + dongle 各一份固件），不能与当前 `lily58_left` / `lily58_right` 共用同一份 `.conf`。

## 二、硬件排查（坏引脚主控复用为 Dongle）

组装前硬件自查三项：
1. **USB 数据链路正常**：能进入 Bootloader（U 盘模式），可拷入 `.uf2`。
2. **复位功能正常**：短接 Reset 或双击按钮可正常重启进入刷机模式。
3. **无严重内部短路**：通电后主控芯片不发热/不烫手；若发热明显应废弃，避免损坏电脑 USB 口。

## 三、代码仓改动清单（对照本仓库实际结构修正）

> 本仓库 `build.yaml` 位于**仓库根目录**（不是 `.github/workflows/build.yaml`），自定义 shield 统一放在根目录 `boards/shields/<name>/`（参考现有 [`boards/shields/dolphin1/`](../boards/shields/dolphin1) 结构），且需要同时提供 `Kconfig.shield` 与 ZMK 新版元数据文件 `<name>.zmk.yml`（现有 shield 均遵循此约定，见 `dolphin1.zmk.yml`）。以下路径已按此修正。

### 1. 左手降级为纯从机

新建 `config/lily58_left.conf`（若已存在则在现有基础上追加）：

```ini
# 强制左手降级为从机 (Peripheral)
CONFIG_ZMK_SPLIT_BLE_ROLE_CENTRAL=n

# 降级为从机后功耗极低，开启深度休眠
CONFIG_ZMK_SLEEP=y
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000
```

> 注意：右手保持现状（Peripheral 不变），不需要新建 `lily58_right.conf`，除非现有配置中有需要针对性调整的项。

### 2. 新建 Dongle Shield

目录：`boards/shields/lily58_dongle/`（**根目录 boards/shields 下**，不是 `config/boards/shields/`）

**文件 A：`Kconfig.shield`**
```text
# Copyright (c) 2026 The ZMK Contributors
# SPDX-License-Identifier: MIT

config SHIELD_LILY58_DONGLE
    def_bool $(shields_list_contains,lily58_dongle)
```

**文件 B：`Kconfig.defconfig`**
```text
if SHIELD_LILY58_DONGLE

config ZMK_KEYBOARD_NAME
    default "Lily58 Dongle"

endif # SHIELD_LILY58_DONGLE
```

**文件 C：`lily58_dongle.zmk.yml`**（新版 shield 元数据，参考现有 `dolphin1.zmk.yml` 格式）
```yaml
file_format: "1"
id: lily58_dongle
name: Lily58 Dongle
type: shield
requires: [pro_micro]
features:
  - keys
```

**文件 D：`lily58_dongle.conf`**
```ini
# 强制设置为主机 (Central)
CONFIG_ZMK_SPLIT_BLE_ROLE_CENTRAL=y

# 增加蓝牙发射功率，提升 Dongle 与主机/手机的连接稳定性
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y
```

**文件 E：`lily58_dongle.overlay`**（核心：虚拟扫描器接管输入，屏蔽坏主控的幽灵按键）
```dts
#include <dt-bindings/zmk/matrix_transform.h>
#include "lily58.dtsi"

/ {
    chosen {
        zmk,kscan = &mock_kscan;
    };

    mock_kscan: mock_kscan_0 {
        compatible = "zmk,kscan-mock";
        columns = <0>;
        rows = <0>;
        events = <0>;
    };
};
```

> ⚠️ 待验证项：`lily58.dtsi` 中是否已声明了物理 kscan 及 matrix-transform，若有需要在 `mock_kscan` 覆盖后确认不会与原有 `zmk,kscan` chosen 节点冲突（参考 [`boards/shields/dolphin1/dolphin1.dtsi`](../boards/shields/dolphin1/dolphin1.dtsi) 的处理方式）。`zmk-kscan-mock` compatible 字符串与属性名需要以实际 ZMK 版本的 `dts/bindings` 为准，实施前应查阅所用 ZMK 分支的 `app/dts/bindings/kscan/zmk,kscan-mock.yaml`。

### 3. 修改 `build.yaml`（根目录，非 `.github/workflows/build.yaml`）

在现有 `include:` 列表中追加（不要新建文件，直接在现有 [`build.yaml`](../build.yaml) 里加）：

```yaml
  # dongle 三模改造（规划中）
  - board: nice_nano//zmk
    shield: lily58_dongle
    artifact-name: lily58_dongle
  - board: nice_nano//zmk
    shield: lily58_left
    artifact-name: lily58_left_dongle_mode
  - board: nice_nano//zmk
    shield: lily58_right
    artifact-name: lily58_right_dongle_mode
```

> 命名冲突提醒：现有 `build.yaml` 已存在 `artifact-name: lily58_left` / `lily58_right`（双模固件）。Dongle 模式下左手用的是同一个 `lily58_left` shield 但加载不同的 `.conf`（`CONFIG_ZMK_SPLIT_BLE_ROLE_CENTRAL=n`），**必须改用不同的 `artifact-name`** 加以区分，避免下载时覆盖或混淆双模/三模固件。上面已用 `_dongle_mode` 后缀区分。
>
> `settings_reset` 固件已存在于现有 `build.yaml`，无需重复添加。

## 四、烧录与配对 SOP

因蓝牙主从关系彻底重构，旧配对缓存会导致设备无法互连，**必须严格按顺序执行**：

### 步骤 1：全盘清除配对记忆
1. Dongle、左手、右手 3 个主控全部双击 Reset 进入 U 盘模式。
2. 依次拖入 `settings_reset.uf2`。
3. 刷入后主控自动重启闪烁，再次进入 U 盘模式，表示清空完成。

### 步骤 2：烧录新固件
1. `lily58_dongle.uf2` → 坏引脚主控（Dongle）。
2. `lily58_left_dongle_mode.uf2` → 左手主控。
3. `lily58_right_dongle_mode.uf2`（或沿用原 `lily58_right.uf2`，若右手固件未变）→ 右手主控。

### 步骤 3：建立配对通道
1. 先给 Dongle 通电（插入电脑 USB 口，确认亮灯）。
2. 左手通电（开电池开关，**拔掉 USB 数据线**），几秒内自动连上 Dongle。
3. 右手通电（同上），自动连上 Dongle。
4. 按键验证：左右手输入能在电脑上正常输出字符即为成功。

## 五、日常使用说明（交付用户）

- **2.4G 模式**：Dongle 插入电脑，即插即用，可进 BIOS。
- **有线模式**：等同 2.4G 模式；键盘本体接线仅充电。
- **蓝牙模式**：
  1. Dongle 必须通电（USB 供电口或充电宝）。
  2. 键盘按 `BT 1`~`BT 5` 切换 Dongle 的蓝牙连接通道。
  3. 电脑/iPad 搜索到的蓝牙设备是 Dongle，不是键盘本体。

## 六、开放问题 / 实施前必须确认

- [ ] `zmk,kscan-mock` 的具体 binding 属性（`columns`/`rows`/`events`）需对照实际使用的 ZMK 固件版本（`west.yml` 锁定的 revision）核实，不同版本字段可能不同。
- [ ] 确认当前 ZMK 版本是否原生支持 dongle 架构下的 `ZMK_SPLIT_BLE_ROLE_CENTRAL`（近期 ZMK 已有官方 [Dongle 支持 PR](https://github.com/zmkfirmware/zmk/pull/1861) 合并进展，建议实施前查阅官方文档，可能有更规范的 `ZMK_KEYBOARD` / dongle 专用配置方式，无需手搓 mock_kscan）。
- [ ] 是否需要给 Dongle 分配独立的 `zmk,physical-layout` 或仅需最小化 identity（作为纯粹的 BLE central + USB HID bridge）。
- [ ] BLE-01 / BLE-02（见 [plan.md 设计约束](../plan.md#设计约束)）是否需要同步应用到 `lily58_dongle.conf`（坏引脚主控是否也是克隆板，是否有时钟漂移风险）。
- [ ] 与现有双模固件的共存策略：是否保留旧 `lily58_left.conf` 双模逻辑作为可切换分支（如通过 `cmake-args -DZMK_CONFIG` 类似 Silakka54 的做法），避免每次改造都要完全替换现有主力配置。
