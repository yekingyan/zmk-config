# ZMK 分体键盘蓝牙断连问题 — 专家咨询

## 问题概述

我有一个自制的 34 键分体蓝牙机械键盘（Dolphin1），基于 Ferris Sweep（Cradio）设计，使用 ZMK 固件。键盘在使用过程中频繁出现**右手（Peripheral）与左手（Central）之间的蓝牙连接断开**，并且断连发生时**左手也会与电脑断开或假死约 12 秒**。已尝试多种配置方案和 settings reset，问题持续存在。
我使用上的体感是，如果左手连usb，则没有感知到右手会断连的情况，一直使用正常。但如果左手用蓝牙就会有问题。没测试配置时，前5个小时都是正常的，后面怎么试都不对，一种硬件坏了的感觉。但我有很多款这个硬盘，也总不能硬件都坏了吧

## 硬件信息

### 键盘

- **名称**：Dolphin1
- **布局**：34 键，分体式（左手 17 键 + 右手 17 键）
- **PCB**：基于 Ferris Sweep (Cradio) 的自制 PCB
- **PCB 与原版 Cradio 的区别**：SW 编号与网络标号 1:1 映射（未打乱），导致 pin 6/7 位置与原版互换。通过自定义 shield 设备树（`dolphin1.dtsi`）解决了映射问题
- **按键扫描方式**：直连 GPIO（`zmk,kscan-gpio-direct`），非矩阵扫描
- **左右手通信**：蓝牙（BLE）

### 主控板

- **型号**：SuperMini（nice!nano v2 克隆板）× 2
- **芯片**：nRF52840（Nordic Semiconductor）
- **已知硬件问题**：SuperMini 克隆板存在批次差异，部分板子的板载 32kHz 外部晶振质量差或虚焊

### 主机

- **操作系统**：Windows 11
- **蓝牙适配器**：外接 USB 蓝牙适配器
- **适配器电源管理**：已关闭"允许计算机关闭此设备以节约电源"
- **USB 选择性暂停**：已禁用
- **适配器插在 USB 2.0 口**（避免 3.0 口的 2.4GHz 干扰）

### 电池

- **电量状态**：100%（满电），已排除电压不足的可能性

## 固件信息

- **固件框架**：ZMK（基于 Zephyr RTOS）
- **ZMK 版本**：跟踪 `zmkfirmware/zmk` 的 `main` 分支
- **构建方式**：GitHub Actions 云端构建
- **west.yml**：

```yaml
manifest:
  defaults:
    revision: main
  remotes:
    - name: zmkfirmware
      url-base: https://github.com/zmkfirmware
  projects:
    - name: zmk
      remote: zmkfirmware
      import: app/west.yml
  self:
    path: config
```

## 问题现象

### 现象一：右手断连

- **时机**：正在频繁打字的过程中（非空闲休眠），右手突然没有响应
- **频率**：不固定，有时几分钟一次，有时可能十几分钟甚至更长
- **表现**：右手按键完全无反应

### 现象二：左手"殉情"

- 右手断连时，**左手也同时与电脑断开或假死**
- 左手假死持续约 **12 秒**，之后自动恢复
- 恢复后左右手重新建立连接，键盘暂时恢复正常

### 日志证据

通过 `CONFIG_ZMK_USB_LOGGING=y` + `snippet: zmk-usb-logging` 在 USB 串口捕获到以下关键日志：

```
Disconnected from [MAC地址] (public) (reason 0x22)
split_central_disconnected: Disconnected: [MAC地址] (public) (reason 34)
Failed to release peripheral slot (-22)
All devices are connected, scanning is unnecessary
```

之后约 12 秒，日志出现：

```
security changed... level 4
```

表明右手通过最高级别安全重连请求打破了左手的"假死"状态。

### 日志解读

- `reason 0x22`（十进制 34）= BLE Link Layer Response Timeout，即链路层响应超时
- `-22` = Zephyr 的 `-EINVAL`，槽位清理函数返回参数无效
- `All devices are connected` = 左手误判右手仍然在线，拒绝启动扫描重连
- 这指向 ZMK 源码 `app/src/split/bluetooth/central.c` 中的分体主控状态机缺陷

## 当前配置文件

```ini
# dolphin1.conf（当前实际生效的完整配置）

CONFIG_ZMK_KEYBOARD_NAME="Dolphin1"

# --- USB 日志 ---
CONFIG_ZMK_USB_LOGGING=n

# --- 蓝牙 ---
CONFIG_BT_CTLR_PHY_2M=n                     # 禁用 2M PHY，强制 1M
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y              # +8 dBm 发射功率
CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=n       # 关闭实验性功能
CONFIG_ZMK_BLE_PASSKEY_ENTRY=y               # 安全配对码
CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y         # 强制内部 RC 振荡器

# --- Windows 11 ---
CONFIG_BT_GATT_ENFORCE_SUBSCRIPTION=n        # 绕过 GATT 断联 Bug

# --- 电源与休眠 ---
CONFIG_ZMK_BATTERY_REPORTING=y
CONFIG_ZMK_SLEEP=y
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000         # 15 分钟深度休眠

# --- 缓冲区与栈 ---
CONFIG_BT_L2CAP_TX_BUF_COUNT=8
CONFIG_BT_L2CAP_TX_MTU=65
CONFIG_MAIN_STACK_SIZE=2048
CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=2048
CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512

# --- 连接参数 ---
CONFIG_BT_PERIPHERAL_PREF_TIMEOUT=800        # 8 秒超时

# --- 鼠标模拟 ---
# CONFIG_ZMK_POINTING=y                      # 排查期间临时关闭
```

## 设备树（Shield 定义）

```dts
/* dolphin1.dtsi — 34 键直连 GPIO */
kscan0: kscan {
    compatible = "zmk,kscan-gpio-direct";
    wakeup-source;
    input-gpios
    = <&pro_micro  6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW1
    , <&pro_micro 18 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW2
    , <&pro_micro 19 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW3
    /* ... 共 17 个 GPIO 引脚 ... */
    ;
};
```

## 已尝试的方案及结果

### 实验四（2026-04-10）：应用专家综合防断连方案

**背景观察**：左手连 USB 时，右手**从不断连**；左手拔掉 USB 仅用蓝牙时，发生一系列断连和假死。这表明问题极大概率出在无线电抢占（Radio Scheduling）和休眠时钟漂移上。

**操作**：
1. **时钟漂移修复**：`RC=y` + 声明 `500PPM` 精度（防漂移漏接兜底）
2. **解决无线电抢占**：拉开 PC 通信间隔（`MIN_INT=12`, `MAX_INT=24`），避开 7.5ms 主副通信冲突
3. **应对突发流量**：扩容底层蓝牙 `RX_STACK_SIZE=2048`
4. **开启重试机制**：重新开启 `EXPERIMENTAL_FEATURES=y`

**结果**：❌ 失败 — 断连问题依然存在。

### 实验五（2026-04-10）：开启 2M PHY 与全面扩容（专家方案 E）

**操作**：
1. **释放无线电资源**：开启 `CONFIG_BT_CTLR_PHY_2M=y`，大幅减少频段占用时间，解决无线电调度冲突。
2. **状态机深层扩容**：将 `SYSTEM_WORKQUEUE`、`MAIN`、`RX` 线程堆栈全部扩容至 `4096`，并增加 `BLE_THREAD_STACK_SIZE=1024`，防止 OOM 引发槽位清理失败（-22 错误）。

**结果**：❌ 失败 — 开启 2M PHY 后信号雪崩，连配对连上建立都变得极其困难。这就证明了硬件层面的天线信号极差，根本无法支撑 2M 带宽对信噪比的要求。

### 实验六（2026-04-10）：回退 1M PHY 并开启日志验证物理极限（退守方案 F）

**操作**：
1. **退守 1M PHY**：`CONFIG_BT_CTLR_PHY_2M=n`，放弃速度换取通信存活。
2. **开启日志观测**：重新打开 `USB_LOGGING=y`，用以监视如果 1M 下断连发生，是否仍然是原先的死锁报错。
3. **保留防御**：保留扩充的队列栈和防漂移配置。

**结果**：待测试。

---

### 已测试的所有配置组合汇总

以下是在排查过程中测试过的所有配置组合：

| 配置项 | 方案 C | 方案 D | 方案 E | 方案 F（当前） |
|--------|--------|--------|--------|----------------|
| `BT_CTLR_PHY_2M` | `n` | `n` | `y` | `n`（退守） |
| `BLE_EXPERIMENTAL_FEATURES` | `n` | `y` | `y` | `y` |
| `CLOCK_CONTROL_NRF_K32SRC_500PPM` | — | `y` | `y` | `y` |
| `ZMK_USB_LOGGING` | `n` | `n` | `n` | `y` |
| `BT_PERIPHERAL_PREF_MIN_INT` | — | `12` | `12` | `12` |
| `BT_PERIPHERAL_PREF_MAX_INT` | — | `24` | `24` | `24` |
| `BT_RX_STACK_SIZE` | — | `2048` | `4096`| `4096` |
| `WORKQUEUE/MAIN_STACK_SIZE` | `2048` | `2048` | `4096`| `4096` |
| `BLE_THREAD_STACK_SIZE` | — | — | `1024`| `1024` |
| 结果 | ❌ | ❌ | ❌ (连不上) | 待测试 |

## 排除了的可能原因

- **电池电压不足**：电量 100%，满充状态
- **正常休眠断连**：问题发生在频繁打字中途，非空闲状态
- **Windows 电源管理**：已关闭所有相关选项
- **配对缓存污染**：已执行 `settings_reset.uf2` 双边重置 + 电脑端删除旧设备
- **实验性蓝牙与 RC 时钟冲突**：已关闭 `EXPERIMENTAL_FEATURES`，问题仍存在
- **USB Logging 线程死锁**：已关闭，问题仍存在
- **Pointing 高频上报**：已关闭，问题仍存在

## 约束条件

- 主控板是 **SuperMini 克隆板**（非原版 nice!nano），无法更换为原版来对比测试
- PCB 是**自制的**，天线区域的净空处理和走线质量无法保证
- 使用的是 **ZMK main 分支**，无法确定具体的 commit 版本
- 需要**保留蓝牙分体功能**（不能改为有线连接左右手）
- 键盘日常需要使用 **Pointing（鼠标模拟）功能**

## 期望

- 找到导致右手断连（0x22）和左手假死（-22 槽位死锁）的根因
- 获得能够稳定运行的配置方案，使键盘在日常打字和鼠标模拟场景下不出现断连
- 理解这个问题是否属于 ZMK 固件层面的缺陷、硬件层面的限制、还是配置上仍有优化空间

## 附件说明

以下是项目中的相关文件，如需进一步分析可以查看：

- `config/dolphin1.conf` — 键盘配置文件
- `boards/shields/dolphin1/dolphin1.dtsi` — 设备树定义（引脚映射）
- `boards/shields/dolphin1/dolphin1_left.overlay` — 左手 overlay
- `boards/shields/dolphin1/dolphin1_right.overlay` — 右手 overlay
- `config/dolphin1.keymap` — 按键映射
- `config/west.yml` — ZMK west manifest
- `docs/bluetooth-troubleshooting.md` — 完整排查记录
