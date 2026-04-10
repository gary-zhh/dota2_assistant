"""工具模块"""
from .coordinate_mapper import CoordinateMapper, get_coordinate_mapper
from .platform_compat import (
    get_platform, is_windows, is_linux, is_macos,
    get_dota2_path, get_gsi_config_path,
    clear_screen, set_console_encoding
)

__all__ = [
    'CoordinateMapper', 'get_coordinate_mapper',
    'get_platform', 'is_windows', 'is_linux', 'is_macos',
    'get_dota2_path', 'get_gsi_config_path',
    'clear_screen', 'set_console_encoding'
]
