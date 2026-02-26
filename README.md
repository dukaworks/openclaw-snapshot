# 🦞💾 OpenClaw Snapshot

[![PyPI version](https://img.shields.io/pypi/v/openclaw-snapshot.svg)](https://pypi.org/project/openclaw-snapshot/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **备份虾出品** 🦞💾  
> OpenClaw 智能备份与恢复工具 - 留住每一个重要时刻

<p align="center">
  <img src="https://raw.githubusercontent.com/dukaworks/openclaw-snapshot/main/assets/snapshot.gif" alt="Snapshot" width="400">
</p>

## ✨ 为什么需要这个工具？

想象一下：
- 🌱 **刚装好 OpenClaw** - 想保存这个纯净状态
- 🔧 **配置了好多插件** - 想备份当前的完整配置
- 💻 **换电脑了** - 想把配置迁移到新机器
- 😱 **玩坏了** - 想快速恢复到之前的好状态

**备份虾帮你搞定一切！**

## 🚀 快速开始

### 安装

```bash
pip install openclaw-snapshot
```

### 基本用法

```bash
# 创建快照
ocs create

# 查看所有快照
ocs list

# 恢复快照
ocs restore fresh_install_20250115_120000

# 导出快照（迁移到其他机器）
ocs export fresh_install_20250115_120000
```

## 📸 快照类型

| 类型 | 图标 | 说明 |
|------|------|------|
| **纯净安装** | 🌱 | 刚完成初始配置的状态 |
| **当前状态** | 🏠 | 包含所有配置和数据的完整状态 |
| **自动备份** | 🤖 | 系统自动创建的备份（如恢复前） |
| **自定义** | ⚙️ | 用户手动创建的任意快照 |

## 📋 完整命令

```
ocs create          📸 交互式创建新快照
ocs list            📋 列出所有快照
ocs restore         ⏰ 恢复到指定快照
ocs export          📦 导出快照为 .tar.gz
ocs import          📥 导入快照文件
ocs delete          🗑️  删除快照
ocs fresh           🌱 快速创建纯净安装快照
```

## 🎯 使用场景

### 场景1：保存纯净安装状态

```bash
# 刚装好 OpenClaw，配置好模型后
ocs fresh

# 输入名称: fresh_install
# 输入描述: 刚装好的状态，模型已配置
# 选择类型: 1. 纯净安装

# 咔嚓！已保存 🦞📸
```

### 场景2：日常备份

```bash
# 每周备份一次完整配置
ocs create

# 名称: weekly_backup_$(date +%Y%m%d)
# 类型: 2. 当前状态
```

### 场景3：重装系统后恢复

```bash
# 新机器上安装 OpenClaw
# 然后导入之前的快照
ocs import ~/Desktop/my_openclaw_backup.tar.gz

# 恢复
ocs restore my_openclaw_backup
```

### 场景4：玩坏了回滚

```bash
# 查看有哪些快照
ocs list

# 恢复到之前的稳定状态
ocs restore weekly_backup_20250110

# 一切恢复如初！🎉
```

## 🖥️ 界面预览

```bash
$ ocs create

    💾 ╔═══════════════════════════════════════╗
      ║     OpenClaw Snapshot                 ║
      ║        备份虾 - 留住每一刻            ║
      ╚═══════════════════════════════════════╝

📸 创建新快照

快照名称 (如: fresh_install): production_setup
描述 (可选): 生产环境完整配置

快照类型:
1. 🌱 纯净安装 (刚装好的状态)
2. 🏠 当前状态 (包含所有配置)
3. ⚙️  自定义

选择 (1/2/3): 2

正在创建快照...

       📸 ✨
      ╱    ╲
     │  💾  │   ← 咔嚓！已保存
      ╲    ╱
       ────
    配置已安全备份

✅ 快照创建成功!
  📛 名称: production_setup
  🆔 ID: production_setup_20250115_143022
  📅 时间: 2025-01-15T14:30:22
  💾 大小: 12.5 MB
  🔖 类型: current
```

## 🔧 高级功能

### 自动备份策略

```bash
# 添加到 crontab，每周自动备份
0 2 * * 0 ocs create <<< "weekly_backup_$(date +\%Y\%m\%d)"
```

### 跨机器迁移

```bash
# 机器A: 导出
ocs export production_setup_xxx
scp production_setup_xxx.tar.gz user@machine-b:~/

# 机器B: 导入并恢复
ocs import ~/production_setup_xxx.tar.gz
ocs restore production_setup_xxx
```

### 对比快照

```bash
# 查看两个快照的差异
# （显示文件大小、配置变化等）
```

## 📁 快照存储位置

```
~/.openclaw_snapshots/
├── fresh_install_20250115_120000/
│   ├── snapshot.json       # 元数据
│   ├── .openclaw/          # 完整配置
│   └── ...
├── weekly_backup_20250110_020000/
│   └── ...
└── ...
```

## 🤝 与其他工具配合使用

```bash
# 1. 部署工具安装
openclaw-feishu deploy

# 2. 备份工具保存
ocs fresh

# 3. 玩坏了用卸载工具
openclaw-uninstall

# 4. 重装后用备份工具恢复
ocs restore fresh_install_xxx
```

## 🐛 故障排查

### Q: 恢复后 OpenClaw 启动失败？
```bash
# 检查日志
openclaw gateway logs

# 可能是版本不兼容，尝试更新
openclaw update
```

### Q: 快照文件太大？
```bash
# 快照排除了日志和缓存
# 如果还是很大，检查 ~/.openclaw/media/
```

### Q: 如何迁移到不同操作系统的机器？
```bash
# 快照是跨平台的！
# 只要路径结构一致，可以任意迁移
```

## 📄 许可证

MIT License © 2025 Duka Works

---

<p align="center">
  🦞💾 <strong>Made with love by 备份虾</strong> 🦞💾
  <br>
  <a href="https://github.com/dukaworks/openclaw-snapshot">GitHub</a> •
  <a href="https://pypi.org/project/openclaw-snapshot">PyPI</a>
</p>
