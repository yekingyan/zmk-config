# 蓝牙断连排查与解决方案

> Silakka54 (Lily58 + nice!nano) 蓝牙连接稳定性优化记录。

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

## 键盘端配置（已到位）

```conf
# 实验性连接优化
CONFIG_ZMK_BLE_EXPERIMENTAL_CONN=y

# 发射功率拉满 (+8 dBm)
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y

# 禁用 2M PHY（Windows Realtek/Intel 兼容性）
CONFIG_BT_CTLR_PHY_2M=n

# 深度睡眠 15 分钟（与断连无关）
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000
```

## 备用方案（如主机端修复无效）

### 启用完整实验性蓝牙

```conf
# 替换 CONFIG_ZMK_BLE_EXPERIMENTAL_CONN=y 为：
CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES=y
```

包含 `EXPERIMENTAL_CONN`（连接优化）+ `EXPERIMENTAL_SEC`（安全连接 + 密钥覆写）。启用后需重新配对。

### 晶振故障排除（极端情况）

```conf
CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y
```

改用内部 RC 振荡器，功耗增加，仅在怀疑硬件缺陷时尝试。

### 彻底重置配对

- 刷入 ZMK Settings Reset 固件到两半键盘
- 主机上忘记所有键盘配对
- 重新刷正常固件并配对

## 社区参考

- [ZMK 官方蓝牙故障排除](https://zmk.dev/docs/troubleshooting/connection-issues)
- [ZMK 蓝牙配置文档](https://zmk.dev/docs/config/bluetooth)
- r/ErgoMechKeyboards 社区讨论
