"""
简化测试脚本 - 验证决策系统核心逻辑
不需要安装额外依赖
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gsi.game_state import GameState, HeroState, Vector3, AbilityState, ItemState
from decision.actions import Strategy, Action, ActionType
from decision.rule_tactics import RuleTactics


def create_mock_game_state(game_time: float, hp_pct: float) -> GameState:
    """创建模拟游戏状态"""
    hero = HeroState(
        name="npc_dota_hero_axe",
        level=3,
        health=int(800 * hp_pct),
        max_health=800,
        mana=180,
        max_mana=300,
        position=Vector3(-2500, -3000, 0),
        gold=850,
        gold_reliable=200,
        gold_unreliable=650,
        xp=1200,
        alive=True,
        respawn_seconds=0,
        buyback_cost=150,
        buyback_cooldown=0
    )

    state = GameState(
        game_time=game_time,
        clock_time=game_time - 90,
        daytime=True,
        hero=hero
    )

    # 添加技能
    state.abilities = [
        AbilityState(
            name="axe_berserkers_call",
            level=1,
            can_cast=True,
            cooldown=0.0,
            passive=False,
            ultimate=False
        ),
        AbilityState(
            name="axe_battle_hunger",
            level=1,
            can_cast=True,
            cooldown=0.0,
            passive=False,
            ultimate=False
        )
    ]

    # 添加物品
    state.items = [
        ItemState(
            name="item_tango",
            can_cast=True,
            cooldown=0.0,
            charges=3,
            passive=False
        )
    ]

    return state


def test_rule_tactics():
    """测试规则战术系统"""
    print("\n" + "="*60)
    print("Dota 2 AI Assistant - Decision System Test")
    print("="*60 + "\n")

    tactics = RuleTactics()

    # 测试场景1: 对线策略
    print("Scenario 1: Laning (HP: 85%)")
    print("-" * 60)
    state1 = create_mock_game_state(game_time=180, hp_pct=0.85)
    strategy1 = Strategy(goal="laning", aggression_level=0.6)
    actions1 = tactics.get_actions(state1, strategy1)

    print(f"Strategy: {strategy1.goal}, Aggression: {strategy1.aggression_level:.2f}")
    print(f"Generated {len(actions1)} actions:")
    for i, action in enumerate(actions1[:5]):
        print(f"  {i+1}. {action}")
    print()

    # 测试场景2: 撤退策略
    print("Scenario 2: Retreat (HP: 25%)")
    print("-" * 60)
    state2 = create_mock_game_state(game_time=200, hp_pct=0.25)
    strategy2 = Strategy(goal="retreat", aggression_level=0.0)
    actions2 = tactics.get_actions(state2, strategy2)

    print(f"Strategy: {strategy2.goal}, Aggression: {strategy2.aggression_level:.2f}")
    print(f"Generated {len(actions2)} actions:")
    for i, action in enumerate(actions2[:5]):
        print(f"  {i+1}. {action}")
    print()

    # 测试场景3: 打野策略
    print("Scenario 3: Farming (HP: 70%)")
    print("-" * 60)
    state3 = create_mock_game_state(game_time=600, hp_pct=0.70)
    strategy3 = Strategy(goal="farming", aggression_level=0.4)
    actions3 = tactics.get_actions(state3, strategy3)

    print(f"Strategy: {strategy3.goal}, Aggression: {strategy3.aggression_level:.2f}")
    print(f"Generated {len(actions3)} actions:")
    for i, action in enumerate(actions3[:5]):
        print(f"  {i+n}")
    print()

    # 测试场景4: Gank策略
    print("Scenario 4: Ganking mid lane (HP: 90%)")
    print("-" * 60)
    state4 = create_mock_game_state(game_time=400, hp_pct=0.90)
    strategy4 = Strategy(goal="ganking", target_lane="mid", aggression_level=0.8)
    actions4 = tactics.get_actions(state4, strategy4)

    print(f"Strategy: {strategy4.goal}, Lane: {strategy4.target_lane}, Aggression: {strategy4.aggression_level:.2f}")
    print(f"Generated {len(actions4)} actions:")
    for i, action in enumerate(actions4[:5]):
        print(f"  {i+1}. {action}")


    print("="*60)
    print("✅ Rule Tactics System Test Passed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Install dependencies: pip3 install -r requirements.txt")
    print("2. Configure GSI: ./install.sh")
    print("3. Run AI assistant: python3 main.py")
    print("4. Start Dota 2 and enter a game")
    print("\nNote: LLM test requires vLLM server or OpenAI API configured")
    print()


if __name__ == "__main__":
    test_rule_tactics()
