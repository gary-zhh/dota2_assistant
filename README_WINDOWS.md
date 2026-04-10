# Dota 2 AI Assistant - Windows 安装和使用指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速安装](#快速安装)
3. [手动安装](#手动安装)
4. [配置说明](#配置说明)
5. [运行程序](#运行程序)
6. [常见问题](#常见问题)
7. [Windows特殊说明](#windows特殊说明)

---

## 系统要求

### 必需
- ✅ Windows 10/11 (64位)
- ✅ Python 3.8 或更高版本
- ✅ Dota 2 游戏客户端
- ✅ 至少 4GB 可用内存
- ✅ 网络连接（用于LLM API）

### 可选
- 🔧 NVIDIA GPU（如果使用本地vLLM）
- 🔧 管理员权限（用于安装GSI配置）

---

## 快速安装

### 方法一：自动安装（推荐）

1. **下载项目**
   ```
   将整个 dota2_assistant 文件夹复制到你的电脑
   例如: D:\dota2_assistant
   ```

2. **运行安装脚本**
   - 双击 `install_windows.bat`
   - 按照提示完成安装
   - 脚本会自动：
     - 检查Python
     - 安装依赖
     - 查找Dota 2路径
     - 配置GSI

3. **完成！**
   - 安装完成后会生成 `run_assistant.bat`
   - 双击即可启动AI助手

---

## 手动安装

如果自动安装失败，请按以下步骤手动安装：

### 步骤1: 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8 或更高版本
3. **重要**: 安装时勾选 "Add Python to PATH"
4. 验证安装:
   ```cmd
   python --version
   ```

### 步骤2: 安装依赖

打开命令提示符（CMD）或PowerShell：

```cmd
cd D:\dota2_assistant
pip install -r requirements.txt
```

如果下载速度慢，使用国内镜像：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤3: 配置GSI

1. **找到Dota 2安装路径**

   常见位置：
   ```
   C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta
   D:\Steam\steamapps\common\dota 2 beta
   ```

2. **创建GSI目录**（如果不存在）

   ```
   [Dota 2路径]\game\dota\cfg\gamestate_integration
   ```

   例如：
   ```
   C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration
   ```

3. **复制配置文件**

   将 `config\gamestate_integration_ai.cfg` 复制到上述目录

   或者手动创建文件，内容如下：

   ```
   "Dota 2 AI Assistant"
   {
       "uri"           "http://127.0.0.1:3000/"
       "timeout"       "5.0"
       "buffer"        "0.1"
       "throttle"      "0.1"
       "heartbeat"     "30.0"
       "data"
       {
           "provider"      "1"
           "map"           "1"
           "player"        "1"
           "hero"          "1"
           "abilities"     "1"
           "items"         "1"
       }
   }
   ```

### 步骤4: 配置程序

编辑 `config\config.yaml`:

```yaml
gsi:
  host: "127.0.0.1"  # Windows上使用127.0.0.1
  port: 3000

executor:
  enabled: false  # 首次运行建议设为false（观察模式）

llm:
  model: "openai/gpt-oss-20b"
  base_url: "http://localhost:8000/v1"
  api_key: "EMPTY"
```

---

## 配置说明

### config.yaml 详解

```yaml
# GSI服务器配置
gsi:
  host: "127.0.0.1"      # Windows上必须用127.0.0.1
  port: 3000             # 端口号，不要与其他程序冲突

# LLM配置
llm:
  model: "openai/gpt-oss-20b"
  base_url: "http://localhost:8000/v1"  # vLLM服务器地址
  api_key: "EMPTY"
  strategy_interval: 5.0  # 战略决策间隔（秒）

# 执行器配置
executor:
  enabled: false         # true=自动控制, false=仅观察
  human_delay_min: 0.1   # 最小延迟（秒）
  human_delay_max: 0.3   # 最大延迟（秒）
  emergency_stop_key: "F9"  # 紧急停止键

# 游戏配置
game:
  resolution:
    width: 1920          # 你的游戏分辨率
    height: 1080
  minimap:
    x: 50                # 小地图位置（左下角）
    y: 950
    size: 150
```

### 两种运行模式

#### 观察模式（推荐，安全）
```yaml
executor:
  enabled: false
```
- AI只显示决策，不控制游戏
- 无任何风险
- 适合学习和调试

#### 自动模式（实验性，有风险）
```yaml
executor:
  enabled: true
```
- AI实际控制游戏
- ⚠️ 可能违反ToS
- ⚠️ 仅在自定义游戏中测试

---

## 运行程序

### 方法一：使用启动脚本（推荐）

1. 双击 `run_assistant.bat`
2. 等待程序启动
3. 启动Dota 2并进入游戏

### 方法二：命令行运行

```cmd
cd D:\dota2_assistant
python main.py
```

### 方法三：使用PowerShell

```powershell
cd D:\dota2_assistant
python main.py
```

### 完整流程

1. **启动AI助手**
   ```
   双击 run_assistant.bat
   ```

2. **等待提示**
   ```
   === Starting Dota 2 AI Assistant ===
   Waiting for game state from Dota 2...
   ```

3. **启动Dota 2**
   - 打开Steam
   - 启动Dota 2
   - 进入游戏（自定义游戏或演示英雄模式）

4. **选择英雄**
   - 支持全部123个英雄
   - 选择任意英雄开始游戏

5. **观察AI决策**
   ```
   [180s] laning | npc_dota_hero_axe | HP: 85% | MP: 60%
   
   [LLM Strategy] laning
     Aggression: 0.60
   
   [Action] Attack creeps (priority: 0.85)
   ```

6. **停止程序**
   - 按 `Ctrl+C`
   - 或关闭命令行窗口

---

## 常见问题

### Q1: 提示"python不是内部或外部命令"

**原因**: Python未添加到系统PATH

**解决方法**:
1. 重新安装Python，勾选"Add Python to PATH"
2. 或手动添加Python到PATH：
   - 右键"此电脑" → 属性 → 高级系统设置
   - 环境变量 → 系统变量 → Path → 编辑
   - 添加Python安装路径（例如：`C:\Python39`）

### Q2: pip安装依赖失败

**解决方法**:

```cmd
# 方法1: 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方法2: 逐个安装
pip install flask
pip install pynput
pip install pyyaml
pip install openai

# 方法3: 升级pip
python -m pip install --upgrade pip
```

### Q3: 找不到Dota 2路径

**解决方法**:

1. 打开Steam
2. 右键Dota 2 → 属性 → 本地文件 → 浏览
3. 记下路径，例如：
   ```
   D:\SteamLibrary\steamapps\common\dota 2 beta
   ```
4. 手动复制GSI配置文件到：
   ```
   [上述路径]\game\dota\cfg\gamestate_integration\
   ```

### Q4: 程序启动但没有收到游戏数据

**检查清单**:

1. ✅ GSI配置文件是否正确放置
2. ✅ Dota 2是否已启动并进入游戏
3. ✅ 端口3000是否被占用
   ```cmd
   netstat -ano | findstr :3000
   ```
4. ✅ 防火墙是否阻止了连接
   - 控制面板 → Windows Defender 防火墙
   - 允许应用通过防火墙
   - 添加Python

### Q5: 中文显示乱码

**解决方法**:

```cmd
# 在运行前执行
chcp 65001
python main.py
```

或使用提供的 `run_assistant.bat`（已自动设置UTF-8）

### Q6: 提示"ModuleNotFoundError"

**原因**: 某个依赖包未安装

**解决方法**:

```cmd
# 查看缺少哪个包，例如缺少flask
pip install flask

# 或重新安装所有依赖
pip install -r requirements.txt --force-reinstall
```

### Q7: LLM连接失败

**检查**:

1. 是否启动了vLLM服务器？
   ```cmd
   # 需要在另一个终端运行
   vllm serve openai/gpt-oss-20b
   ```

2. 检查 `config.yaml` 中的 `base_url` 是否正确

3. 或使用OpenAI API：
   ```yaml
   llm:
     model: "gpt-4"
     base_url: "https://api.openai.com/v1"
     api_key: "your-api-key-here"
   ```

### Q8: 权限不足

**解决方法**:

- 右键 `install_windows.bat` → 以管理员身份运行
- 或右键 `run_assistant.bat` → 以管理员身份运行

---

## Windows特殊说明

### 1. 路径分隔符

Windows使用反斜杠 `\`，程序会自动处理：

```python
# 这些都可以工作
"C:\Program Files\Steam"
"C:/Program Files/Steam"
r"C:\Program Files\Steam"
```

### 2. 防火墙设置

首次运行时，Windows可能会弹出防火墙提示：

- ✅ 允许Python访问网络
- ✅ 允许专用网络
- ✅ 允许公用网络（可选）

### 3. 杀毒软件

某些杀毒软件可能会误报：

- 添加 `dota2_assistant` 文件夹到白名单
- 或临时禁用杀毒软件

### 4. 管理员权限

某些操作可能需要管理员权限：

- 安装Python包
- 复制文件到Program Files
- 修改系统设置

**解决方法**: 右键 → 以管理员身份运行

### 5. 长路径支持

如果路径过长导致错误：

1. Win+R 输入 `gpedit.msc`
2. 计算机配置 → 管理模板 → 系统 → 文件系统
3. 启用"启用 Win32 长路径"

### 6. 中文路径

**建议**: 避免使用中文路径

```
❌ C:\用户\张三\桌面\dota2_assistant
✅ C:\Users\zhangsan\Desktop\dota2_assistant
✅ D:\dota2_assistant
```

### 7. 编码问题

程序已自动处理UTF-8编码，如果仍有问题：

```cmd
# 设置控制台为UTF-8
chcp 65001

# 设置Python环境变量
set PYTHONIOENCODING=utf-8
```

---

## 性能优化（Windows）

### 1. 关闭不必要的后台程序

- 任务管理器 → 启动 → 禁用不需要的程序

### 2. 设置高性能模式

- 控制面板 → 电源选项 → 高性能

### 3. 关闭Windows Defender实时保护（可选）

- 仅在运行AI时临时关闭
- 运行完毕后重新启用

### 4. 使用SSD

- 将项目放在SSD上以提高读写速度

---

## 目录结构

```
D:\dota2_assistant\
├── install_windows.bat          # Windows安装脚本
├── run_assistant.bat            # Windows启动脚本
├── main.py                      # 主程序
├── requirements.txt             # Python依赖
├── config/
│   ├── config.yaml              # 主配置文件
│   └── gamestate_integration_ai.cfg  # GSI配置
├── gsi/                         # GSI模块
├── decision/                    # 决策系统
├── executor/                    # 执行器
├── ui/                          # 界面
├── utils/                       # 工具
│   └── platform_compat.py       # 平台兼容性
└── README_WINDOWS.md            # 本文件
```

---

## 快速测试

### 测试1: Python环境

```cmd
python --version
pip --version
```

预期输出：
```
Python 3.9.x
pip 21.x.x
```

### 测试2: 依赖安装

```cmd
python -c "import flask; import pynput; import yaml; print('✓ All dependencies OK')"
```

预期输出：
```
✓ All dependencies OK
```

### 测试3: 平台检测

```cmd
python utils/platform_compat.py
```

预期输出：
```
Platform: windows
Is Windows: True
✓ Dota 2 found: C:\...\dota 2 beta
```

### 测试4: 坐标映射

```cmd
python utils/coordinate_mapper.py
```

预期输出：
```
✅ Coordinate mapping system test completed!
```

---

## 卸载

如需卸载：

1. 删除项目文件夹
   ```
   D:\dota2_assistant
   ```

2. 删除GSI配置
   ```
   [Dota 2路径]\game\dota\cfg\gamestate_integration\gamestate_integration_ai.cfg
   ```

3. 卸载Python包（可选）
   ```cmd
   pip uninstall flask pynput pyyaml openai
   ```

---

## 获取帮助

### 文档
- `README.md` - 完整功能说明
- `PROJECT_COMPLETE.md` - 项目总结
- `ALL_HEROES_COMPLETE.md` - 英雄支持说明

### 测试
- 观察模式测试（安全）
- 自定义游戏测试
- 演示英雄模式测试

### 社区
- GitHub Issues
- 项目文档

---

## 附录：完整安装命令

```cmd
REM 1. 进入项目目录
cd D:\dota2_assistant

REM 2. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 3. 测试环境
python utils/platform_compat.py

REM 4. 运行程序
python main.py
```

---

**祝你使用愉快！🎮**

如有问题，请参考文档或检查配置文件。

---

**版本**: v1.0 - Windows Support  
**更新时间**: 2026-04-10  
**支持系统**: Windows 10/11 (64位)
