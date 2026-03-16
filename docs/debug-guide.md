# ZMK 固件底层调试与断联排查指南

本文档记录了基于 Zephyr RTOS 的 ZMK 固件的高阶调试方法。主要用于排查诸如“打字中途蓝牙突然断频、死锁”或“内存栈溢出”等常规参数调整无法定位的深层问题。

## 1. 原理说明

ZMK 底层拥有完善的实时操作系统日志系统（Log）。当键盘发生死机、重启、蓝牙发射队列阻塞或被主机主动断开时，底层堆栈都会向串行接口（Serial）输出错误原因如 `Panic`、`TX queue is full` 或 HCI 错误码。

通过**连接 USB 数据线查看日志，同时强制键盘通过蓝牙发送数据**，并在此状态下进行高频操作（例如狂按 Combo、鼠标层连压），即可完美复现并捕获断联崩溃瞬间的真实错误栈。

## 2. 预备工作：开启 USB 日志输出支持

开启 USB 调试需要修改您的 `.conf` 和构建脚本。**警告：日常使用务必关闭日志功能，否则未接入抓取工具时可能导致键盘耗电暴增或假死卡顿！**

### 2.1 修改 `.conf` 配置文件
在主控配置文件（如 `lily58.conf` 或 `lily58_left.conf`）中开启日志：

```ini
# 开启 ZMK USB 日志输出功能 (调试抓Log必备，日常请设为 =n 或删除)
CONFIG_ZMK_USB_LOGGING=y

# (可选) 若需要极详尽的蓝牙通讯底层记录（可能降低键盘处理速度），可附加开启：
# CONFIG_BT_DEBUG_LOG=y 
```

同时，为排查是否因“堆栈溢出”或“蓝牙发送死锁”导致的断联，强烈建议同时扩大内存栈与 L2CAP 的 TX 缓冲区大小：
```ini
CONFIG_BT_L2CAP_TX_BUF_COUNT=8
CONFIG_BT_L2CAP_TX_MTU=65
CONFIG_MAIN_STACK_SIZE=2048
CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=2048
```

### 2.2 修改 `build.yaml` 编译脚本
针对需要抓取日志的主控板，在其构建阶段注入 `zmk-usb-logging` snippet：

```yaml
  - board: nice_nano//zmk
    shield: lily58_left
    snippet: zmk-usb-logging
    artifact-name: lily58_left
```

### 2.3 修改 `keymap` 键位 (必备条件)
因为要在插线状态下测试**蓝牙**断联，必须配置强制输出通道切换热键。
请在键位图中包含输出头文件，并在某一层级配置 `&out OUT_BLE` 功能：

```c
#include <dt-bindings/zmk/outputs.h>

// 在您的配置层放上它们：
// &out OUT_BLE  (强制信号走蓝牙，USB仅供电及输出Log)
// &out OUT_USB  (强制信号走线材)
```

**以上修改提交并自动构建完成后，请将新的固件刷入您的主控键盘中。**

---

## 3. 情景复现与抓取步骤 (Windows 环境)

无需安装额外复杂工具，只需通过网页即可完成抓取：

1. **连接硬件**：用 USB 数据线将刷好调试固件的键盘直接插到电脑上。
2. **确认串口 (COM口)**：右键开始菜单 -> `设备管理器` -> 展开 `端口 (COM 和 LPT)`。找到名为 `USB 串行设备 (COMx)` 或 `ZMK CDC ACM (COMx)` 的端口号。
3. **打开串口监控台**：
   - 使用 Chrome 或 Edge 浏览器打开 [Google Chrome Labs Web Serial 工具](https://googlechromelabs.github.io/serial-terminal/)。
   - 点击 `Connect` 按钮，选择您的串口（COMx），由于是 USB CDC ACM，波特率通常默认 `115200` 即可，点击连接。
   - 此时随便按两下普通按键，终端应滚动出现 `[inf] <zmk:...` 的日志信息。
4. **触发情景 (核心操作)**：
   - 按下前面第二步中配置的 **`&out OUT_BLE`** 宏按键，强制让键盘打出的字只通过蓝牙发送给电脑。
   - 此时，在保证终端正在实时滚动日志的情况下，**开始疯狂地、高频地复现您遇到的问题操作**（如狂按鼠标层或大量触发组合键）。
5. **捕获异常**：当键盘突然断联、无反应或卡死的一瞬间，立即停止敲击，去串口监控页面查看终端里最后输出的几十行日志。

---

## 4. 断联/死锁日志分析指南

拿到崩溃瞬间的最后一段 Log 后，寻找以下关键词直接“对症下药”：

### 类型 A: 内存栈溢出与硬断言崩溃 (Software Crash)
* **表现与日志**：终端爆发大量错误栈，如 `*** HARD FAULT ***`、`Kernel Panic` 或 `ASSERTION FAILED`，紧接着通常伴随重新输出 `Booting Zephyr OS...`（说明键盘自行重启了）。
* **原因**：触发了 ZMK 的底层防崩溃保护。通常是因为高频的操作（如快速滚动鼠标、瞬间触发大量宏和组合键）撑爆了当前协程或系统工作队列的内存分配（Stack Overflow）。
* **对策**：继续扩大 `.conf` 中的 `CONFIG_MAIN_STACK_SIZE` 与 `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE` 参数，或者检讨鼠标层的上报频率机制。

### 类型 B: 发送队列堵塞锁死 (TX Buffer Full)
* **表现与日志**：不断滚动 `[wrn] bt_l2cap: No available buffers`，然后变成 `Failed to send data over BLE`，导致打字无反应。
* **原因**：键盘端生成蓝牙数据包的速度（如鼠标高速滑行时发出的位移包）远大于 Windows 端接收和应答的速度。发送缓冲队列（TX Buffer）全部打满。
* **对策**：增加 `.conf` 中发送缓冲区容量：`CONFIG_BT_L2CAP_TX_BUF_COUNT=8` （或更高）及 `CONFIG_BT_L2CAP_TX_MTU=65`。

### 类型 C: 底层连接被意外断开 (HCI Disconnect Reason)
* **表现与日志**：由于协议底层的断联产生了一条事件通知，包含 16 进制 HCI code，例如：`[inf] bt_hci_core: Disconnected: xx:xx:xx:xx:xx:xx (reason 0x13)` 或 `reason 0x08`。
* **原因速查**：
  * **`0x08` (Connection Timeout)**：通讯超时。键盘发送了数据却没有按时收到 Win11 主机的 ACK 响应。常见于 2.4G 极其严重的干扰，或者电脑网卡突然打盹进入省电休眠。
  * **`0x13` (Remote User Terminated Connection)**：对方主动终止连接！**这意味着 100% 是 Windows 操作系统向键盘发送了踢出指令**。绝不是键盘和固件的问题，应立刻去排查 Win11 的电源选项、蓝牙网卡高级驱动设置是否开启了“允许计算机关闭此设备以节约电源”或相关省电策略冲突。
  * **`0x3D` (Connection Terminated due to MIC Failure)**：这表明安全验证失败。通常出现在刷机、回滚固件或跨主机设备配对时，安全密钥表和 MAC 地址未达成共识，需要两端彻彻底底删除配对履历（或刷 Reset）后洗牌重连。

通过这种“降维” Debug 手段，您永远不需要再为了摸不准蓝牙断联的病因而盲目前后修改参数了。

---

## 5. 真实案例存档：频发 0x22 (LMP Response Timeout)

**问题描述**：在打字中断联问题的排查中，抓取到了 `0x22` 错误码导致的断联，并发现该问题在重刷官方固件后变得尤为严重。

**深度解析（破案啦！）**：
*   **现象**：重刷 ZMK 官方固件后连接变得极不稳定。
*   **根因**：**硬件时钟漂移 (Clock Drift)**。官方 `nice!nano` 固件默认寻找板载的 **32.768 kHz 外部石英晶振**。然而，许多国产克隆板（如 SuperMini NRF52840）处于成本或体积考虑**阉割了这颗晶振**。
*   **后果**：由于没有高精度时钟，蓝牙同步信号会随着时间产生微小偏移。当偏移超出蓝牙协议容忍范围时，主机（电脑）就会判定响应超时，抛出 `reason 0x22 (LMP Response Timeout)`。

**终极修复策略 ("核心解法")**：
不再单纯通过放宽超时限制来“治标”，而是直接针对克隆板进行底层时钟校准：

1. **强制开启内部时钟**：在 `.conf` 文件中添加 `CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y`。这将强制芯片使用内部 RC 振荡器模拟时钟，彻底解决由于缺少外部晶振导致的同步失败。
2. **清理冗余配置**：开启 RC 时钟后，蓝牙稳定性将回归正常。此时建议删除或注释掉之前为了缓解症状而添加的 `CONFIG_BT_PERIPHERAL_PREF_TIMEOUT` 等参数，以恢复最佳的响应速度。
3. **保留物理排查**：天线增益（主机背后的蓝牙天线）依然是信号强度的物理保障，需确保已正确安装。

