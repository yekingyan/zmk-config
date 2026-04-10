# 蓝牙断连排查与解决方案

> 适用于 Dolphin1 / Lily58 / bgkeeb，所有使用 nice!nano 克隆板 (SuperMini) 的 ZMK 键盘。

## 核心报错

```
Disconnected from [MAC] (public) (reason 0x22)
split_central_disconnected: Disconnected: [MAC] (public) (reason 34)
```

- `reason 34`（0x22）= **Link Layer Response Timeout（链路层响应超时）**
- 含义：左手主控板（Central）呼叫右手副板（Peripheral），副板未在规定时间内回应，主控判定连接丢失并主动断开

## 原因排查（按概率从高到低）

### 正常休眠（不是 Bug）

- **触发场景**：键盘几分钟没有输入，副板自动深度休眠，蓝牙广播停止，主控报超时断连
- **解决**：无需处理，按下右手任意键等 1~2 秒即可自动唤醒重连

### SuperMini 晶振硬件缺陷（重点排查）

- **触发场景**：满电状态下**正在频繁打字中途**，右手突然毫无征兆断连
- **原因**：SuperMini 存在批次问题，板载外部 32kHz 晶振质量差或虚焊，晶振跑飞导致蓝牙时钟失同步
- **解决**：弃用外部晶振，强制使用芯片内部 RC 振荡器：
  ```conf
  CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y
  ```

### 供电异常（物理掉电）

- **触发场景**：拿起/移动/震动键盘时右手断连
- **原因**：电池没电、电池线松动、电源开关虚焊，瞬间掉电导致超时
- **解决**：
  - 检查右手电池电压
  - 插 USB 供电测试：插线不断 + 电池断 → 重焊电池线或电源开关

### 蓝牙配对缓存污染

- **触发场景**：频繁修改 keymap / 多次刷固件后，左右手连不上
- **原因**：频繁刷写导致主控和副板保存的配对密钥不一致
- **解决**：终极重置
  - 给左右两块板子都刷入 `settings_reset.uf2`
  - 主机上忘记所有键盘配对
  - 重新刷入正常固件并配对

### 左手"殉情"假死（Split 状态机死锁 — 已确认根因）

当右手断连同时导致**左手也与电脑断开/假死 12 秒**，根因是 ZMK split 主控状态机的已知缺陷。

**源码级根因链**（`app/src/split/bluetooth/central.c`）：

```
右手 0x22 超时断开
  → 左手调用槽位清理函数
    → 返回 -22 (EINVAL)，槽位状态异常，清理失败
      → 左手误判"右手还在线"，打印 "All devices are connected, scanning is unnecessary"
        → 拒绝扫描重连，假死 12 秒
          → 直到右手触发 Level 4 安全重连请求才恢复
```

**触发条件（叠加因素）**：

| 因素 | 机制 |
|------|------|
| **脏配对数据** | 刷固件不擦除 Flash 中的配对记忆，错乱数据导致 -22 |
| **USB Logging** | 未接 USB 时日志队列填满 → 线程死锁 → 错过蓝牙回应窗口 |
| **Pointing** | 高频坐标上报加剧线程拥堵 → 加速触发 0x22 |
| **EXPERIMENTAL_FEATURES** | 与 RC 时钟冲突，激进时序导致断言失败 |

## 排查决策树

> **先判断断连时机：**
> - **放着没用**时断开 → 正常休眠，无需处理
> - **右手断，左手不断** → 晶振/供电/信号问题
> - **右手断，左手假死 12 秒** → Split 状态机 -22 死锁（见上方根因链）

## 主机端修复（Windows）

### 关闭蓝牙适配器电源管理（关键）

- 设备管理器 → 蓝牙 → 外置适配器 → 属性 → 电源管理
- **取消勾选** "允许计算机关闭此设备以节约电源"
- 同样处理适配器所在的 USB Root Hub

### 关闭 USB 选择性暂停

- `powercfg.cpl` → 当前计划 → 更改高级电源设置
- USB 设置 → USB 选择性暂停设置 → **已禁用**

### 适配器插入位置

- **不要**插 USB 3.0 口（蓝色口），USB 3.0 产生 2.4GHz 干扰
- 插 USB 2.0 口，或用延长线拉远离机箱

### 适配器选型

- ✅ 推荐：TP-Link UB500 / UB4A（Bluetooth 5.0）
- ❌ 避免：杂牌 Realtek 芯片适配器

## 键盘端配置（当前生效）

```conf
# --- 蓝牙核心 ---
CONFIG_BT_CTLR_PHY_2M=n                     # 禁用 2M PHY，强制 1M（兼容性优先）
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y              # +8 dBm 发射功率（自制 PCB 必需）
CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=n       # 关闭（与 RC 时钟冲突）
CONFIG_ZMK_BLE_PASSKEY_ENTRY=y               # 安全配对码
CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y         # 强制内部 RC 振荡器（SuperMini 必需）

# --- Windows 11 ---
CONFIG_BT_GATT_ENFORCE_SUBSCRIPTION=n        # 绕过 GATT 电量断联 Bug

# --- 线程负载优化 ---
CONFIG_ZMK_USB_LOGGING=n                     # 关闭（线程死锁触发源）
# CONFIG_ZMK_POINTING=y                      # 临时关闭（高频上报加剧拥堵）

# --- 连接参数 ---
CONFIG_BT_PERIPHERAL_PREF_TIMEOUT=800        # 超时 8 秒，容忍 RC 漂移

# --- 缓冲区与栈 ---
CONFIG_BT_L2CAP_TX_BUF_COUNT=8
CONFIG_BT_L2CAP_TX_MTU=65
CONFIG_MAIN_STACK_SIZE=2048
CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=2048
CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512
```

## 实验记录

### 实验一（2026-04-09）：蓝牙配置精简

**假设**：合并 `EXPERIMENTAL_FEATURES=y` 并降低发射功率，可以在不损失稳定性的前提下简化配置。

**变更摘要**：

| 参数 | 变更前 | 变更后 |
|------|--------|--------|
| `EXPERIMENTAL_CONN` | `y` | 删除 |
| `EXPERIMENTAL_SEC` | `y` | 删除 |
| `EXPERIMENTAL_FEATURES` | `n` | `y` |
| `TX_PWR_PLUS_8` | `y` | 注释掉 |
| `PREF_MIN/MAX_INT` | `12/24` | 删除 |
| `BATTERY_REPORT_INTERVAL` | `60` | 删除 |

**结果**：❌ 失败 — 右手断连导致左手殉情假死

### 实验二（2026-04-10）：控制变量排除崩溃源

**假设**：`EXPERIMENTAL_FEATURES` 与 RC 时钟冲突 + 发射功率不足是主因。

**变更**：`EXPERIMENTAL_FEATURES=n`，`TX_PWR_PLUS_8=y`，保留 USB logging

**结果**：❌ 失败

- 日志捕获到关键报错：`Failed to release peripheral slot (-22)` + `All devices are connected, scanning is unnecessary`
- 确认了根因：ZMK split 状态机 -22 槽位死锁（非 Kernel Panic）
- USB logging（线程资源争抢）和脏配对数据（Flash 未清除）是触发条件

### 实验三（2026-04-10）：清除触发条件 + Settings Reset

**假设**：关闭线程负载源（USB logging + Pointing）+ 彻底清洗 Flash 配对数据，可以避免触发 -22 死锁。

**变更摘要**：

| 参数 | 变更前 | 变更后 | 理由 |
|------|--------|--------|------|
| `USB_LOGGING` | `y` | `n` | 日志队列是线程死锁触发源 |
| `POINTING` | `y` | 注释掉 | 高频上报加剧线程拥堵 |
| `build.yaml` snippet | `zmk-usb-logging` | 移除 | 配合关闭 logging |

**⚠️ 刷固件后必须操作（终极双边重置）**：

- 给左右手都刷 `settings_reset.uf2`（格式化内部 Flash，清除脏配对数据）
- 在电脑端删除旧的 Dolphin1 蓝牙设备
- 重新刷入新固件，先开左手再开右手，纯净配对

**判定逻辑**：

- ✅ 稳定（打字不断连）→ 根因确认，进入 Step 1 恢复 Pointing
- ❌ 仍崩 → 问题在更深的固件层或硬件层

**稳定后逐步恢复**：

- [ ] Step 1: 恢复 `CONFIG_ZMK_POINTING=y`（验证 Pointing 是否独立触发问题）
- [ ] Step 2: 恢复 `EXPERIMENTAL_CONN=y` + `EXPERIMENTAL_SEC=y`
- [ ] Step 3: 恢复 `EXPERIMENTAL_FEATURES=y`

**结果**：❌ 失败 — 关闭 USB logging + Pointing + settings reset 后，断连仍然发生

### 实验四（2026-04-10）：应用专家综合防断连方案

**背景观察**：左手连 USB 时，右手**从不断连**；左手拔掉 USB 仅用蓝牙时，发生一系列断连和假死。这表明问题极大概率出在无线电抢占（Radio Scheduling）和休眠时钟漂移上。

**方案解析（四大优化支柱）**：

1. **补全 RC 时钟精度声明**
   - 之前只开启了 RC 振荡器（`RC=y`），但没有声明精度。Zephyr 默认以为时钟很准，分配了极窄的接收窗口，遇到 SuperMini 的廉价 RC，漂移一出直接漏接数据包。
   - 对策：必须加上 `CONFIG_CLOCK_CONTROL_NRF_K32SRC_500PPM=y`（保命选项）。

2. **解决无线电抢占（Radio Contention）**
   - 左手连 PC 蓝牙时，PC 的连接间隔如果也是默认的 7.5ms，会与左右手之间的 7.5ms 抢占同一块射频资源（同一时间只能干一件事）。插着 USB 时不需要用蓝牙连 PC，所以不抢占。
   - 对策：强制拉开与 PC 的通信间隔（`MIN_INT=12` / `MAX_INT=24`），让出时间片。

3. **应对高频突发流量（防拥塞）**
   - 当遇到网络波动时（特别是后续开启 Pointing 时），积压的包会瞬间撑爆默认仅为 3 的底层 TX 队列。
   - 对策：深层扩容。加上 `BT_CTLR_TX_BUFFERS=10` 和 `BT_RX_STACK_SIZE=2048`。

4. **利用新版 Zephyr 重试机制**
   - 新版 ZMK 的实验性特性中包含了优化过的重试逻辑。
   - 对策：重新开启 `EXPERIMENTAL_FEATURES=y`，配合 `500ppm` 时钟宽容度一起食用。

**判定逻辑**：
- ✅ 稳定运行（拔掉 USB 仅蓝牙模式下不再发生断连假死） → 问题彻底解决。
- ❌ 仍然断连（目前状态）→ 问题依然存在，由于 `BT_CTLR_TX_BUFFERS` 等在 Zephyr 4.1 已被废弃，导致编译失败被迫移除部分优化。此时继续断连，说明可能需要进一步排查 Zephyr 4.1 下的新配置策略。

**结果**：❌ 失败 — 即使加上了 `500ppm` 时钟精度和拉开连接间隔，纯蓝牙模式下仍然会断连。并且由于 ZMK 底层 Zephyr 4.1 的变动，部分底层缓冲队列优化被迫下线。

### 实验五（2026-04-10）：开启 2M PHY 与全面扩容（专家方案 E）

**背景**：专家指出，禁用 2M PHY 是一个反向优化。1M PHY 的传输距离稍远，但占用空中时间是 2M PHY 的两倍，会极大加剧左手芯片的调度拥堵。同时需进一步加强状态机缓冲区韧性以解决假死。

**方案解析（方案 E 优调）**：

1. **释放无线电资源**（核心修改）
   - 开启 `CONFIG_BT_CTLR_PHY_2M=y`，大幅减少每次传输的射频占用时间，缓解无线电调度冲突。
2. **增强队列与状态机抗压能力**
   - 升级多个关键工作线程的堆栈大小，以扛住突发流量，防止因 OOM 导致的槽位清理失败（-22 错误）：
     - `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=4096`
     - `CONFIG_MAIN_STACK_SIZE=4096`
     - `CONFIG_BT_RX_STACK_SIZE=4096`
     - `CONFIG_ZMK_BLE_THREAD_STACK_SIZE=1024`
3. **保持之前的防断连基础**
   - `RC=y` + `500ppm` 时钟
   - 发射功率 `+8dBm`
   - `EXPERIMENTAL_FEATURES=y`

**物理层警示**：如果此方案加 settings reset 依然导致高频断连，说明克隆板天线周边的 PCB 覆铜/走线造成了极度严重的信号衰减（导致容错率为零）。硬件上可能需要垫高主控或在天线下方留出 Keepout 禁布区。

**判定逻辑**：
- ✅ 稳定运行 → 调度拥堵及状态机死锁解除。
- ❌ 仍崩 → 准备迎接必须修改硬件（垫高主控或切断底盘连线）的现实。

**结果**：❌ 失败 — 开启 2M PHY 后，信号抗衰减能力断崖式下跌，连最基础的初始配对都极难完成。

### 实验六（2026-04-10）：回退 1M PHY 验证物理极限（退守方案 F）

**背景观察**：开启 2M PHY 后“很难连上”。这个现象反向证明了：克隆板的物理信号极差。在 2M 带宽下，由于对信噪比要求高，原本就因为 PCB 铺铜或烂天线导致微弱的信号直接雪崩，连握手包都大量丢失。这极大地佐证了之前 0x22 断连的真凶就是环境干扰导致的物理信号丢失，而非单纯配置问题。

**方案解析（方案 F 退守）**：

1. **退守 1M PHY**：`CONFIG_BT_CTLR_PHY_2M=n`。接受拥堵，先活下来。1M 的穿透力和信号容忍度天生比 2M 强 ~5dBm。
2. **重开 USB 日志看最后一眼**：`CONFIG_ZMK_USB_LOGGING=y`。既然已经基本确实是物理层干扰了，干脆把日志全开，一旦再断，看看死锁报错是不是和之前一模一样。
3. **保留深层防拥堵护甲**：保留了 4096 的 RX、MAIN 和 Workqueue 缓冲区栈大小。

**物理层警示（终极建议）**：如果回退 1M PHY 后，在纯蓝牙模式下依然会断：
> 找两根排针或者飞线，把左手的 SuperMini 主控**悬空垫高 1-2 厘米**（或者把天线那头掰出 PCB 边缘之外），远离电路板背面的金属铺铜。如果垫高之后断连消失，那就 100% 盲猜命中：**自制 PCB 设计时的天线净空（Keepout）没做好造成严重射频屏蔽，或者克隆板天线批次太差。**

**判定逻辑**：
- ✅ 恢复能连，且打字不断连 → 深层扩容生效，1M PHY 保命成功。
- ❌ 恢复能连，但打字仍会断连崩溃 → 软件已无能为力，必须开始物理垫高主控。

**结果**：待测试（等您出结果）。

---

## 社区参考

- [ZMK 官方蓝牙故障排除](https://zmk.dev/docs/troubleshooting/connection-issues)
- [ZMK 蓝牙配置文档](https://zmk.dev/docs/config/bluetooth)
- [ZMK Issue #2461（split 配对/握手相关）](https://github.com/zmkfirmware/zmk/issues/2461)
- r/ErgoMechKeyboards 社区讨论
