# SuperMini NRF52840 键盘引脚映射文档

本文档整理了基于 **SuperMini NRF52840** 控制器的 **Sweep (Cradio)** 及其衍生键盘（如 **Dolphin1**）的详尽引脚对应关系。

由于该方案采用直连触发（Direct Pin）而非传统的矩阵扫描（Matrix），每个按键都独立占用一个 GPIO 引脚。

---

## 核心参数参考

### 1. 电源与系统引脚
* **VCC (3.3V)**: 引脚 22。主要为系统供电。
* **GND**: 引脚 4, 5, 24。所有按键的 Pin 2 统一连接至此。
* **RAW**: 引脚 25。电池正极输入。
* **RESET**: 引脚 23。

### 2. 外部 VCC 切断控制 (Power Management)
根据 SuperMini 的文档：
* **P0.13**: 当该引脚拉低（Low）时，VCC 输出会被关闭。这对于节省 RGB 灯或外部传感器的待机功耗非常有用。

### 3. ZMK 配置建议
在编写 `keyboard.overlay` 或 `keymap` 文件时，建议使用 **Arduino Label (D0-D21)** 或 **GPIO Label (P0.xx/P1.xx)**。

**示例代码片段 (Direct Config):**
```dts
input_processors {
    // 举例：SWITCH10 对应的引脚在 ZMK 中应定义为:
    // &gpio0 6 (对应 P0.06 / D1)
};
```

---

## 原版 Sweep (Cradio) 键盘引脚映射表

本表列出了每个按键（SWITCH）与 MCU 引脚的对应关系，包含 **物理编号**、**逻辑 GPIO（nRF52840 内部编号）** 以及 **Arduino 常用别名**。

| 按键编号 | 按键位置 | MCU 物理引脚号 | nRF52840 内部引脚 | Arduino/ZMK 别名 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SWITCH1** | Q | 12 | **P0.11** | **D7** | **注意: 在 Dolphin1 中被替换** |
| **SWITCH2** | W | 18 | **P1.15** | **D18** | |
| **SWITCH3** | E | 19 | **P1.13** | **D15** | |
| **SWITCH4** | R | 20 | **P0.02** | **D19** | |
| **SWITCH5** | T | 21 | **P0.29** | **D20** | 原理图中 SW5 连线有交叉，请检查 |
| **SWITCH6** | A | 17 | **P0.31** | **D21** | |
| **SWITCH7** | S | 16 | **P0.09** | **D10** | |
| **SWITCH8** | D | 15 | **P0.10** | **D16** | |
| **SWITCH9** | F | 14 | **P1.11** | **D14** | |
| **SWITCH10**| G | 2 | **P0.06** | **D1** | |
| **SWITCH11**| Z | 6 | **P0.17** | **D2** | |
| **SWITCH12**| X | 7 | **P0.20** | **D3** | |
| **SWITCH13**| C | 8 | **P0.22** | **D4** | |
| **SWITCH14**| V | 9 | **P0.24** | **D5** | |
| **SWITCH15**| B | 10 | **P1.00** | **D6** | **注意: 在 Dolphin1 中被替换** |
| **SWITCH16**| Thumb 1 | 11 | **P1.04** | **D8** | |
| **SWITCH17**| Thumb 2 | 13 | **P1.06** | **D9** | |
| **SWITCH18**| Thumb 3 | 3 | **P0.08** | **D0** | Cradio 36键版本第三个拇指 |

---

## Dolphin1 定制分支的差异说明

在 **Dolphin1** 键盘设计中（34键布局），SW 编号与网络标号采用了 1:1 映射（未打乱）。这导致引脚的分配与原版 Cradio 有所区别，最核心的差异在于 **Q 和 B 键的互换**：

- **Q 键 (SW1)**: 原版 Cradio 使用的是 `D7`，但在 Dolphin1 中使用的是 `D6`（内部引脚 P1.00）。
- **B 键 (SW15)**: 原版 Cradio 使用的是 `D6`，但在 Dolphin1 中使用的是 `D7`（内部引脚 P0.11）。

*(注：引脚 6 和 7 的位置在 input-gpios 中与原版互换。)*

### Dolphin1 的 ZMK `input-gpios` 参考：
```dts
        input-gpios
        // 第一排 (Top Row: Q W E R T)
        = <&pro_micro  6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW1  → Q
        , <&pro_micro 18 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW2  → W
        , <&pro_micro 19 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW3  → E
        , <&pro_micro 20 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW4  → R
        , <&pro_micro 21 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW5  → T

        // 第二排 (Middle Row: A S D F G)
        , <&pro_micro 15 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW6  → A
        , <&pro_micro 14 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW7  → S
        , <&pro_micro 16 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW8  → D
        , <&pro_micro 10 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW9  → F
        , <&pro_micro  1 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW10 → G

        // 第三排 (Bottom Row: Z X C V B)
        , <&pro_micro  2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW11 → Z
        , <&pro_micro  3 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW12 → X
        , <&pro_micro  4 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW13 → C
        , <&pro_micro  5 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW14 → V
        , <&pro_micro  7 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW15 → B

        // 拇指键簇 (Thumb Cluster)
        , <&pro_micro  8 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW16 → Thumb 1
        , <&pro_micro  9 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)> // SW17 → Thumb 2
        ;
```

---

## 硬件检查提醒
1. **SW5 连线**: 在原版原理图中，`SWITCH5` 的引脚 1 可能同时连接了引脚 21 和引脚 24 (GND)。这会导致该按键永久触发或短路。请务必在 PCB 设计中确认 `SWITCH5` 的引脚 1 仅连接到 `D21`。
2. **镜像设计**: Sweep/Dolphin 键盘通常采用 **Reversible Footprint（可翻转焊盘）**。由于 PCB 是正反盲插设计，左手和右手的引脚映射可能会因为 PCB 的翻转而完全相反。强烈建议焊接完成后，使用测试固件逐个排查按键响应。
