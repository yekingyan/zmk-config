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

### 左手"殉情"重启（Kernel Panic / HardFault）

当右手断连同时导致**左手也与电脑断开**，说明左手 nRF52840 发生了内核崩溃或看门狗强制重启。

**嫌疑人清单**：

| 嫌疑人 | 配置项 | 崩溃机制 |
|--------|--------|----------|
| USB Logging 死锁 | `CONFIG_ZMK_USB_LOGGING=y` | 非 USB 供电时日志队列填满 → 线程死锁 |
| 实验性蓝牙 + RC 时钟 | `CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=y` | RC 500ppm 漂移 + 激进连接间隔 → 时序断言失败 |
| Pointing 队列溢出 | `CONFIG_ZMK_POINTING=y` | 高频鼠标报告 + 丢包重传 → 击穿队列 / OOM |
| 发射功率不足 | `TX_PWR_PLUS_8` 被注释 | 自制 PCB 天线差 → 持续丢包 → 协议栈异常 |

## 排查决策树

> **先判断断连时机：**
> - **放着没用**时断开 → 正常休眠，无需处理
> - **右手断，左手不断** → 晶振/供电/信号问题
> - **右手断，左手也断（殉情）** → 左手内核崩溃，按嫌疑人清单排查

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

**结果**：❌ 失败

- 右手断连同时导致左手也与电脑断开（"殉情"现象）
- 电池满电排除了电压不稳假设
- 日志确认 `reason 0x22` Split 链路层超时

**根因分析**：左手发生了 Kernel Panic / HardFault，触发看门狗重启。嫌疑人：
- USB Logging 在非 USB 供电时导致死锁
- `EXPERIMENTAL_FEATURES=y` 与 RC 时钟精度冲突导致时序断言失败
- 发射功率不足加剧了丢包和协议栈异常

### 实验二（2026-04-10）：控制变量排除崩溃源

**假设**：`EXPERIMENTAL_FEATURES=y` 与 RC 时钟冲突 + 发射功率不足是崩溃主因。保留 USB logging 作为观测手段。

**变更摘要**：

| 参数 | 变更前 | 变更后 | 理由 |
|------|--------|--------|------|
| `EXPERIMENTAL_FEATURES` | `y` | `n` | 排除时序冲突（主要嫌疑人） |
| `TX_PWR_PLUS_8` | 注释 | `y` | 恢复信号强度 |
| `USB_LOGGING` | `y` | `y`（保留） | 作为观测手段，如果仍崩则反证为其元凶 |

**影响范围**：Dolphin1 / Lily58 / bgkeeb 三个键盘同步变更

**⚠️ 刷固件后必须操作**：

- 给左右手都刷 `settings_reset.uf2`（清除旧配对缓存）
- 在电脑端删除旧的蓝牙设备
- 重新刷正常固件，让左右手纯净配对

**判定逻辑**：

- ✅ 稳定 → 元凶确认为 `EXPERIMENTAL_FEATURES` 或 `TX_PWR`，USB logging 无罪
- ❌ 仍崩 → USB logging 就是死锁元凶（日志里应能看到崩溃前的最后输出）

**如果基线稳定，后续逐一恢复**：

- [ ] Step 1: 恢复 `EXPERIMENTAL_CONN=y` + `EXPERIMENTAL_SEC=y`（单独子开关）
- [ ] Step 2: 恢复 `EXPERIMENTAL_FEATURES=y`（验证是否与 RC 冲突）
- [ ] Step 3: 注释掉 `TX_PWR_PLUS_8`（验证是否是信号问题）

**结果**：待测试

---

## 社区参考

- [ZMK 官方蓝牙故障排除](https://zmk.dev/docs/troubleshooting/connection-issues)
- [ZMK 蓝牙配置文档](https://zmk.dev/docs/config/bluetooth)
- r/ErgoMechKeyboards 社区讨论
