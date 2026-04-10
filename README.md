# Dota 2 AI Assistant

一个使用Game State Integration (GSI)、LLM战略决策和规则战术执行的Dota 2 AI助手。

## ⚠️ 重要警告

**使用输入模拟控制在线游戏可能违反Valve服务条款，存在以下风险：**
- 账号可能被VAC反作弊系统检测
- 可能导致永久封禁
- 影响其他玩家的游戏体验

**建议：**
- 仅在自定义游戏中测试
- 使用小号进行测试
- 不要在Ranked模式使用

## 项目状态

当前实现：**Phase 2 - 决策系统（核心AI）**

- ✅ GSI配置文件
- ✅ GSI HTTP服务器
- ✅ 游戏状态解析器
- ✅ LLM战略决策（OpenAI/vLLM）
- ✅ 规则战术系统（对线、打野、gank、推塔）
- ✅ 输入模拟执行器框架
- ⏳ 计算机视觉（单位识别）
- ⏳ 英雄知识库（待完善）
- ⏳ 高级战术（补刀预判、躲技能）

## 安装

### 1. 安装Python依赖

```bash
cd dota2_assistant
pip install -r requirements.txt
```

### 2. 配置GSI

将GSI配置文件复制到Dota 2配置目录：

**macOS:**
```bash
mkdir -p ~/Library/Application\ Support/Steam/steamapps/common/dota\ 2\ beta/game/dota/cfg/gamestate_integration/
cp config/gamestate_integration_ai.cfg ~/Library/Application\ Support/Steam/steamapps/common/dota\ 2\ beta/game/dota/cfg/gamestate_integration/
```

**Linux:**
```bash
mkdir -p ~/.steam/steam/steamapps/common/dota\ 2\ beta/game/dota/cfg/gamestate_integration/
cp config/gamestate_integration_ai.cfg ~/.steam/steam/steamapps/common/dota\ 2\ beta/game/dota/cfg/gamestate_integration/
```

**Windows:**
```powershell
# 通常在 C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration\
# 手动复制 config\gamestate_integration_ai.cfg 到该目录
```

### 3. 配置程序

编辑 `config/config.yaml` 根据你的需求调整配置：

```yaml
gsi:
  port: 3000  # GSI监听端口

executor:
  enabled: false  # 设为true启用自动控制（有风险！）

game:
  resolution:
    width: 1920  # 你的游戏分辨率
    height: 1080
```

## 使用

### 运行AI助手

**观察模式（推荐）**:
```bash
# 确保 config.yaml 中 executor.enabled: false
python3 main.py
```

你会看到：
```
[12.3s] laning | npc_dota_hero_axe | HP: 85% | MP: 60% | Gold: 625 | Lvl: 3

[LLM Strategy] laning
  Aggression: 0.60
  Target lane: bot

[Action] Attack creeps (priority: 0.60)
```

**自动模式（实验性）**:
```bash
# 修改 config.yaml: executor.enabled: true
python3 main.py
```

⚠️ **警告**: 自动模式会实际控制游戏，仅在自定义游戏中测试！

### 配置LLM

如果你有本地vLLM服务器：
```bash
# 终端1: 启动vLLM
vllm serve openai/gpt-oss-20b --gpu-memory-utilization 0.7

# 终端2: 启动AI助手
python3 main.py
```

如果使用OpenAI API：
```yaml
# config.yaml
llm:
  model: "gpt-4"
  base_url: "https://api.openai.com/v1"
  api_key: "your-api-key-here"
```

### 当前功能

**Phase 1 - GSI集成**：
- 实时接收游戏状态（100ms更新频率）
- 解析英雄、技能、物品、地图信息
- 线程安全的状态管理

**Phase 2 - 决策系统**：
- **LLM战略决策**: 使用大语言模型做高层决策（对线/打野/gank/推塔/撤退）
- **规则战术系统**: 基于规则生成具体动作（移动、攻击、技能、物品）
- **混合架构**: LLM负责战略，规则负责战术执行
- **动作优先级**: 自动排序和选择最优动作
- **输入模拟**: 键盘/鼠标控制（可选，默认禁用）

### 使用模式

**1. 观察模式（推荐，安全）**
- AI只显示决策，不控制游戏
- 可以学习AI的思考过程
- 无封号风险

**2. 自动模式（实验性，有风险）**
- AI实际控制游戏角色
- ⚠️ 仅在自定义游戏中使用
- 可能违反ToS

## 架构

```
dota2_assistant/
├── config/
│   ├── gamestate_integration_ai.cfg  # GSI配置
│   └── config.yaml                    # 程序配置
├── gsi/
│   ├── server.py                      # GSI HTTP服务器
│   └── game_state.py                  # 游戏状态数据结构
├── decision/                          # 决策系统（待实现）
├── executor/                          # 动作执行器（待实现）
├── main.py                            # 主程序
└── requirements.txt                   # 依赖
```

## 开发路线图

### Phase 1: GSI集成 ✅
- [x] GSI配置和服务器
- [x] 游戏状态解析
- [x] 基础主程序

### Phase 2: 决策系统（进行中）
- [ ] LLM战略决策
- [ ] 规则战术系统
- [ ] 英雄知识库

### Phase 3: 动作执行
- [ ] 输入模拟
- [ ] 相机控制
- [ ] 动作队列

## GSI数据示例

Dota 2通过GSI发送的JSON数据示例：

```json
{
  "provider": {
    "name": "Dota 2",
    "appid": 570,
    "version": 50
  },
  "map": {
    "name": "start",
    "matchid": "0",
    "game_time": 123,
    "clock_time": 95,
    "daytime": true,
    "radiant_score": 5,
    "dire_score": 3
  },
  "hero": {
    "name": "npc_dota_hero_axe",
    "level": 5,
    "health": 680,
    "max_health": 800,
    "mana": 240,
    "max_mana": 300,
    "x": 1234.5,
    "y": -2345.6,
    "gold": 1250,
    "alive": true
  },
  "abilities": {
    "ability_0": {
      "name": "axe_berserkers_call",
      "level": 2,
      "can_cast": true,
      "cooldown": 0,
      "ultimate": false
    }
  },
  "items": {
    "slot0": {
      "name": "item_blink",
      "can_cast": true,
      "cooldown": 0
    }
  }
}
```

## 故障排除

### GSI没有数据

1. 检查配置文件是否正确放置
2. 确保Dota 2已启动并进入游戏
3. 检查端口3000是否被占用
4. 查看Dota 2控制台是否有GSI相关错误

### 程序报错

1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 检查Python版本（需要3.8+）
3. 查看错误日志

## 参考资料

- [Dota 2 GSI官方文档](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration)
- [Dota 2 Bot API](https://developer.valvesoftware.com/wiki/Dota_Bot_Scripting)

## 许可

本项目仅供学习和研究使用。使用本软件造成的任何后果由使用者自行承担。

## 贡献

欢迎提交Issue和Pull Request！

当前需要帮助的领域：
- LLM prompt工程
- 规则战术算法
- 坐标系统映射
- 性能优化
