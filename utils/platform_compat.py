"""
平台兼容性工具
处理Windows/Linux/macOS的差异
"""
import os
import sys
import platform


def get_platform():
    """获取当前平台"""
    return platform.system().lower()


def is_windows():
    """是否为Windows系统"""
    return get_platform() == 'windows'


def is_linux():
    """是否为Linux系统"""
    return get_platform() == 'linux'


def is_macos():
    """是否为macOS系统"""
    return get_platform() == 'darwin'


def get_dota2_path():
    """
    获取Dota 2安装路径

    Returns:
        str: Dota 2安装路径，如果未找到返回None
    """
    if is_windows():
        # Windows常见路径
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta",
            r"C:\Program Files\Steam\steamapps\common\dota 2 beta",
            r"D:\Steam\steamapps\common\dota 2 beta",
            r"D:\SteamLibrary\steamapps\common\dota 2 beta",
            r"E:\Steam\steamapps\common\dota 2 beta",
        ]
    elif is_macos():
        # macOS路径
        home = os.path.expanduser("~")
        possible_paths = [
            f"{home}/Library/Application Support/Steam/steamapps/common/dota 2 beta",
        ]
    else:  # Linux
        # Linux路径
        home = os.path.expanduser("~")
        possible_paths = [
            f"{home}/.steam/steam/steamapps/common/dota 2 beta",
            f"{home}/.local/share/Steam/steamapps/common/dota 2 beta",
        ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_gsi_config_path():
    """
    获取GSI配置文件路径

    Returns:
        str: GSI配置目录路径
    """
    dota2_path = get_dota2_path()
    if not dota2_path:
        return None

    return os.path.join(dota2_path, "game", "dota", "cfg", "gamestate_integration")


def normalize_path(path):
    """
    规范化路径（处理Windows/Unix差异）

    Args:
        path: 原始路径

    Returns:
        str: 规范化后的路径
    """
    return os.path.normpath(path)


def clear_screen():
    """清屏（跨平台）"""
    if is_windows():
        os.system('cls')
    else:
        os.system('clear')


def set_console_encoding():
    """设置控制台编码为UTF-8（主要针对Windows）"""
    if is_windows():
        try:
            # Windows设置UTF-8编码
            os.system('chcp 65001 >nul')
            # Python 3.7+
            if sys.version_info >= (3, 7):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not set UTF-8 encoding: {e}")


def get_default_host():
    """
    获取默认的GSI服务器地址

    Windows上使用127.0.0.1更可靠
    """
    if is_windows():
        return "127.0.0.1"
    else:
        return "0.0.0.0"


def check_admin_rights():
    """
    检查是否有管理员权限（Windows）

    Returns:
        bool: 是否有管理员权限
    """
    if not is_windows():
        return True  # Unix系统不需要检查

    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def get_python_executable():
    """
    获取Python可执行文件路径

    Returns:
        str: python或python3
    """
    if is_windows():
        return "python"
    else:
        return "python3"


if __name__ == "__main__":
    # 测试平台检测
    print("=== Platform Detection Test ===\n")

    print(f"Platform: {get_platform()}")
    print(f"Is Windows: {is_windows()}")
    print(f"Is Linux: {is_linux()}")
    print(f"Is macOS: {is_macos()}")
    print()

    print(f"Python executable: {get_python_executable()}")
    print(f"Default GSI host: {get_default_host()}")
    print()

    dota2_path = get_dota2_path()
    if dota2_path:
        print(f"✓ Dota 2 found: {dota2_path}")
        gsi_path = get_gsi_config_path()
        print(f"✓ GSI config path: {gsi_path}")
    else:
        print("✗ Dota 2 not found")

    print()

    if is_windows():
        print(f"Admin rights: {check_admin_rights()}")

    print("\n✅ Platform compatibility test completed!")
