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
        hp_pct = state.get_health_percentage()
        game_time = state.game_time

        # 判断是哪条路（基于英雄位置）
        hero_x, hero_y = hero.position.x, hero.position.y

        # 计算对线位置（根据路线保持合适的站位）
        if abs(hero_x + hero_y) < 2000:  # 中路
            lane_center = (0, 0)
            safe_offset = 300
        elif hero_x < 0 and hero_y > 0:  # 上路（天辉视角）
            lane_center = (-3000, 3000)
            safe_offset = 400
        else:  # 下路
            lane_center = (3000, -3000)
            safe_offset = 400

        # 根据血量决定激进程度
        if hp_pct < 0.3:
            # 血量很低，撤退到塔下
            tower_pos = (lane_center[0] * 0.7, lane_center[1] * 0.7)
            actions.append(Action(
                action_type=ActionType.MOVE,
                priority=0.95,
                target_location=tower_pos,
                reason="Very low HP, retreat to tower"
            ))
        elif hp_pct < 0.5:
            # 血量偏低，保守走位
            safe_pos = (
                hero_x + (lane_center[0] - hero_x) * 0.3,
                hero_y + (lane_center[1] - hero_y) * 0.3
            )
            actions.append(Action(
                action_type=ActionType.MOVE,
                priority=0.7,
                target_location=safe_pos,
                reason="Low HP, playing safe"
            ))
            # 仍然尝试补刀，但优先级较低
            actions.append(Action(
                action_type=ActionType.ATTACK_CREEP,
                priority=0.5,
                reason="Careful last hitting"
            ))
        else:
            # 血量健康，积极对线
            # 1. 走位到对线位置
            lane_pos = (
                lane_center[0] + (safe_offset if strategy.aggression_level > 0.5 else -safe_offset),
                lane_center[1] + (safe_offset if strategy.aggression_level > 0.5 else -safe_offset)
            )

            # 计算与目标位置的距离
            dist_to_lane = math.sqrt(
                (hero_x - lane_pos[0])**2 + (hero_y - lane_pos[1])**2
            )

            # 如果距离对线位置较远，先移动
            if dist_to_lane > 500:
                actions.append(Action(
                    action_type=ActionType.MOVE,
                    priority=0.75,
                    target_location=lane_pos,
                    reason="Moving to lane position"
                ))

            # 2. 补刀动作（使用A键攻击移动）
            actions.append(Action(
                action_type=ActionType.ATTACK_CREEP,
                priority=0.8,
                reason="Last hitting creeps"
            ))

            # 3. 定期微调走位（避免站桩）
            if int(game_time * 10) % 3 == 0:  # 每0.3秒左右
                micro_offset = (
                    hero_x + (100 if int(game_time) % 2 == 0 else -100),
                    hero_y + (100 if int(game_time) % 2 == 1 else -100)
                )
                actions.append(Action(
                    action_type=ActionType.MOVE,
                    priority=0.4,
                    target_location=micro_offset,
                    reason="Micro positioning"
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
