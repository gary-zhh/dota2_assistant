"""
测试脚本 - 验证决策系统
不需要Dota 2，使用模拟数据测试LLM和规则系统
"""
import asyncio
import yaml
from gsi import GameState, HeroState, Vector3, AbilityState, ItemState
from decision import LLMStrategy, RuleTactics, Strategy


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
        clock_time=game_time - 90,  # 游戏开始前有90秒准备时间
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
        ),
        AbilityState(
            name="axe_counter_helix",
            level=1,
            can_cast=False,
            cooldown=0.0,
            passive=True,
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
        ),
        ItemState(
            name="item_quelling_blade",
            can_cast=False,
            cooldown=0.0,
            charges=0,
            passive=True
        )
    ]

    return state


async def test_llm_strategy():
    """测试LLM战略决策"""
    print("=== Testing LLM Strategy ===\n")

    # 加载配置
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    llm = LLMStrategy(
        model=config['llm']['model'],
        base_url=config['llm']['base_url'],
        api_key=config['llm']['api_key']
    )

    # 测试场景1: 对线期，血量健康
    print("Scenario 1: Early game, healthy")
    state1 = create_mock_game_state(game_time=180, hp_pct=0.85)
    try:
        strategy1 = await llm.decide(state1)
        print(f"Decision: {strategy1.goal}, Aggression: {strategy1.aggression_level:.2f}\n")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure vLLM server is running or configure OpenAI API\n")

    # 测试场景2: 对线期，血量低
    print("Scenario 2: Early game, low health")
    state2 = create_mock_game_state(game_time=200, hp_pct=0.25)
    try:
        strategy2 = await llm.decide(state2)
        print(f"Decision: {strategy2.goal}, Aggression: {strategy2.aggression_level:.2f}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def test_rule_tactics():
    """测试规则战术系统"""
    print("=== Testing Rule Tactics ===\n")

    tactics = RuleTactics()

    # 测试场景1: 对线策略
    print("Scenario 1: Laning strategy")
    state1 = create_mock_game_state(game_time=180, hp_pct=0.85)
    strategy1 = Strategy(goal="laning", aggression_level=0.6)
    actions1 = tactics.get_actions(state1, strategy1)

    print(f"Generated {len(actions1)} actions:")
    for i, action in enumerate(actions1[:3]):  # 显示前3个
        print(f"  {i+1}. {action}")
    print()

    # 测试场景2: 撤退策略
    print("Scenario 2: Retreat strategy")
    state2 = create_mock_game_state(game_time=200, hp_pct=0.25)
    strategy2 = Strategy(goal="retreat", aggression_level=0.0)
    actions2 = tactics.get_actions(state2, strategy2)

    print(f"Generated {len(actions2)} actions:")
    for i, action in enumerate(actions2[:3]):
        print(f"  {i+1}. {action}")
    print()

    # 测试场景3: 打野策略
    print("Scenario 3: Farming strategy")
    state3 = create_mock_game_state(game_time=600, hp_pct=0.70)
    strategy3 = Strategy(goal="farming", aggression_level=0.4)
    actions3 = tactics.get_actions(state3, strategy3)

    print(f"Generated {len(actions3)} actions:")
    for i, action in enumerate(actions3[:3]):
        print(f"  {i+1}. {action}")
    print()


async def main():
    """主测试函数"""
    print("\n" + "="*50)
    print("Dota 2 AI Assistant - Decision System Test")
    print("="*50 + "\n")

    # 测试规则系统（不需要LLM）
    test_rule_tactics()

    # 测试LLM系统（需要LLM服务器）
    print("Testing LLM (requires vLLM server or OpenAI API)...")
    await test_llm_strategy()

    print("="*50)
    print("Test completed!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
