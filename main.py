"""
Dota 2 AI Assistant - 主程序
使用GSI获取游戏状态，LLM做战略决策，规则系统做战术执行
"""
import asyncio
import yaml
import sys
import time
from pathlib import Path

from gsi import GSIServer, GameState
from decision import LLMStrategy, RuleTactics, Action
from utils import set_console_encoding


# 设置控制台编码（Windows兼容）
set_console_encoding()


class Dota2Assistant:
    """Dota 2 AI助手主类"""

    def __init__(self, config_path: str = "config/config.yaml"):
        # 加载配置
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # 初始化GSI服务器
        self.gsi_server = GSIServer(
            host=self.config['gsi']['host'],
            port=self.config['gsi']['port']
        )

        # 初始化决策系统
        llm_config = self.config['llm']
        self.llm_strategy = LLMStrategy(
            model=llm_config['model'],
            base_url=llm_config['base_url'],
            api_key=llm_config['api_key']
        )
        self.rule_tactics = RuleTactics()

        # 当前战略
        self.current_strategy = None
        self.last_strategy_time = 0.0
        self.strategy_interval = llm_config['strategy_interval']

        # 执行器开关
        self.executor_enabled = self.config['executor']['enabled']

        print("Dota 2 AI Assistant initialized")
        print(f"GSI Server: {self.config['gsi']['host']}:{self.config['gsi']['port']}")
        print(f"LLM Model: {llm_config['model']}")
        print(f"Executor enabled: {self.executor_enabled}")
        if not self.executor_enabled:
            print("⚠️  Executor is DISABLED - will only show decisions, not execute")

    def on_game_state_update(self, state: GameState):
        """游戏状态更新回调"""
        # 打印基础信息
        if state.hero:
            health_pct = state.get_health_percentage() * 100
            mana_pct = state.get_mana_percentage() * 100
            phase = state.get_game_phase()
            print(f"\r[{state.game_time:.1f}s] {phase} | {state.hero.name} | "
                  f"HP: {health_pct:.0f}% | MP: {mana_pct:.0f}% | "
                  f"Gold: {state.hero.gold} | Lvl: {state.hero.level}", end="")

    async def run(self):
        """主循环"""
        print("\n=== Starting Dota 2 AI Assistant ===")
        print("Waiting for game state from Dota 2...")
        print("Make sure you have:")
        print("1. Copied gamestate_integration_ai.cfg to Dota 2 config folder")
        print("2. Started Dota 2 and entered a game")
        if self.executor_enabled:
            print("3. ⚠️  WARNING: Executor is ENABLED - AI will control your hero!")
        print("\nPress Ctrl+C to stop\n")

        # 设置回调
        self.gsi_server.set_state_callback(self.on_game_state_update)

        # 启动GSI服务器（后台线程）
        self.gsi_server.start_async()

        try:
            # 主循环
            while True:
                await asyncio.sleep(0.1)

                # 获取最新游戏状态
                state = self.gsi_server.get_latest_state()

                if state is None:
                    continue

                # 只在英雄存活时做决策
                if not state.is_hero_alive():
                    continue

                current_time = time.time()

                # 1. 战略决策（每N秒）
                if (self.current_strategy is None or
                    current_time - self.last_strategy_time >= self.strategy_interval):

                    try:
                        self.current_strategy = await self.llm_strategy.decide(state)
                        self.last_strategy_time = current_time
                    except Exception as e:
                        print(f"\nLLM error: {e}")
                        continue

                # 2. 战术动作生成
                if self.current_strategy:
                    actions = self.rule_tactics.get_actions(state, self.current_strategy)

                    # 显示决策
                    if actions:
                        top_action = actions[0]
                        print(f"\n[Action] {top_action}")

                        # 3. 执行动作（如果启用）
                        if self.executor_enabled:
                            # TODO: 调用执行器
                            print("  (Executor not implemented yet)")

        except KeyboardInterrupt:
            print("\n\nStopping AI Assistant...")
            sys.exit(0)


def main():
    """主函数"""
    assistant = Dota2Assistant()

    # 运行异步主循环
    asyncio.run(assistant.run())


if __name__ == "__main__":
    main()
