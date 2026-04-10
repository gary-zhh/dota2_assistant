"""
GSI HTTP服务器
接收Dota 2通过Game State Integration发送的游戏状态数据
"""
import json
import threading
from typing import Optional, Callable
from flask import Flask, request
from .game_state import GameState


class GSIServer:
    """Game State Integration HTTP服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 3000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.latest_state: Optional[GameState] = None
        self.state_lock = threading.Lock()
        self.on_state_update: Optional[Callable[[GameState], None]] = None

        # 设置路由
        @self.app.route('/', methods=['POST'])
        def receive_game_state():
            try:
                data = request.get_json(force=True)
                game_state = GameState.from_gsi_data(data)

                with self.state_lock:
                    self.latest_state = game_state

                if self.on_state_update:
                    self.on_state_update(game_state)

                return '', 200
            except Exception as e:
                print(f"Error processing GSI data: {e}")
                return str(e), 500

    def start(self):
        """启动服务器（阻塞）"""
        print(f"Starting GSI server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)

    def start_async(self):
        """在后台线程启动服务器（非阻塞）"""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        print(f"GSI server started in background on {self.host}:{self.port}")

    def get_latest_state(self) -> Optional[GameState]:
        """获取最新的游戏状态"""
        with self.state_lock:
            return self.latest_state

    def set_state_callback(self, callback: Callable[[GameState], None]):
        """设置状态更新回调函数"""
        self.on_state_update = callback
