# 蓝牙断连排查与解决方案

> 适用于 Dolphin1 / Lily58 / bgkeeb，所有使用 nice!nano 克隆板 (SuperMini) 的 ZMK 键盘。

## 症状

- 打字间隔几分钟后整个键盘断连
- 按键后需 5-10 秒才恢复
- 每小时断几次，高频发生
- 深度睡眠（15 分钟）尚未触发就已断连

## 根因

**Windows 蓝牙电源管理**主动掐断空闲 BLE 连接，不是键盘端问题。

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

> ⚠️ 当前处于调试状态，Dolphin1 已开启 `CONFIG_ZMK_USB_LOGGING=y`

```conf
# --- 蓝牙核心 ---
CONFIG_BT_CTLR_PHY_2M=n                     # 禁用 2M PHY，强制 1M（兼容性优先）
CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=y       # 合并开关：含 CONN + SEC
CONFIG_ZMK_BLE_PASSKEY_ENTRY=y               # 安全配对码
CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y         # 强制内部 RC 振荡器（SuperMini 必需）

# --- Windows 11 ---
CONFIG_BT_GATT_ENFORCE_SUBSCRIPTION=n        # 绕过 GATT 电量断联 Bug

# --- 发射功率（已注释，观察中）---
# CONFIG_BT_CTLR_TX_PWR_PLUS_8=y             # 如 split 通信不稳可取消注释

# --- 连接参数 ---
CONFIG_BT_PERIPHERAL_PREF_TIMEOUT=800        # 超时 8 秒，容忍 RC 漂移
# PREF_MIN/MAX_INT 已删除                     # 保证 RC 时钟宽容度

# --- 缓冲区与栈 ---
CONFIG_BT_L2CAP_TX_BUF_COUNT=8
CONFIG_BT_L2CAP_TX_MTU=65
CONFIG_MAIN_STACK_SIZE=2048
CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=2048
CONFIG_ZMK_BEHAVIORS_QUEUE_SIZE=512
```

## 回退方案

如果 `EXPERIMENTAL_FEATURES=y` 导致 Win11 断流 0x22 timeout：

```conf
# 1. 关闭合并开关
CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=n

# 2. 单独启用子功能
CONFIG_ZMK_BLE_EXPERIMENTAL_CONN=y
CONFIG_ZMK_BLE_EXPERIMENTAL_SEC=y
```

如果降低发射功率后 split 通信不稳：

```conf
# 取消注释，恢复 +8 dBm 发射功率
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y
```

### 彻底重置配对

- 刷入 ZMK Settings Reset 固件到两半键盘
- 主机上忘记所有键盘配对
- 重新刷正常固件并配对

## 实验记录

### 2026-04-09：蓝牙配置精简实验

**假设**：合并 `EXPERIMENTAL_FEATURES=y` 并降低发射功率，可以在不损失稳定性的前提下简化配置、降低功耗。

**变更摘要**：

| 参数 | 变更前 | 变更后 | 理由 |
|------|--------|--------|------|
| `EXPERIMENTAL_CONN` | `y` | 删除 | 被 `EXPERIMENTAL_FEATURES` 包含 |
| `EXPERIMENTAL_SEC` | `y` | 删除 | 被 `EXPERIMENTAL_FEATURES` 包含 |
| `EXPERIMENTAL_FEATURES` | `n` | `y` | 合并开关，简化管理 |
| `TX_PWR_PLUS_8` | `y` | 注释掉 | 测试默认功率下电压稳定性 |
| `PREF_MIN_INT` | `12` | 删除 | 保证 RC 时钟宽容度 |
| `PREF_MAX_INT` | `24` | 删除 | 同上 |
| `BATTERY_REPORT_INTERVAL` | `60` | 删除 | 改用 ZMK 默认间隔 |

**影响范围**：Dolphin1 / Lily58 / bgkeeb 三个键盘同步变更

**结果**：❌ 失败

- `EXPERIMENTAL_FEATURES=y` 仍然导致连接不稳定，与预期不符
- 电池电量 100%（满电），"电压不稳"的假设不成立，开启 USB logging 继续排查

---

## 社区参考

- [ZMK 官方蓝牙故障排除](https://zmk.dev/docs/troubleshooting/connection-issues)
- [ZMK 蓝牙配置文档](https://zmk.dev/docs/config/bluetooth)
- r/ErgoMechKeyboards 社区讨论
