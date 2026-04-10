"""
视觉反馈系统
在终端显示AI决策和游戏状态的可视化界面
"""
import os
import sys
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from gsi import GameState
    from decision import Action, Strategy


class VisualFeedback:
    """终端可视化反馈"""

    def __init__(self, width: int = 80):
        self.width = width
        self.last_update = None

    def clear_screen(self):
        """清屏"""
        from utils import clear_screen
        clear_screen()

    def draw_header(self):
        """绘制标题"""
        title = "DOTA 2 AI ASSISTANT"
        print("=" * self.width)
        print(title.center(self.width))
        print("=" * self.width)

    def draw_game_state(self, state: GameState):
        """绘制游戏状态"""
        if not state.hero:
            print("\n⏳ Waiting for game state...")
            return

        hero = state.hero
        phase = state.get_game_phase()

        # 游戏时间和阶段
        game_time_str = f"{int(state.game_time // 60)}:{int(state.game_time % 60):02d}"
        print(f"\n⏱️  Game Time: {game_time_str} | Phase: {phase.upper()}")

        # 英雄信息
        print(f"\n🦸 Hero: {hero.name}")
        print(f"   Level: {hero.level} | Gold: {hero.gold}")

        # 血量条
        hp_pct = state.get_health_percentage()
        self._draw_bar("HP", hp_pct, hero.health, hero.max_health, "❤️", "🟥")

        # 蓝量条
        mp_pct = state.get_mana_percentage()
        self._draw_bar("MP", mp_pct, hero.mana, hero.max_mana, "💙", "🟦")

        # 状态效果
        status = []
        if hero.is_stunned:
            status.append("😵 STUNNED")
        if hero.is_silenced:
            status.append("🤐 SILENCED")
        if hero.is_disarmed:
            status.append("🚫 DISARMED")
        if not hero.alive:
            status.append("💀 DEAD")

        if status:
            print(f"\n   Status: {' '.join(status)}")

    def _draw_bar(self, label: str, percentage: float, current: int, maximum: int,
                  filled_char: str = "█", empty_char: str = "░"):
        """绘制进度条"""
        bar_width = 30
        filled = int(bar_width * percentage)
        empty = bar_width - filled

        # 颜色编码（根据百分比）
        if percentage > 0.7:
            color = "\033[92m"  # 绿色
        elif percentage > 0.3:
            color = "\033[93m"  # 黄色
        else:
            color = "\033[91m"  # 红色

        reset = "\033[0m"

        bar = filled_char * filled + empty_char * empty
        print(f"   {label}: {color}{bar}{reset} {percentage*100:.0f}% ({current}/{maximum})")

    def draw_strategy(self, strategy: Optional[Strategy]):
        """绘制战略决策"""
        print(f"\n{'─' * self.width}")
        print("🧠 STRATEGY")
        print(f"{'─' * self.width}")

        if not strategy:
            print("   No set...")
            return

        # 目标
        goal_icons = {
            "laning": "🌾",
            "farming": "💰",
            "ganking": "🗡️",
            "pushing": "🏰",
            "retreat": "🏃",
            "teamfight": "⚔️",
            "dead": "💀"
        }

        icon = goal_icons.get(strategy.goal, "❓")
        print(f"   Goal: {icon} {strategy.goal.upper()}")

        if strategy.target_lane:
            print(f"   Lane: {strategy.target_lane.upper()}")

        # 激进度条
        aggr_pct = strategy.aggression_level
        aggr_bar_width = 20
        aggr_filled = int(aggr_bar_width * aggr_pct)
        aggr_bar = "🔥" * aggr_filled + "·" * (aggr_bar_width - aggr_filled)
        print(f"   Aggression: {aggr_bar} {aggr_pct*100:.0f}%")

        # 购买建议
        if strategy.should_buy and strategy.recommended_items:
            print(f"   💵 Buy: {', '.join(strategy.recommended_items[:3])}")

    def draw_actions(self, actions: List[Action]):
        """绘制动作列表"""
        print(f"\n{'─' * self.width}")
        print("⚡ ACTIONS")
        print(f"{'─' * self.width}")

        if not actions:
            print("   No actions...")
            return

        # 显示前5个动作
        for i, action in enumerate(actions[:5], 1):
            priority_bar = "█" * int(action.priority * 10)
            print(f"   {i}. [{priority_bar:10s}] {action}")

    def draw_footer(self, executor_enabled: bool):
        """绘制页脚"""
        print(f"\n{'─' * self.width}")

        mode = "🤖 AUTO MODE" if executor_enabled else "👁️  OBSERVE MODE"
        print(f"{mode.center(self.width)}")

        if executor_enabled:
            warning = "⚠️  AI IS CONTROLLING THE GAME"
            print(f"{warning.center(self.width)}")

        print(f"{'─' * self.width}")
        print(f"Press Ctrl+C to stop".center(self.width))

    def render(self, state: Optional[GameState], strategy: Optional[Strategy],
               actions: List[Action], executor_enabled: bool):
        """渲染完整界面"""
        self.clear_screen()
        self.draw_header()

        if state:
            self.draw_game_state(state)

        self.draw_strategy(strategy)
        self.draw_actions(actions)
        self.draw_footer(executor_enabled)

        self.last_update = datetime.now()


class SimpleLogger:
    """简单的日志记录器"""

    def __init__(self, log_file: str = "ai_assistant.log"):
        self.log_file = log_file

    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_line)

    def info(self, message: str):
        self.log("INFO", message)

    def warning(self, message: str):
        self.log("WARNING", message)

    def error(self, message: str):
        self.log("ERROR", message)

    def decision(self, strategy: Strategy, action: Action):
        """记录决策"""
        msg = f"Strategy: {strategy.goal} | Action: {action.action_type.value} (priority: {action.priority:.2f})"
        self.log("DECISION", msg)


if __name__ == "__main__":
    # 测试视觉反馈
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from gsi.game_state import HeroState, Vector3, AbilityState
    from decision.actions import ActionType

    # 创建模拟数据
    hero = HeroState(
        name="npc_dota_hero_axe",
        level=5,
        health=650,
        max_health=800,
        mana=180,
        max_mana=300,
        position=Vector3(-2500, -3000, 0),
        gold=1250,
        gold_reliable=300,
        gold_unreliable=950,
        xp=2400,
        alive=True,
        respawn_seconds=0,
        buyback_cost=200,
        buyback_cooldown=0
    )

    state = GameState(
        game_time=420,
        clock_time=330,
        daytime=True,
        hero=hero
    )

    strategy = Strategy(
        goal="laning",
        target_lane="bot",
        aggression_level=0.65,
        should_buy=True,
        recommended_items=["item_blink", "item_blade_mail"]
    )

    actions = [
        Action(
            action_type=ActionType.ATTACK_CREEP,
            priority=0.85,
            reason="Last hit creep"
        ),
        Action(
            action_type=ActionType.USE_ABILITY,
            priority=0.60,
            ability_name="axe_berserkers_call",
            reason="Enemy in range"
        ),
        Action(
            action_type=ActionType.MOVE,
            priority=0.45,
            target_location=(-2400, -2900),
            reason="Safe positioning"
        ),
    ]

    # 渲染界面
    visual = VisualFeedback()
    visual.render(state, strategy, actions, executor_enabled=False)

    print("\n\n✓ Visual feedback system test completed!")
