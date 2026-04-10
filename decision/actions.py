"""
动作定义
定义AI可以执行的所有动作类型
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple


class ActionType(Enum):
    """动作类型"""
    # 移动
    MOVE = "move"
    ATTACK_MOVE = "attack_move"

    # 攻击
    ATTACK_UNIT = "attack_unit"
    ATTACK_CREEP = "attack_creep"

    # 技能
    USE_ABILITY = "use_ability"
    USE_ABILITY_ON_UNIT = "use_ability_on_unit"
    USE_ABILITY_ON_LOCATION = "use_ability_on_location"

    # 物品
    USE_ITEM = "use_item"
    USE_ITEM_ON_UNIT = "use_item_on_unit"

    # 购买
    BUY_ITEM = "buy_item"

    # 其他
    RETREAT = "retreat"
    IDLE = "idle"
    DENY = "deny"


@dataclass
class Action:
    """动作"""
    action_type: ActionType
    priority: float = 0.0  # 优先级（0-1）

    # 目标
    target_location: Optional[Tuple[float, float]] = None  # 世界坐标
    target_unit: Optional[str] = None  # 单位名称

    # 技能/物品
    ability_name: Optional[str] = None
    item_name: Optional[str] = None

    # 原因（用于调试）
    reason: str = ""

    def __str__(self):
        if self.action_type == ActionType.MOVE:
            return f"Move to {self.target_location} (priority: {self.priority:.2f})"
        elif self.action_type == ActionType.ATTACK_UNIT:
            return f"Attack {self.target_unit} (priority: {self.priority:.2f})"
        elif self.action_type == ActionType.USE_ABILITY:
            return f"Use {self.ability_name} (priority: {self.priority:.2f})"
        elif self.action_type == ActionType.RETREAT:
            return f"Retreat to {self.target_location} (priority: {self.priority:.2f})"
        else:
            return f"{self.action_type.value} (priority: {self.priority:.2f})"


@dataclass
class Strategy:
    """战略决策"""
    goal: str  # 当前目标：laning, farming, ganking, pushing, teamfight, retreat
    target_lane: Optional[str] = None  # top, mid, bot
    aggression_level: float = 0.5  # 激进程度 0-1
    should_buy: bool = False
    recommended_items: list = None

    def __post_init__(self):
        if self.recommended_items is None:
            self.recommended_items = []
