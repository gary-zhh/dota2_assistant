"""
坐标映射系统
实现精确的Dota 2世界坐标到屏幕坐标的转换
"""
import math
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Vector2:
    """2D向量"""
    x: float
    y: float

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)


@dataclass
class CameraState:
    """相机状态"""
    position: Vector2  # 相机中心位置（世界坐标）
    zoom: float = 1.0  # 缩放级别
    angle: float = 0.0  # 旋转角度（弧度）


class CoordinateMapper:
    """坐标映射器"""

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Dota 2地图范围（世界坐标）
        self.map_min = Vector2(-8000, -8000)
        self.map_max = Vector2(8000, 8000)
        self.map_size = 16000

        # 小地图配置
        self.minimap_position = Vector2(50, 950)  # 左下角
        self.minimap_size = 150

        # 默认相机状态
        self.camera = CameraState(
            position=Vector2(0, 0),
            zoom=1.0
        )

        # 游戏视口配置
        # Dota 2的默认视野范围（世界单位）
        self.viewport_width = 3000  # 水平视野范围
        self.viewport_height = 2000  # 垂直视野范围

        # UI边距（屏幕像素）
        self.ui_margin_left = 0
        self.ui_margin_right = 0
        self.ui_margin_top = 0
        self.ui_margin_bottom = 200  # 底部UI栏

        # 可用游戏区域
        self.game_area_width = screen_width - self.ui_margin_left - self.ui_margin_right
        self.game_area_height = screen_height - self.ui_margin_top - self.ui_margin_bottom

    def update_camera(self, hero_position: Tuple[float, float]):
        """
        更新相机位置（跟随英雄）

        Args:
            hero_position: 英雄的世界坐标
        """
        self.camera.position = Vector2(hero_position[0], hero_position[1])

    def world_to_screen(
        self,
        world_pos: Tuple[float, float],
        use_minimap: bool = False
    ) -> Optional[Tuple[int, int]]:
        """
        将世界坐标转换为屏幕坐标

        Args:
            world_pos: 世界坐标 (x, y)
            use_minimap: 是否使用小地图点击（更可靠但精度低）

        Returns:
            屏幕坐标 (x, y)，如果不在屏幕内返回None
        """
        if use_minimap:
            return self._world_to_minimap(world_pos)
        else:
            return self._world_to_viewport(world_pos)

    def _world_to_minimap(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """
        将世界坐标转换为小地图坐标

        小地图映射：
        - 世界坐标 (-8000, -8000) 到 (8000, 8000)
        - 映射到小地图区域
        """
        wx, wy = world_pos

        # 归一化到 0-1
        norm_x = (wx - self.map_min.x) / self.map_size
        norm_y = (wy - self.map_min.y) / self.map_size

        # 映射到小地图（注意Y轴反转）
        screen_x = self.minimap_position.x + norm_x * self.minimap_size
        screen_y = self.minimap_position.y + (1 - norm_y) * self.minimap_size

        return (int(screen_x), int(screen_y))

    def _world_to_viewport(
        self,
        world_pos: Tuple[float, float]
    ) -> Optional[Tuple[int, int]]:
        """
        将世界坐标转换为游戏视口坐标

        考虑相机位置和缩放
        """
        wx, wy = world_pos

        # 相对于相机的位置
        relative_x = wx - self.camera.position.x
        relative_y = wy - self.camera.position.y

        # 检查是否在视野范围内
        half_viewport_width = self.viewport_width / 2 * self.camera.zoom
        half_viewport_height = self.viewport_height / 2 * self.camera.zoom

        if (abs(relative_x) > half_viewport_width or
            abs(relative_y) > half_viewport_height):
            return None  # 不在屏幕内

        # 归一化到 -1 到 1
        norm_x = relative_x / half_viewport_width
        norm_y = relative_y / half_viewport_height

        # 转换为屏幕坐标
        # Dota 2使用等距视角，Y轴需要特殊处理
        screen_x = self.ui_margin_left + (norm_x + 1) * self.game_area_width / 2
        screen_y = self.ui_margin_top + (1 - norm_y) * self.game_area_height / 2

        # 应用等距投影修正
        # Dota 2的视角大约是30度俯视角
        iso_angle = math.radians(30)
        screen_y = screen_y * math.cos(iso_angle)

        return (int(screen_x), int(screen_y))

    def screen_to_world(
        self,
        screen_pos: Tuple[int, int]
    ) -> Optional[Tuple[float, float]]:
        """
        将屏幕坐标转换为世界坐标（逆向转换）

        Args:
            screen_pos: 屏幕坐标 (x, y)

        Returns:
            世界坐标 (x, y)，如果无效返回None
        """
        sx, sy = screen_pos

        # 检查是否在游戏区域内
        if (sx < self.ui_margin_left or
            sx > self.screen_width - self.ui_margin_right or
            sy < self.ui_margin_top or
            sy > self.screen_height - self.ui_margin_bottom):
            return None

        # 转换为归一化坐标
        norm_x = (sx - self.ui_margin_left) / self.game_area_width * 2 - 1
        norm_y = 1 - (sy - self.ui_margin_top) / self.game_area_height * 2

        # 反向应用等距投影
        iso_angle = math.radians(30)
        norm_y = norm_y / math.cos(iso_angle)

        # 转换为世界坐标
        half_viewport_width = self.viewport_width / 2 * self.camera.zoom
        half_viewport_height = self.viewport_height / 2 * self.camera.zoom

        world_x = self.camera.position.x + norm_x * half_viewport_width
        world_y = self.camera.position.y + norm_y * half_viewport_height

        return (world_x, world_y)

    def calculate_distance(
        self,
        pos1: Tuple[float, float],
        pos2: Tuple[float, float]
    ) -> float:
        """计算两个世界坐标之间的距离"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx**2 + dy**2)

    def is_on_screen(self, world_pos: Tuple[float, float]) -> bool:
        """判断世界坐标是否在当前屏幕内"""
        return self._world_to_viewport(world_pos) is not None

    def get_direction_to(
        self,
        from_pos: Tuple[float, float],
        to_pos: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        获取从一个位置到另一个位置的方向向量（归一化）

        Returns:
            (dx, dy) 归一化的方向向量
        """
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        length = math.sqrt(dx**2 + dy**2)

        if length > 0:
            return (dx / length, dy / length)
        return (0, 0)

    def move_towards(
        self,
        from_pos: Tuple[float, float],
        to_pos: Tuple[float, float],
        distance: float
    ) -> Tuple[float, float]:
        """
        从一个位置向另一个位置移动指定距离

        Args:
            from_pos: 起始位置
            to_pos: 目标位置
            distance: 移动距离

        Returns:
            新的位置坐标
        """
        direction = self.get_direction_to(from_pos, to_pos)
        new_x = from_pos[0] + direction[0] * distance
        new_y = from_pos[1] + direction[1] * distance
        return (new_x, new_y)

    def clamp_to_map(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        """将坐标限制在地图范围内"""
        x = max(self.map_min.x, min(self.map_max.x, world_pos[0]))
        y = max(self.map_min.y, min(self.map_max.y, world_pos[1]))
        return (x, y)

    def get_safe_retreat_position(
        self,
        hero_pos: Tuple[float, float],
        team: str = "radiant"
    ) -> Tuple[float, float]:
        """
        获取安全撤退位置（泉水方向）

        Args:
            hero_pos: 英雄当前位置
            team: 队伍 ("radiant" 或 "dire")

        Returns:
            撤退目标位置
        """
        # 泉水位置
        if team == "radiant":
            fountain = (-6500, -6500)
        else:
            fountain = (6500, 6500)

        # 向泉水方向移动一段距离
        direction = self.get_direction_to(hero_pos, fountain)
        retreat_distance = 1000  # 移动1000单位

        retreat_x = hero_pos[0] + direction[0] * retreat_distance
        retreat_y = hero_pos[1] + direction[1] * retreat_distance

        return self.clamp_to_map((retreat_x, retreat_y))

    def get_lane_position(self, lane: str, position: str = "safe") -> Tuple[float, float]:
        """
        获取指定路线的位置

        Args:
            lane: "top", "mid", "bot"
            position: "safe" (靠近己方塔), "mid" (中间), "aggressive" (靠近敌方塔)

        Returns:
            世界坐标
        """
        lane_positions = {
            "top": {
                "safe": (-5000, 5000),
                "mid": (-3000, 3000),
                "aggressive": (-1000, 1000)
            },
            "mid": {
                "safe": (-2000, -2000),
                "mid": (0, 0),
                "aggressive": (2000, 2000)
            },
            "bot": {
                "safe": (5000, -5000),
                "mid": (3000, -3000),
                "aggressive": (1000, -1000)
            }
        }

        return lane_positions.get(lane, {}).get(position, (0, 0))


# 全局实例
_coordinate_mapper = None


def get_coordinate_mapper(screen_width: int = 1920, screen_height: int = 1080) -> CoordinateMapper:
    """获取全局坐标映射器实例"""
    global _coordinate_mapper
    if _coordinate_mapper is None:
        _coordinate_mapper = CoordinateMapper(screen_width, screen_height)
    return _coordinate_mapper


if __name__ == "__main__":
    # 测试坐标映射系统
    print("=== Coordinate Mapping System Test ===\n")

    mapper = CoordinateMapper(1920, 1080)

    # 测试1: 世界坐标到小地图
    print("Test 1: World to Minimap")
    test_positions = [
        (-6500, -6500, "Radiant Fountain"),
        (6500, 6500, "Dire Fountain"),
        (0, 0, "Map Center"),
        (-3000, 3000, "Top Lane"),
        (3000, -3000, "Bot Lane")
    ]

    for wx, wy, name in test_positions:
        minimap_pos = mapper._world_to_minimap((wx, wy))
        print(f"  {name}: ({wx}, {wy}) -> Minimap ({minimap_pos[0]}, {minimap_pos[1]})")

    # 测试2: 相机跟随和视口转换
    print("\nTest 2: World to Viewport (Camera at hero)")
    hero_pos = (-2500, -3000)
    mapper.update_camera(hero_pos)

    nearby_positions = [
        (hero_pos, "Hero position"),
        ((-2500, -2500), "500 units north"),
        ((-2000, -3000), "500 units east"),
        ((-3000, -3000), "500 units west"),
        ((0, 0), "Far away (map center)")
    ]

    for pos, name in nearby_positions:
        screen_pos = mapper._world_to_viewport(pos)
        if screen_pos:
            print(f"  {name}: {pos} -> Screen {screen_pos}")
        else:
            print(f"  {name}: {pos} -> Off screen")

    # 测试3: 距离计算
    print("\nTest 3: Distance Calculation")
    pos1 = (-2500, -3000)
    pos2 = (-2000, -2500)
    distance = mapper.calculate_distance(pos1, pos2)
    print(f"  Distance from {pos1} to {pos2}: {distance:.0f} units")

    # 测试4: 方向和移动
    print("\nTest 4: Direction and Movement")
    direction = mapper.get_direction_to(pos1, pos2)
    print(f"  Direction from {pos1} to {pos2}: ({direction[0]:.2f}, {direction[1]:.2f})")

    new_pos = mapper.move_towards(pos1, pos2, 500)
    print(f"  Move 500 units towards target: {new_pos}")

    # 测试5: 安全撤退位置
    print("\nTest 5: Safe Retreat Position")
    retreat_pos = mapper.get_safe_retreat_position(hero_pos, "radiant")
    print(f"  Hero at {hero_pos}")
    print(f"  Retreat position: {retreat_pos}")
    retreat_distance = mapper.calculate_distance(hero_pos, retreat_pos)
    print(f"  Retreat distance: {retreat_distance:.0f} units")

    # 测试6: 路线位置
    print("\nTest 6: Lane Positions")
    for lane in ["top", "mid", "bot"]:
        for position in ["safe", "mid", "aggressive"]:
            pos = mapper.get_lane_position(lane, position)
            print(f"  {lane.upper()} lane ({position}): {pos}")

    print("\n✅ Coordinate mapping system test completed!")
