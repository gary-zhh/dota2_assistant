"""
游戏状态数据结构
解析GSI提供的JSON数据并提供便捷的访问接口
"""
from dataclasses import dataclass
from typing import Optional, Dict, List, Any


@dataclass
class Vector3:
    """3D坐标"""
    x: float
    y: float
    z: float = 0.0


@dataclass
class HeroState:
    """英雄状态"""
    name: str
    level: int
    health: int
    max_health: int
    mana: int
    max_mana: int
    position: Vector3
    gold: int
    gold_reliable: int
    gold_unreliable: int
    xp: int
    alive: bool
    respawn_seconds: int
    buyback_cost: int
    buyback_cooldown: int

    # 状态效果
    is_stunned: bool = False
    is_silenced: bool = False
    is_disarmed: bool = False
    is_rooted: bool = False
    is_invisible: bool = False

    # 移动
    move_speed: int = 0


@dataclass
class AbilityState:
    """技能状态"""
    name: str
    level: int
    can_cast: bool
    cooldown: float
    passive: bool
    ultimate: bool


@dataclass
class ItemState:
    """物品状态"""
    name: str
    can_cast: bool
    cooldown: float
    charges: int
    passive: bool


@dataclass
class GameState:
    """完整游戏状态"""
    # 基础信息
    game_time: float  # 游戏时间（秒）
    clock_time: float  # 游戏内时钟时间（秒）
    daytime: bool

    # 玩家英雄
    hero: Optional[HeroState] = None

    # 技能和物品
    abilities: List[AbilityState] = None
    items: List[ItemState] = None

    # 地图信息
    map_name: str = ""

    # 队伍信息
    team_radiant_score: int = 0
    team_dire_score: int = 0

    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []
        if self.items is None:
            self.items = []

    @classmethod
    def from_gsi_data(cls, data: Dict[str, Any]) -> 'GameState':
        """从GSI JSON数据创建GameState对象"""
        game_state = cls(
            game_time=0.0,
            clock_time=0.0,
            daytime=True
        )

        # 解析地图信息
        if 'map' in data:
            map_data = data['map']
            game_state.map_name = map_data.get('name', '')
            game_state.game_time = map_data.get('game_time', 0.0)
            game_state.clock_time = map_data.get('clock_time', 0.0)
            game_state.daytime = map_data.get('daytime', True)

            # 队伍分数
            if 'radiant_score' in map_data:
                game_state.team_radiant_score = map_data['radiant_score']
            if 'dire_score' in map_data:
                game_state.team_dire_score = map_data['dire_score']

        # 解析英雄信息
        if 'hero' in data:
            hero_data = data['hero']
            game_state.hero = HeroState(
                name=hero_data.get('name', ''),
                level=hero_data.get('level', 1),
                health=hero_data.get('health', 0),
                max_health=hero_data.get('max_health', 1),
                mana=hero_data.get('mana', 0),
                max_mana=hero_data.get('max_mana', 1),
                position=Vector3(
                    x=hero_data.get('x', 0),
                    y=hero_data.get('y', 0),
                    z=hero_data.get('z', 0)
                ) if 'x' in hero_data else Vector3(0, 0, 0),
                gold=hero_data.get('gold', 0),
                gold_reliable=hero_data.get('gold_reliable', 0),
                gold_unreliable=hero_data.get('gold_unreliable', 0),
                xp=hero_data.get('xp', 0),
                alive=hero_data.get('alive', True),
                respawn_seconds=hero_data.get('respawn_seconds', 0),
                buyback_cost=hero_data.get('buyback_cost', 0),
                buyback_cooldown=hero_data.get('buyback_cooldown', 0),
                is_stunned=hero_data.get('stunned', False),
                is_silenced=hero_data.get('silenced', False),
                is_disarmed=hero_data.get('disarmed', False),
                is_rooted=hero_data.get('rooted', False),
                is_invisible=hero_data.get('smoked', False),
                move_speed=hero_data.get('move_speed', 0)
            )

        # 解析技能
        if 'abilities' in data:
            abilities_data = data['abilities']
            for ability_name, ability_info in abilities_data.items():
                if isinstance(ability_info, dict):
                    game_state.abilities.append(AbilityState(
                        name=ability_name,
                        level=ability_info.get('level', 0),
                        can_cast=ability_info.get('can_cast', False),
                        cooldown=ability_info.get('cooldown', 0.0),
                        passive=ability_info.get('passive', False),
                        ultimate=ability_info.get('ultimate', False)
                    ))

        # 解析物品
        if 'items' in data:
            items_data = data['items']
            for slot, item_info in items_data.items():
                if isinstance(item_info, dict) and item_info.get('name'):
                    game_state.items.append(ItemState(
                        name=item_info.get('name', ''),
                        can_cast=item_info.get('can_cast', False),
                        cooldown=item_info.get('cooldown', 0.0),
                        charges=item_info.get('charges', 0),
                        passive=item_info.get('passive', False)
                    ))

        return game_state

    def get_ability_by_name(self, name: str) -> Optional[AbilityState]:
        """根据名称获取技能"""
        for ability in self.abilities:
            if ability.name == name:
                return ability
        return None

    def get_item_by_name(self, name: str) -> Optional[ItemState]:
        """根据名称获取物品"""
        for item in self.items:
            if item.name == name:
                return item
        return None

    def is_hero_alive(self) -> bool:
        """英雄是否存活"""
        return self.hero is not None and self.hero.alive

    def get_health_percentage(self) -> float:
        """获取血量百分比"""
        if self.hero and self.hero.max_health > 0:
            return self.hero.health / self.hero.max_health
        return 0.0

    def get_mana_percentage(self) -> float:
        """获取蓝量百分比"""
        if self.hero and self.hero.max_mana > 0:
            return self.hero.mana / self.hero.max_mana
        return 0.0

    def get_game_phase(self) -> str:
        """判断游戏阶段"""
        if self.game_time < 600:  # 10分钟前
            return "laning"
        elif self.game_time < 1800:  # 30分钟前
            return "mid_game"
        else:
            return "late_game"
