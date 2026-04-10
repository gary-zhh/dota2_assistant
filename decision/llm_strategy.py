"""
LLM战略决策层
使用大语言模型做高层战略决策
"""
import re
from typing import Optional
from openai import AsyncOpenAI

from gsi import GameState
from .actions import Strategy


class LLMStrategy:
    """LLM战略决策器"""

    def __init__(self, model: str, base_url: str, api_key: str):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
        self.last_decision_time = 0.0

    async def decide(self, game_state: GameState) -> Strategy:
        """做出战略决策"""
        if not game_state.hero or not game_state.hero.alive:
            return Strategy(goal="dead", aggression_level=0.0)

        # 构建prompt
        prompt = self._build_prompt(game_state)

        try:
            # 调用LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            # 解析响应
            decision_text = response.choices[0].message.content
            strategy = self._parse_decision(decision_text, game_state)

            print(f"\n[LLM Strategy] {strategy.goal}")
            print(f"  Aggression: {strategy.aggression_level:.2f}")
            if strategy.target_lane:
                print(f"  Target lane: {strategy.target_lane}")

            return strategy

        except Exception as e:
            print(f"LLM decision error: {e}")
            # 降级到安全策略
            return self._safe_fallback_strategy(game_state)

    def _get_system_prompt(self) -> str:
        """系统提示词"""
        return """You are a Dota 2 strategic AI. Your role is to make high-level decisions about what the hero should do.

Available strategies:
- laning: Stay in lane, farm creeps, harass enemy
- farming: Focus on farming jungle/lane
- ganking: Roam to other lanes to kill enemies
- pushing: Push towers
- teamfight: Join team fights
- retreat: Go back to base to heal/buy items

Consider:
- Game time and phase (early/mid/late game)
- Hero health and mana
- Gold and items
- Team situation

Respond in this format:
GOAL: [strategy]
LANE: [top/mid/bot or none]
AGGRESSION: [0.0-1.0]
BUY: [yes/no]
ITEMS: [item1, item2, ...]
REASON: [brief explanation]"""

    def _build_prompt(self, state: GameState) -> str:
        """构建决策prompt"""
        hero = state.hero
        phase = state.get_game_phase()

        # 计算关键指标
        hp_pct = state.get_health_percentage() * 100
        mp_pct = state.get_mana_percentage() * 100

        prompt = f"""Current game state:

TIME: {state.game_time:.0f}s ({phase})
HERO: {hero.name}, Level {hero.level}
HEALTH: {hp_pct:.0f}% ({hero.health}/{hero.max_health})
MANA: {mp_pct:.0f}% ({hero.mana}/{hero.max_mana})
GOLD: {hero.gold} (reliable: {hero.gold_reliable})
POSITION: ({hero.position.x:.0f}, {hero.position.y:.0f})

STATUS:"""

        if hero.is_stunned:
            prompt += " STUNNED"
        if hero.is_silenced:
            prompt += " SILENCED"
        if not hero.is_stunned and not hero.is_silenced:
            prompt += " OK"

        # 技能状态
        ready_abilities = [a.name for a in state.abilities if a.can_cast and a.level > 0]
        if ready_abilities:
            prompt += f"\nABILITIES READY: {', '.join(ready_abilities[:3])}"

        # 物品
        items = [i.name for i in state.items]
        if items:
            prompt += f"\nITEMS: {', '.join(items[:6])}"

        prompt += "\n\nWhat should the hero do now?"

        return prompt

    def _parse_decision(self, text: str, state: GameState) -> Strategy:
        """解析LLM响应"""
        # 提取目标
        goal_match = re.search(r'GOAL:\s*(\w+)', text, re.IGNORECASE)
        goal = goal_match.group(1).lower() if goal_match else "laning"

        # 提取路线
        lane_match = re.search(r'LANE:\s*(\w+)', text, re.IGNORECASE)
        lane = lane_match.group(1).lower() if lane_match else None
        if lane == "none":
            lane = None

        # 提取激进度
        aggr_match = re.search(r'AGGRESSION:\s*([\d.]+)', text, re.IGNORECASE)
        aggression = float(aggr_match.group(1)) if aggr_match else 0.5
        aggression = max(0.0, min(1.0, aggression))

        # 提取购买建议
        buy_match = re.search(r'BUY:\s*(\w+)', text, re.IGNORECASE)
        should_buy = buy_match and buy_match.group(1).lower() == "yes"

        # 提取物品
        items_match = re.search(r'ITEMS:\s*(.+)', text, re.IGNORECASE)
        items = []
        if items_match:
            items_text = items_match.group(1)
            items = [i.strip() for i in items_text.split(',')]

        return Strategy(
            goal=goal,
            target_lane=lane,
            aggression_level=aggression,
            should_buy=should_buy,
            recommended_items=items
        )

    def _safe_fallback_strategy(self, state: GameState) -> Strategy:
        """安全降级策略"""
        hp_pct = state.get_health_percentage()

        if hp_pct < 0.3:
            return Strategy(goal="retreat", aggression_level=0.0)
        elif state.game_time < 600:
            return Strategy(goal="laning", aggression_level=0.5)
        else:
            return Strategy(goal="farming", aggression_level=0.3)
