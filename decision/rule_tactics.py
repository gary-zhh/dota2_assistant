"""
规则战术层
基于规则的战术决策和动作生成
"""
from typing import List, Optional
import math

from gsi import GameState
from .actions import Action, ActionType, Strategy


class RuleTactics:
    """规则战术系统"""

    def __init__(self):
        self.last_action_time = 0.0

    def get_actions(self, game_state: GameState, strategy: Strategy) -> List[Action]:
        """根据游戏状态和战略生成动作列表"""
        if not game_state.hero or not game_state.hero.alive:
            return []

        actions = []

        # 根据战略生成动作
        if strategy.goal == "retreat":
            actions.extend(self._retreat_actions(game_state))
        elif strategy.goal == "laning":
            actions.extend(self._laning_actions(game_state, strategy))
        elif strategy.goal == "farming":
            actions.extend(self._farming_actions(game_state))
        elif strategy.goal == "ganking":
            actions.extend(self._ganking_actions(game_state, strategy))
        elif strategy.goal == "pushing":
            actions.extend(self._pushing_actions(game_state))

        # 添加通用动作（技能使用、物品使用等）
        actions.extend(self._ability_actions(game_state, strategy))
        actions.extend(self._item_actions(game_state))

        # 按优先级排序
        actions.sort(key=lambda a: a.priority, reverse=True)

        return actions

    def _retreat_actions(self, state: GameState) -> List[Action]:
        """撤退动作"""
        actions = []

        # 计算泉水方向（简化：假设天辉在左下，夜魇在右上）
        hero_pos = state.hero.position

        # Dota 2地图大致范围：-7000到7000
        # 天辉泉水约在(-6500, -6500)，夜魇泉水约在(6500, 6500)
        if hero_pos.x < 0:  # 假设是天辉
            fountain = (-6500, -6500)
        else:  # 夜魇
            fountain = (6500, 6500)

        actions.append(Action(
            action_type=ActionType.RETREAT,
            priority=0.9,
            target_location=fountain,
            reason="Low health, retreating to fountain"
        ))

        return actions

    def _laning_actions(self, state: GameState, strategy: Strategy) -> List[Action]:
        """对线动作"""
        actions = []
        hero = state.hero

        # 简化的对线逻辑
        hp_pct = state.get_health_percentage()

        if hp_pct < 0.4:
            # 血量低，保守走位
            actions.append(Action(
                action_type=ActionType.MOVE,
                priority=0.7,
                target_location=(hero.position.x - 200, hero.position.y - 200),
                reason="Low HP, playing safe"
            ))
        else:
            # 正常对线，保持位置
            actions.append(Action(
                action_type=ActionType.ATTACK_CREEP,
                priority=0.6,
                reason="Last hitting creeps"
            ))

        return actions

    def _farming_actions(self, state: GameState) -> List[Action]:
        """打野/刷钱动作"""
        actions = []

        actions.append(Action(
            action_type=ActionType.ATTACK_CREEP,
            priority=0.7,
            reason="Farming creeps"
        ))

        return actions

    def _ganking_actions(self, state: GameState, strategy: Strategy) -> List[Action]:
        """游走gank动作"""
        actions = []

        # 简化：移动到目标路线
        if strategy.target_lane:
            # 根据路线计算大致位置
            lane_positions = {
                "top": (-5000, 5000),
                "mid": (0, 0),
                "bot": (5000, -5000)
            }
            target = lane_positions.get(strategy.target_lane, (0, 0))

            actions.append(Action(
                action_type=ActionType.MOVE,
                priority=0.8,
                target_location=target,
                reason=f"Moving to {strategy.target_lane} lane for gank"
            ))

        return actions

    def _pushing_actions(self, state: GameState) -> List[Action]:
        """推塔动作"""
        actions = []

        actions.append(Action(
            action_type=ActionType.ATTACK_MOVE,
            priority=0.7,
            reason="Pushing tower"
        ))

        return actions

    def _ability_actions(self, state: GameState, strategy: Strategy) -> List[Action]:
        """技能使用动作"""
        actions = []

        # 检查可用技能
        for ability in state.abilities:
            if ability.can_cast and ability.level > 0:
                # 简化的技能使用逻辑
                mp_pct = state.get_mana_percentage()

                if mp_pct > 0.5:  # 蓝量充足
                    priority = 0.5 if ability.ultimate else 0.4

                    actions.append(Action(
                        action_type=ActionType.USE_ABILITY,
                        priority=priority * strategy.aggression_level,
                        ability_name=ability.name,
                        reason=f"Use {ability.name}"
                    ))

        return actions

    def _item_actions(self, state: GameState) -> List[Action]:
        """物品使用动作"""
        actions = []

        hp_pct = state.get_health_percentage()

        # 检查治疗物品
        for item in state.items:
            if item.can_cast:
                # 简化：检查是否是治疗物品
                if "flask" in item.name.lower() or "salve" in item.name.lower():
                    if hp_pct < 0.5:
                        actions.append(Action(
                            action_type=ActionType.USE_ITEM,
                            priority=0.8,
                            item_name=item.name,
                            reason="Use healing item"
                        ))

                # 其他主动物品
                elif "blink" in item.name.lower():
                    actions.append(Action(
                        action_type=ActionType.USE_ITEM,
                        priority=0.6,
                        item_name=item.name,
                        reason="Use blink dagger"
                    ))

        return actions

    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """计算两点距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
