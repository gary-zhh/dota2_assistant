"""
输入控制器
使用pynput模拟键盘和鼠标输入
"""
import time
import random
from typing import Tuple, Optional

try:
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Key, Controller as KeyboardController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not installed. Executor will not work.")

from decision import Action, ActionType
from utils import get_coordinate_mapper


class InputController:
    """输入控制器"""

    def __init__(self, config: dict):
        if not PYNPUT_AVAILABLE:
            raise ImportError("pynput is required for input control")

        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        self.config = config
        self.human_delay_min = config['executor']['human_delay_min']
        self.human_delay_max = config['executor']['human_delay_max']

        # 初始化坐标映射器
        self.mapper = get_coordinate_mapper(
            config['game']['resolution']['width'],
            config['game']['resolution']['height']
        )

        # 当前英雄位置（用于更新相机）
        self.hero_position = None

    def update_hero_position(self, position: Tuple[float, float]):
        """更新英雄位置（用于相机跟随）"""
        self.hero_position = position
        self.mapper.update_camera(position)

    def execute(self, action: Action, hero_position: Optional[Tuple[float, float]] = None):
        """执行动作"""
        try:
            # 更新英雄位置
            if hero_position:
                self.update_hero_position(hero_position)

            if action.action_type == ActionType.MOVE:
                self._move_to(action.target_location)
            elif action.action_type == ActionType.ATTACK_UNIT:
                self._attack_unit(action.target_unit)
            elif action.action_type == ActionType.ATTACK_CREEP:
                self._attack_move()
            elif action.action_type == ActionType.USE_ABILITY:
                self._use_ability(action.ability_name)
            elif action.action_type == ActionType.RETREAT:
                self._move_to(action.target_location)
            else:
                print(f"Action type {action.action_type} not implemented")

            # 添加人类化延迟
            self._human_delay()

        except Exception as e:
            print(f"Error executing action: {e}")

    def _move_to(self, location: Optional[Tuple[float, float]], use_minimap: bool = True):
        """
        移动到指定位置

        Args:
            location: 世界坐标
            use_minimap: 是否使用小地图（更可靠）
        """
        if not location:
            return

        # 使用坐标映射器转换
        screen_pos = self.mapper.world_to_screen(location, use_minimap=use_minimap)

        if not screen_pos:
            print(f"Warning: Position {location} is off screen")
            # 降级到小地图
            screen_pos = self.mapper.world_to_screen(location, use_minimap=True)

        # 右键点击
        self.mouse.position = screen_pos
        time.sleep(0.05)
        self.mouse.click(Button.right)

    def _attack_unit(self, unit_name: Optional[str]):
        """攻击单位"""
        # TODO: 需要计算机视觉来定位单位
        print(f"Attack unit not implemented: {unit_name}")

    def _attack_move(self):
        """攻击移动（A键）"""
        self.keyboard.press('a')
        time.sleep(0.05)
        self.keyboard.release('a')

        # 点击当前位置
        time.sleep(0.05)
        self.mouse.click(Button.left)

    def _use_ability(self, ability_name: Optional[str]):
        """使用技能"""
        if not ability_name:
            return

        # 简化：假设技能在QWER键
        # TODO: 需要技能槽位映射
        ability_keys = {
            0: 'q',
            1: 'w',
            2: 'e',
            3: 'r'
        }

        # 暂时使用Q键
        key = 'q'
        self.keyboard.press(key)
        time.sleep(0.05)
        self.keyboard.release(key)

    def _human_delay(self):
        """添加人类化的随机延迟"""
        delay = random.uniform(self.human_delay_min, self.human_delay_max)
        time.sleep(delay)

    def emergency_stop(self):
        """紧急停止"""
        # 释放所有按键
        pass
