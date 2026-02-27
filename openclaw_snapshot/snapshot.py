#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞💾 OpenClaw Snapshot - 备份虾
智能备份与恢复工具 - 留住每一个重要时刻
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import subprocess

# 颜色代码 🎨
class Colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

# ASCII 艺术
LOGO = f"""
{Colors.PINK}
    💾 ╔═══════════════════════════════════════╗
      ║     OpenClaw Snapshot                 ║
      ║        备份虾 - 留住每一刻            ║
      ╚═══════════════════════════════════════╝
{Colors.END}
"""

SNAPSHOT_ART = f"""
{Colors.CYAN}
       📸 ✨
      ╱    ╲
     │  💾  │   ← 咔嚓！已保存
      ╲    ╱
       ────
    配置已安全备份
{Colors.END}
"""

RESTORE_ART = f"""
{Colors.GREEN}
    ⏰ ✨ 🦞 ✨ ⏰
    
    时光倒流成功！
    一切恢复到熟悉的样子
    
    🦞 "欢迎回来~"
{Colors.END}
"""

class SnapshotManager:
    """快照管理器"""
    
    def __init__(self):
        self.home = Path.home()
        self.openclaw_dir = self.home / ".openclaw"
        self.snapshot_dir = self.home / ".openclaw_snapshots"
        self.ensure_snapshot_dir()
    
    def ensure_snapshot_dir(self):
        """确保快照目录存在"""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def get_openclaw_paths(self) -> List[Path]:
        """获取所有 OpenClaw 相关路径"""
        paths = []
        
        if self.openclaw_dir.exists():
            paths.append(self.openclaw_dir)
        
        # 其他可能的位置
        other_paths = [
            self.home / ".config" / "openclaw",
            self.home / "Library" / "Application Support" / "openclaw",
        ]
        
        for p in other_paths:
            if p.exists():
                paths.append(p)
        
        return paths
    
    def calculate_checksum(self, path: Path) -> str:
        """计算目录/文件的校验和"""
        if path.is_file():
            return hashlib.md5(path.read_bytes()).hexdigest()[:8]
        
        # 目录：计算所有文件的组合校验和
        hashes = []
        for f in sorted(path.rglob("*")):
            if f.is_file():
                try:
                    hashes.append(hashlib.md5(f.read_bytes()).hexdigest())
                except:
                    pass
        
        return hashlib.md5("".join(hashes).encode()).hexdigest()[:8] if hashes else "empty"
    
    def create_snapshot(self, name: str, description: str = "", snapshot_type: str = "custom") -> Dict:
        """创建快照"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"{name}_{timestamp}"
        snapshot_path = self.snapshot_dir / snapshot_id
        
        # 创建快照目录
        snapshot_path.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        paths = self.get_openclaw_paths()
        for src in paths:
            dst = snapshot_path / src.name
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        # 创建元数据
        metadata = {
            "id": snapshot_id,
            "name": name,
            "description": description,
            "type": snapshot_type,  # fresh, current, custom
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "paths": [str(p) for p in paths],
            "size": self.get_directory_size(snapshot_path),
            "checksum": self.calculate_checksum(snapshot_path)
        }
        
        # 保存元数据
        meta_file = snapshot_path / "snapshot.json"
        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def get_directory_size(self, path: Path) -> int:
        """获取目录大小（字节）"""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total
    
    def list_snapshots(self) -> List[Dict]:
        """列出所有快照"""
        snapshots = []
        
        for snapshot_dir in sorted(self.snapshot_dir.iterdir()):
            if snapshot_dir.is_dir():
                meta_file = snapshot_dir / "snapshot.json"
                if meta_file.exists():
                    with open(meta_file) as f:
                        metadata = json.load(f)
                        snapshots.append(metadata)
        
        return sorted(snapshots, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_snapshot(self, snapshot_id: str, force: bool = False) -> bool:
        """恢复快照"""
        snapshot_path = self.snapshot_dir / snapshot_id
        
        if not snapshot_path.exists():
            print_error(f"快照不存在: {snapshot_id}")
            return False
        
        # 读取元数据
        meta_file = snapshot_path / "snapshot.json"
        with open(meta_file) as f:
            metadata = json.load(f)
        
        # 检查 OpenClaw 是否正在运行
        try:
            result = subprocess.run(["pgrep", "-f", "openclaw"], capture_output=True)
            if result.returncode == 0:
                print_warning("OpenClaw 正在运行，建议先停止")
                if not force:
                    confirm = input("是否停止并继续恢复? (yes/no): ").strip()
                    if confirm != "yes":
                        return False
                    subprocess.run(["pkill", "-f", "openclaw"], check=False)
                    import time
                    time.sleep(2)
        except:
            pass
        
        # 备份当前状态（以防万一）
        if self.openclaw_dir.exists():
            backup_name = f"auto_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print_info(f"自动备份当前状态: {backup_name}")
            self.create_snapshot(backup_name, "自动备份：恢复前的状态", "auto")
        
        # 删除当前配置
        if self.openclaw_dir.exists():
            shutil.rmtree(self.openclaw_dir)
        
        # 恢复快照
        for item in snapshot_path.iterdir():
            if item.name == "snapshot.json":
                continue
            
            dst = self.openclaw_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        
        print_success(f"已恢复到快照: {metadata['name']}")
        print(RESTORE_ART)
        return True
    
    def export_snapshot(self, snapshot_id: str, export_path: str) -> bool:
        """导出快照为压缩包"""
        snapshot_path = self.snapshot_dir / snapshot_id
        
        if not snapshot_path.exists():
            print_error(f"快照不存在: {snapshot_id}")
            return False
        
        export_file = Path(export_path)
        if export_file.is_dir():
            export_file = export_file / f"{snapshot_id}.tar.gz"
        
        # 创建 tar.gz
        with tarfile.open(export_file, "w:gz") as tar:
            tar.add(snapshot_path, arcname=snapshot_id)
        
        print_success(f"已导出到: {export_file}")
        return True
    
    def import_snapshot(self, import_path: str) -> bool:
        """导入快照"""
        import_file = Path(import_path)
        
        if not import_file.exists():
            print_error(f"文件不存在: {import_path}")
            return False
        
        # 解压
        with tarfile.open(import_file, "r:gz") as tar:
            # 获取快照 ID
            snapshot_id = tar.getnames()[0].split('/')[0]
            snapshot_path = self.snapshot_dir / snapshot_id
            
            if snapshot_path.exists():
                print_warning(f"快照 {snapshot_id} 已存在，将覆盖")
                shutil.rmtree(snapshot_path)
            
            tar.extractall(self.snapshot_dir)
        
        print_success(f"已导入快照: {snapshot_id}")
        return True
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除快照"""
        snapshot_path = self.snapshot_dir / snapshot_id
        
        if not snapshot_path.exists():
            print_error(f"快照不存在: {snapshot_id}")
            return False
        
        shutil.rmtree(snapshot_path)
        print_success(f"已删除快照: {snapshot_id}")
        return True
    
    def compare_snapshots(self, snapshot_id1: str, snapshot_id2: str) -> Dict:
        """对比两个快照"""
        # 简化版：比较元数据
        path1 = self.snapshot_dir / snapshot_id1 / "snapshot.json"
        path2 = self.snapshot_dir / snapshot_id2 / "snapshot.json"
        
        if not path1.exists() or not path2.exists():
            print_error("快照不存在")
            return {}
        
        with open(path1) as f:
            meta1 = json.load(f)
        with open(path2) as f:
            meta2 = json.load(f)
        
        diff = {
            "name1": meta1["name"],
            "name2": meta2["name"],
            "time_diff": meta1["timestamp"] != meta2["timestamp"],
            "size_diff": meta1["size"] - meta2["size"],
            "checksum_diff": meta1["checksum"] != meta2["checksum"]
        }
        
        return diff


# CLI 界面函数
def print_logo():
    print(LOGO)

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def cmd_create(args):
    """创建快照命令"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.CYAN}📸 创建新快照{Colors.END}\n")
    
    # 交互式输入
    name = input(f"{Colors.BOLD}快照名称 (如: fresh_install): {Colors.END}").strip()
    if not name:
        name = f"snapshot_{datetime.now().strftime('%Y%m%d')}"
    
    description = input(f"{Colors.BOLD}描述 (可选): {Colors.END}").strip()
    
    print(f"\n{Colors.CYAN}快照类型:{Colors.END}")
    print("1. 🌱 纯净安装 (刚装好的状态)")
    print("2. 🏠 当前状态 (包含所有配置)")
    print("3. ⚙️  自定义")
    
    type_choice = input(f"{Colors.BOLD}选择 (1/2/3): {Colors.END}").strip()
    snapshot_type = {"1": "fresh", "2": "current", "3": "custom"}.get(type_choice, "custom")
    
    # 创建快照
    print(f"\n{Colors.YELLOW}正在创建快照...{Colors.END}")
    metadata = manager.create_snapshot(name, description, snapshot_type)
    
    print(SNAPSHOT_ART)
    print_success(f"快照创建成功!")
    print(f"  📛 名称: {metadata['name']}")
    print(f"  🆔 ID: {metadata['id']}")
    print(f"  📅 时间: {metadata['created_at']}")
    print(f"  💾 大小: {format_size(metadata['size'])}")
    print(f"  🔖 类型: {metadata['type']}")

def cmd_list(args):
    """列出快照命令"""
    manager = SnapshotManager()
    snapshots = manager.list_snapshots()
    
    print_logo()
    print(f"{Colors.CYAN}📋 快照列表 ({len(snapshots)} 个){Colors.END}\n")
    
    if not snapshots:
        print_info("还没有快照，使用 'create' 命令创建一个吧！")
        return
    
    # 打印表格
    print(f"{'ID':<25} {'名称':<20} {'类型':<12} {'大小':<10} {'时间':<20}")
    print("-" * 95)
    
    for snap in snapshots:
        snap_type_icon = {
            "fresh": "🌱",
            "current": "🏠",
            "custom": "⚙️",
            "auto": "🤖"
        }.get(snap['type'], "📦")
        
        print(f"{snap['id'][:24]:<25} {snap['name'][:19]:<20} {snap_type_icon} {snap['type']:<10} {format_size(snap['size']):<10} {snap['created_at'][:19]:<20}")
    
    print(f"\n{Colors.DIM}提示: 使用 'restore <ID>' 恢复快照{Colors.END}")

def cmd_restore(args):
    """恢复快照命令"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.CYAN}⏰ 恢复快照{Colors.END}\n")
    
    # 列出快照供选择
    snapshots = manager.list_snapshots()
    if not snapshots:
        print_error("没有可用的快照")
        return
    
    print("可用快照:")
    for i, snap in enumerate(snapshots[:10], 1):
        print(f"{i}. {snap['name']} ({snap['id'][:20]}...)")
    
    choice = input(f"\n{Colors.BOLD}输入要恢复的快照 ID (或序号): {Colors.END}").strip()
    
    # 支持序号选择
    if choice.isdigit() and 1 <= int(choice) <= len(snapshots):
        snapshot_id = snapshots[int(choice) - 1]['id']
    else:
        snapshot_id = choice
    
    # 确认
    print_warning("⚠️  这将覆盖当前的 OpenClaw 配置！")
    confirm = input(f"{Colors.BOLD}确认恢复? 输入 'RESTORE' 继续: {Colors.END}").strip()
    
    if confirm != "RESTORE":
        print_info("已取消")
        return
    
    # 执行恢复
    if manager.restore_snapshot(snapshot_id):
        print_success("恢复完成！建议运行 'openclaw gateway restart' 启动服务")

def cmd_export(args):
    """导出快照命令"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.CYAN}📦 导出快照{Colors.END}\n")
    
    # 列出可用快照
    snapshots = manager.list_snapshots()
    if not snapshots:
        print_error("没有可用的快照")
        return
    
    print("可用快照:")
    for i, snap in enumerate(snapshots[:10], 1):
        print(f"{i}. {snap['name']} ({snap['id'][:20]}...)")
    
    choice = input(f"\n{Colors.BOLD}输入要导出的快照 ID (或序号 1-{len(snapshots)}): {Colors.END}").strip()
    
    # 支持序号选择
    if choice.isdigit() and 1 <= int(choice) <= len(snapshots):
        snapshot_id = snapshots[int(choice) - 1]['id']
    else:
        snapshot_id = choice
    
    export_path = input(f"{Colors.BOLD}导出路径 (默认 ~/Desktop): {Colors.END}").strip() or str(Path.home() / "Desktop")
    
    if manager.export_snapshot(snapshot_id, export_path):
        print_success(f"快照已导出，可以复制到其他机器导入！")

def cmd_import(args):
    """导入快照命令"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.CYAN}📥 导入快照{Colors.END}\n")
    
    import_path = input(f"{Colors.BOLD}快照文件路径 (.tar.gz): {Colors.END}").strip()
    
    if manager.import_snapshot(import_path):
        print_success("快照已导入，可以使用 'restore' 命令恢复！")

def cmd_delete(args):
    """删除快照命令"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.RED}🗑️  删除快照{Colors.END}\n")
    
    # 列出可用快照
    snapshots = manager.list_snapshots()
    if not snapshots:
        print_error("没有可用的快照")
        return
    
    print("可用快照:")
    for i, snap in enumerate(snapshots[:10], 1):
        print(f"{i}. {snap['name']} ({snap['id'][:20]}...)")
    
    choice = input(f"\n{Colors.BOLD}输入要删除的快照 ID (或序号 1-{len(snapshots)}): {Colors.END}").strip()
    
    # 支持序号选择
    if choice.isdigit() and 1 <= int(choice) <= len(snapshots):
        snapshot_id = snapshots[int(choice) - 1]['id']
    else:
        snapshot_id = choice
    
    print_warning("⚠️  删除后无法恢复！")
    confirm = input(f"{Colors.BOLD}确认删除? 输入 'DELETE' 继续: {Colors.END}").strip()
    
    if confirm == "DELETE":
        manager.delete_snapshot(snapshot_id)
    else:
        print_info("已取消")

def cmd_auto_fresh(args):
    """自动创建纯净安装快照"""
    manager = SnapshotManager()
    
    print_logo()
    print(f"{Colors.CYAN}🌱 创建纯净安装快照{Colors.END}\n")
    
    # 检查是否是刚安装的状态
    print_info("这会保存当前 OpenClaw 配置作为'纯净安装'基准")
    confirm = input(f"{Colors.BOLD}继续? (yes/no): {Colors.END}").strip()
    
    if confirm == "yes":
        metadata = manager.create_snapshot(
            "fresh_install",
            "纯净安装状态 - 刚完成初始配置",
            "fresh"
        )
        print(SNAPSHOT_ART)
        print_success("纯净安装快照已创建！")
        print(f"以后重装后可以恢复这个状态")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_logo()
        print(f"{Colors.CYAN}🦞💾 OpenClaw Snapshot - 备份虾{Colors.END}\n")
        print("用法: openclaw-snapshot <命令> [选项]")
        print()
        print("命令:")
        print("  create          📸 创建新快照")
        print("  list            📋 列出所有快照")
        print("  restore         ⏰ 恢复快照")
        print("  export          📦 导出快照")
        print("  import          📥 导入快照")
        print("  delete          🗑️  删除快照")
        print("  fresh           🌱 创建纯净安装快照")
        print()
        print("简写: ocs = openclaw-snapshot")
        print()
        print("示例:")
        print("  ocs create                    # 交互式创建")
        print("  ocs list                      # 查看所有快照")
        print("  ocs restore fresh_install_xxx # 恢复指定快照")
        print("  ocs export fresh_install_xxx  # 导出到文件")
        sys.exit(0)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "restore": cmd_restore,
        "export": cmd_export,
        "import": cmd_import,
        "delete": cmd_delete,
        "fresh": cmd_auto_fresh,
    }
    
    if command in commands:
        try:
            commands[command](args)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 已取消{Colors.END}")
        except Exception as e:
            print_error(f"发生错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print_error(f"未知命令: {command}")
        print_info("使用 'openclaw-snapshot' 查看帮助")

if __name__ == "__main__":
    main()
