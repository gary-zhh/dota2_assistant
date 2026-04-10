"""
英雄知识库
提供英雄技能、物品、玩法建议等信息
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AbilityInfo:
    """技能信息"""
    name: str
    slot: int
    ability_type: str  # no_target, unit_target, point_target, passive
    behavior: str  # aoe, enemy, ally, passive, channeled
    cast_range: int = 0
    radius: int = 0
    cooldown: List[float] = None
    mana_cost: List[int] = None
    weight: float = 0.5  # 使用优先级
    ultimate: bool = False
    description: str = ""

    def __post_init__(self):
        if self.cooldown is None:
            self.cooldown = []
        if self.mana_cost is None:
            self.mana_cost = []


@dataclass
class HeroInfo:
    """英雄信息"""
    hero_id: str  # npc_dota_hero_xxx
    name: str
    primary_attribute: str  # strength, agility, intelligence
    roles: List[str]
    abilities: Dict[str, AbilityInfo]
    item_builds: Dict[str, List[str]]  # pos_1, pos_3, etc.
    skill_build: List[int]
    playstyle: Dict[str, Any]


class HeroKnowledge:
    """英雄知识库"""

    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(__file__),
                "hero_knowledge",
                "heroes.json"
            )

        with open(data_path, 'r') as f:
            self.data = json.load(f)

        self.heroes: Dict[str, HeroInfo] = {}
        self._load_heroes()

    def _load_heroes(self):
        """加载英雄数据"""
        for hero_id, hero_data in self.data['heroes'].items():
            # 解析技能
            abilities = {}
            for ability_name, ability_data in hero_data['abilities'].items():
                abilities[ability_name] = AbilityInfo(
                    name=ability_name,
                    slot=ability_data['slot'],
                    ability_type=ability_data['type'],
                    behavior=ability_data['behavior'],
                    cast_range=ability_data.get('cast_range', 0),
                    radius=ability_data.get('radius', 0),
                    cooldown=ability_data.get('cooldown', []),
                    mana_cost=ability_data.get('mana_cost', []),
                    weight=ability_data.get('weight', 0.5),
                    ultimate=ability_data.get('ultimate', False),
                    description=ability_data.get('description', '')
                )

            # 创建英雄信息
            self.heroes[hero_id] = HeroInfo(
                hero_id=hero_id,
                name=hero_data['name'],
                primary_attribute=hero_data['primary_attribute'],
                roles=hero_data['roles'],
                abilities=abilities,
                item_builds=hero_data['item_builds'],
                skill_build=hero_data['skill_build'],
                playstyle=hero_data['playstyle']
            )

    def get_hero(self, hero_id: str) -> Optional[HeroInfo]:
        """获取英雄信息"""
        return self.heroes.get(hero_id)

    def get_ability(self, hero_id: str, ability_name: str) -> Optional[AbilityInfo]:
        """获取技能信息"""
        hero = self.get_hero(hero_id)
        if hero:
            return hero.abilities.get(ability_name)
        return None

    def get_item_build(self, hero_id: str, position: str = "pos_1") -> List[str]:
        """获取出装方案"""
        hero = self.get_hero(hero_id)
        if hero:
            return hero.item_builds.get(position, [])
        return []

    def get_skill_build(self, hero_id: str) -> List[int]:
        """获取技能加点方案"""
        hero = self.get_hero(hero_id)
        if hero:
            return hero.skill_build
        return []

    def get_ability_priority(self, hero_id: str) -> List[str]:
        """获取技能使用优先级（按weight排序）"""
        hero = self.get_hero(hero_id)
        if not hero:
            return []

        # 按weight排序
        sorted_abilities = sorted(
            hero.abilities.items(),
            key=lambda x: x[1].weight,
            reverse=True
        )

        return [name for name, _ in sorted_abilities]

    def get_playstyle_tip(self, hero_id: str, game_phase: str) -> str:
        """获取玩法建议"""
        hero = self.get_hero(hero_id)
        if not hero:
            return ""

        phase_map = {
            "laning": "early_game",
            "mid_game": "mid_game",
            "late_game": "late_game"
        }

        phase_key = phase_map.get(game_phase, "early_game")
        return hero.playstyle.get(phase_key, "")

    def get_combos(self, hero_id: str) -> List[str]:
        """获取技能连招"""
        hero = self.get_hero(hero_id)
        if not hero:
            return []

        return hero.playstyle.get("combos", [])

    def should_use_ability(self, hero_id: str, ability_name: str,
                          mana_pct: float, hp_pct: float) -> bool:
        """判断是否应该使用技能"""
        ability = self.get_ability(hero_id, ability_name)
        if not ability:
            return False

        # 被动技能不需要主动使用
        if ability.ability_type == "passive":
            return False

        # 大招需要更谨慎
        if ability.ultimate:
            return mana_pct > 0.5 and hp_pct > 0.3

        # 普通技能
        return mana_pct > 0.3

    def get_item_priority(self, hero_id: str, current_gold: int) -> Optional[str]:
        """根据金钱推荐下一个物品"""
        items = self.get_item_build(hero_id)
        if not items:
            return None

        # 简化：返回第一个买得起的物品
        item_costs = self.data.get('item_data', {})

        for item in items:
            item_info = item_costs.get(item, {})
            cost = item_info.get('cost', 9999)
            if current_gold >= cost:
                return item

        return None


# 全局实例
_hero_knowledge = None


def get_hero_knowledge() -> HeroKnowledge:
    """获取全局英雄知识库实例"""
    global _hero_knowledge
    if _hero_knowledge is None:
        _hero_knowledge = HeroKnowledge()
    return _hero_knowledge


if __name__ == "__main__":
    # 测试
    kb = HeroKnowledge()

    # 测试Axe
    axe = kb.get_hero("npc_dota_hero_axe")
    print(f"Hero: {axe.name}")
    print(f"Roles: {', '.join(axe.roles)}")
    print(f"\nAbilities:")
    for ability_name in kb.get_ability_priority("npc_dota_hero_axe"):
        ability = axe.abilities[ability_name]
        print(f"  - {ability.name} (weight: {ability.weight})")

    print(f"\nItem build (pos_3):")
    for item in kb.get_item_build("npc_dota_hero_axe", "pos_3")[:5]:
        print(f"  - {item}")

    print(f"\nEarly game tip:")
    print(f"  {kb.get_playstyle_tip('npc_dota_hero_axe', 'laning')}")

    print(f"\nCombos:")
    for combo in kb.get_combos("npc_dota_hero_axe"):
        print(f"  - {combo}")
