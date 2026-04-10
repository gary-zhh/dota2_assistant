# Dota 2 AI Assistant - 开发日志

## Phase 1: GSI集成（基础设施）✅

**完成时间**: 2026-04-10

### 已实现功能

1. **GSI配置文件** (`config/gamestate_integration_ai.cfg`)
   - 配置Dota 2向本地HTTP服务器发送游戏状态
   - 更新频率: 100ms
   - 包含数据: 地图、玩家、英雄、技能、物品

2. **GSI HTTP服务器** (`gsi/server.py`)
   - Flask HTTP服务器监听端口3000
   - 接收并解析JSON格式的游戏状态
   - 线程安全的状态存储
   - 支持回调函数机制

3. **游戏状态数据结构** (`gsi/game_state.py`)
   - `GameState`: 完整游戏状态
   - `HeroState`: 英雄状态（血量、蓝量、位置、金钱等）
   - `AbilityState`: 技能状态（等级、冷却、是否可用）
   - `ItemState`: 物品状态（冷却、充能数）
   - 便捷方法: `get_health_percentage()`, `get_game_phase()` 等

4. **主程序框架** (`main.py`)
   - 异步主循环
   - GSI服务器集成
   - 实时显示游戏状态
   - 为Phase 2预留决策系统接口

5. **配置系统** (`config/config.yaml`)
   - GSI服务器配置
   - LLM配置（待使用）
   - 执行器配置（待使用）
   - 游戏分辨率配置

6. **文档**
   - README.md: 完整的安装和使用说明
   - install.sh: 自动安装脚本
   - 风险警告和免责声明

### 项目结构

```
dota2_assistant/
├── config/
│   ├── gamestate_integration_ai.cfg  # GSI配置
│   └── config.yaml                    # 程序配置
├── gsi/
│   ├── __init__.py
│   ├── server.py                      # GSI HTTP服务器
│   └── game_state.py                  # 游戏状态数据结构
├── decision/                          # 决策系统（待实现）
├── executor/                          # 动作执行器（待实现）
├── utils/                             # 工具函数（待实现）
├── main.py                            # 主程序
├── requirements.txt                   # Python依赖
├── install.sh                         # 安装脚本
├── README.md                          # 使用文档
└── DEVLOG.md                          # 本文件
```

### 测试方法

1. 运行安装脚本:
   ```bash
   ./install.sh
   ```

2. 启动AI助手:
   ```bash
   python3 main.py
   ```

3. 启动Dota 2，进入演示英雄模式或自定义游戏

4. 观察终端输出，应该看到类似:
   ```
   [12.3s] npc_dota_hero_axe | HP: 85% | MP: 60% | Gold: 625 | Level: 3
   ```

### 技术要点

- **线程安全**: 使用`threading.Lock`保护共享状态
- **异步架构**: 主循环使用`asyncio`，为后续LLM调用做准备
- **数据类**: 使用`@dataclass`简化数据结构定义
- **错误处理**: GSI服务器捕获并记录解析错误

### Phase 2: 决策系统（核心AI）✅

**完成时间**: 2026-04-10

### 已实现功能

1. **动作定义系统** (`decision/actions.py`)
   - `ActionType`: 所有可能的动作类型（移动、攻击、技能、物品等）
   - `Action`: 动作数据结构（类型、优先级、目标、原因）
   - `Strategy`: 战略决策数据结构（目标、路线、激进度）

2. **LLM战略决策层** (`decision/llm_strategy.py`)
   - 集成OpenAI API（兼容vLLM）
   - 智能prompt构建（游戏状态 → 自然语言）
   - 结构化响应解析（GOAL/LANE/AGGRESSION/BUY/ITEMS）
   - 降级策略（LLM失败时的安全fallback）
   - 决策频率控制（可配置间隔）

3. **规则战术层** (`decision/rule_tactics.py`)
   - 战略到动作的转换
   - 对线逻辑（补刀、走位）
   - 撤退逻辑（低血量回泉水）
   - 打野/刷钱逻辑
   - 游走gank逻辑
   - 推塔逻辑
   - 技能使用判断（蓝量、冷却、激进度）
   - 物品使用判断（治疗物品、主动物品）
   - 动作优先级排序

4. **输入控制器框架** (`executor/input_controller.py`)
   - pynput集成（键盘/鼠标模拟）
   - 基础动作执行（移动、攻击、技能）
   - 世界坐标到屏幕坐标转换（简化版）
   - 人类化延迟（随机延迟模拟人类反应）
   - 紧急停止机制

5. **主程序集成** (`main.py`)
   - 完整的决策循环
   - LLM战略决策（每N秒）
   - 规则战术生成（每帧）
   - 动作显示和执行
   - 实时状态监控

### 决策流程

```
游戏状态 (GSI)
    ↓
LLM战略决策 (每5秒)
    ├─ 分析游戏阶段
    ├─ 评估英雄状态
    └─ 输出战略目标
    ↓
规则战术系统 (每0.1秒)
    ├─ 根据战略生成动作
    ├─ 计算动作优先级
    └─ 输出动作列表
    ↓
输入控制器 (可选)
    ├─ 坐标转换
    ├─ 模拟输入
    └─ 人类化延迟
```

### LLM Prompt示例

```
Current game state:

TIME: 180s (laning)
HERO: npc_dota_hero_axe, Level 3
HEALTH: 75% (600/800)
MANA: 60% (180/300)
GOLD: 850 (reliable: 200)
POSITION: (-2500, -3000)

STATUS: OK
ABILITIES READY: axe_berserkers_call, axe_battle_hunger
ITEMS: item_tango, item_quelling_blade

What should the hero do now?
```

### LLM响应示例

```
GOAL: laning
LANE: bot
AGGRESSION: 0.6
BUY: no
ITEMS: item_boots, item_bracer
REASON: Early game, focus on farming and harassing enemy in lane
```

### 测试方法

1. **仅决策模式**（推荐，安全）:
   ```bash
   # config.yaml中设置 executor.enabled: false
   python3 main.py
   ```
   - 只显示决策，不执行动作
   - 可以观察AI的思考过程

2. **完整模式**（有风险）:
   ```bash
   # config.yaml中设置 executor.enabled: true
   python3 main.py
   ```
   - AI会实际控制游戏
   - ⚠️ 仅在自定义游戏中测试

### 当前限制

1. **坐标映射简化**: 使用小地图点击，精度有限
2. **视觉识别缺失**: 无法识别屏幕上的单位
3. **技能槽位硬编码**: 假设技能在QWER
4. **英雄知识有限**: 没有英雄特定逻辑
5. **团战处理简单**: 复杂场景决策不够智能

## 下一步: Phase 3 - 优化和完善

**目标**: 提升AI的实战能力

**待实现**:
1. 计算机视觉集成
   - 单位识别和定位
   - 血条检测
   - 技能特效识别

2. 英雄知识库
   - 从dota2bot-OpenHyperAI移植英雄数据
   - 技能连招逻辑
   - 出装决策树

3. 高级战术
   - 补刀预判算法
   - 躲技能逻辑
   - 团战目标选择
   - 地图意识和预测

4. 性能优化
   - LLM响应缓存
   - 决策并行化
   - 降低延迟

**预计时间**: 2-3周

## 风险和限制

### 技术限制

1. **GSI延迟**: 约100ms更新频率，无法获取瞬时信息
2. **视野限制**: 只能获取可见单位信息（战争迷雾内不可见）
3. **坐标映射**: GSI提供世界坐标，需要转换为屏幕坐标（Phase 3）

### 法律和道德风险

⚠️ **重要**: 使用输入模拟控制在线游戏可能违反Valve ToS

- 可能被VAC检测
- 账号封禁风险
- 影响其他玩家体验

**建议**:
- 仅在自定义游戏中测试
- 使用小号
- 不在Ranked模式使用
- 考虑开发"建议模式"而非"自动模式"

## 参考资料

- [Dota 2 GSI文档](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration)
- [bota/项目](../bota/) - LLM决策架构参考
- [dota2bot-OpenHyperAI/项目](../dota2bot-OpenHyperAI/) - 游戏逻辑参考
