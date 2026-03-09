# 固件部署指南

## 构建

1. 推送代码到 GitHub（`test/callum-osm` 或 `main` 分支）
2. GitHub Actions 自动编译，产出两个 uf2 文件：
   - `lily58_left-nice_nano_v2-zmk.uf2`
   - `lily58_right-nice_nano_v2-zmk.uf2`
3. 从 Actions 的 Artifacts 下载 zip，解压得到 uf2 文件

## 刷入

逐个刷入左手和右手，顺序无所谓。

1. USB 线连接目标半边到电脑
2. **双击 Reset 按钮**（间隔要快，<500ms），进入 Bootloader
3. 电脑弹出 `NICENANO` U 盘
4. 用 `copy` 命令将对应的 uf2 文件复制到 U 盘：
   ```cmd
   copy "D:\path\to\lily58_left-nice_nano_v2-zmk.uf2" E:\
   ```
   （E 盘替换为实际 NICENANO 盘符）
5. 复制完成后 nice!nano 自动重启，U 盘消失，刷入成功
6. 拔掉，换另一半重复步骤 1-5

## 注意事项

- left 刷 left，right 刷 right，别搞反
- 用 `copy` 命令复制，不要拖拽
- U 盘里原有的 `CURRENT.UF2` 是 Bootloader 自动生成的备份，不用管
- 刷固件不需要电池，USB 供电即可
- 如果 U 盘没弹出来，说明没进入 Bootloader，重新双击 Reset
- 刷完后如果蓝牙连不上，按 Sys 层的 `BT_CLR` 清除配对重连
