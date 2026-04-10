"""
补刀算法
预判最佳补刀时机
"""
import math
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class CreepState:
    """小兵状态"""
    handle: int
    health: int
    max_health: int
    position: Tuple[float, float]
    is_ally: bool
    is_under_attack: bool = False
    incoming_damage: int = 0


@dataclass
class LastHitPrediction:
    """补刀预判结果"""
    creep_handle: int
    time_to_kill: float  # 小兵还能存活多久（秒）
    should_attack_now: bool
    priority: float  # 优先级 0-1
    reason: str


class LastHitCalculator:
    """补刀计算器"""

    def __init__(self):
        # 攻击动画时间（秒）
        self.attack_point = 0.5  # 简化：假设0.5秒
        self.attack_backswing = 0.3

        # 弹道速度（单位/秒）
        self.projectile_speed = 900  # 简化：假设900

    def calculate_last_hit(
        self,
        hero_damage: int,
        hero_position: Tuple[float, float],
        creep: CreepState,
        ally_creeps_damage: int = 0,
        enemy_creeps_damage: int = 0
    ) -> LastHitPrediction:
        """
        计算是否应该补刀

        Args:
            hero_damage: 英雄攻击力
            hero_position: 英雄位置
            creep: 小兵状态
            ally_creeps_damage: 友方小兵每秒伤害
            enemy_creeps_damage: 敌方小兵每秒伤害
        """
        # 计算距离
        distance = self._calculate_distance(hero_position, creep.position)

        # 计算攻击延迟
        attack_delay = self._calculate_attack_delay(distance)

        # 预测小兵血量
        predicted_hp = self._predict_creep_hp(
            creep,
            attack_delay,
            ally_creeps_damage,
            enemy_creeps_damage
        )

        # 判断是否应该攻击
        should_attack = self._should_attack_now(
            hero_damage,
            predicted_hp,
            creep.health
        )

        # 计算优先级
        priority = self._calculate_priority(
            creep,
            predicted_hp,
            hero_damage
        )

        # 计算小兵存活时间
        time_to_kill = self._calculate_time_to_kill(
            creep.health,
            ally_creeps_damage if not creep.is_ally else enemy_creeps_damage
        )

        # 生成原因
        reason = self._generate_reason(
            should_attack,
            predicted_hp,
            hero_damage,
            time_to_kill
        )

        return LastHitPrediction(
            creep_handle=creep.handle,
            time_to_kill=time_to_kill,
            should_attack_now=should_attack,
            priority=priority,
            reason=reason
        )

    def _calculate_distance(
        self,
        pos1: Tuple[float, float],
        pos2: Tuple[float, float]
    ) -> float:
        """计算两点距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def _calculate_attack_delay(self, distance: float) -> float:
        """
        计算攻击延迟

        包括：
        1. 攻击前摇（attack point）
        2. 弹道飞行时间（如果是远程）
        """
        # 攻击前摇
        delay = self.attack_point

        # 弹道飞行时间（假设是远程英雄）
        if distance > 150:  # 远程攻击
            projectile_time = distance / self.projectile_speed
            delay += projectile_time

        return delay

    def _predict_creep_hp(
        self,
        creep: CreepState,
        time_delay: float,
        ally_damage: int,
        enemy_damage: int
    ) -> int:
        """
        预测小兵在延迟后的血量

        考虑：
        1. 友方小兵的持续伤害
        2. 敌方小兵的持续伤害
        3. 已知的即将到来的伤害
        """
        current_hp = creep.health

        # 减去即将到来的伤害
        current_hp -= creep.incoming_damage

        # 根据小兵阵营计算伤害
        if creep.is_ally:
            # 友方小兵受到敌方伤害
            damage_per_second = enemy_damage
        else:
            # 敌方小兵受到友方伤害
            damage_per_second = ally_damage

        # 预测血量
        predicted_hp = current_hp - int(damage_per_second * time_delay)

        return max(0, predicted_hp)

    def _should_attack_now(
        self,
        hero_damage: int,
        predicted_hp: int,
        current_hp: int
    ) -> bool:
        """
        判断是否应该立即攻击

        策略：
        1. 如果预测血量 <= 英雄伤害，应该攻击
        2. 如果预测血量 > 英雄伤害但 < 英雄伤害*1.5，也应该攻击（提前量）
        3. 如果当前血量已经很低，立即攻击
        """
        # 情况1：预测血量在击杀范围内
        if predicted_hp <= hero_damage and predicted_hp > 0:
            return True

        # 情况2：预测血量接近击杀范围（提前量）
        if predicted_hp <= hero_damage * 1.3 and predicted_hp > hero_damage * 0.7:
            return True

        # 情况3：当前血量已经很低，不能再等
        if current_hp <= hero_damage * 1.2:
            return True

        return False

    def _calculate_priority(
        self,
        creep: CreepState,
        predicted_hp: int,
        hero_damage: int
    ) -> float:
        """
        计算补刀优先级

        优先级因素：
        1. 血量越低，优先级越高
        2. 预测血量越接近英雄伤害，优先级越高
        3. 远程小兵优先级高于近战小兵（给更多金钱）
        """
        # 基础优先级：血量百分比
        hp_pct = creep.health / creep.max_health
        priority = 1.0 - hp_pct

        # 预测血量匹配度
        if predicted_hp > 0:
            match_score = 1.0 - abs(predicted_hp - hero_damage) / hero_damage
            match_score = max(0, min(1, match_score))
            priority = (priority + match_score) / 2

        # 紧急度：血量很低时提高优先级
        if creep.health < hero_damage * 1.5:
            priority = min(1.0, priority * 1.3)

        return priority

    def _calculate_time_to_kill(
        self,
        current_hp: int,
        damage_per_second: int
    ) -> float:
        """计算小兵还能存活多久"""
        if damage_per_second <= 0:
            return 999.0  # 没有伤害，永远不会死

        return current_hp / damage_per_second

    def _generate_reason(
        self,
        should_attack: bool,
        predicted_hp: int,
        hero_damage: int,
        time_to_kill: float
    ) -> str:
        """生成决策原因"""
        if should_attack:
            if predicted_hp <= hero_damage:
                return f"Perfect timing: predicted HP {predicted_hp} <= damage {hero_damage}"
            elif time_to_kill < 1.0:
                return f"Urgent: creep dies in {time_to_kill:.1f}s"
            else:
                return f"Good timing: predicted HP {predicted_hp} ≈ damage {hero_damage}"
        else:
            return f"Wait: predicted HP {predicted_hp} > damage {hero_damage}"

    def find_best_last_hit(
        self,
        hero_damage: int,
        hero_position: Tuple[float, float],
        creeps: list,
        ally_creeps_damage: int = 50,
        enemy_creeps_damage: int = 50
    ) -> Optional[LastHitPrediction]:
        """
        从多个小兵中找到最佳补刀目标

        Returns:
            优先级最高的补刀目标，如果没有合适的返回None
        """
        predictions = []

        for creep in creeps:
            prediction = self.calculate_last_hit(
                hero_damage,
                hero_position,
                creep,
                ally_creeps_damage,
                enemy_creeps_damage
            )

            if prediction.should_attack_now:
                predictions.append(prediction)

        if not predictions:
            return None

        # 返回优先级最高的
        return max(predictions, key=lambda p: p.priority)


if __name__ == "__main__":
    # 测试补刀算法
    calculator = LastHitCalculator()

    # 模拟场景：3个小兵
    creeps = [
        CreepState(
            handle=1,
            health=120,
            max_health=550,
            position=(100, 100),
            is_ally=False
        ),
        CreepState(
            handle=2,
            health=300,
            max_health=550,
            position=(150, 150),
            is_ally=False
        ),
        CreepState(
            handle=3,
            health=80,
            max_health=550,
            position=(200, 100),
            is_ally=False
        ),
    ]

    hero_damage = 60
    hero_position = (0, 0)

    print("=== Last Hit Calculator Test ===\n")
    print(f"Hero damage: {hero_damage}")
    print(f"Hero position: {hero_position}\n")

    # 测试每个小兵
    for creep in creeps:
        prediction = calculator.calculate_last_hit(
            hero_damage,
            hero_position,
            creep,
            ally_creeps_damage=40,
            enemy_creeps_damage=0
        )

        print(f"Creep #{creep.handle}:")
        print(f"  HP: {creep.health}/{creep.max_health}")
        print(f"  Distance: {calculator._calculate_distance(hero_position, creep.position):.0f}")
        print(f"  Should attack: {prediction.should_attack_now}")
        print(f"  Priority: {prediction.priority:.2f}")
        print(f"  Time to kill: {prediction.time_to_kill:.1f}s")
        print(f"  Reason: {prediction.reason}")
        print()

    # 找最佳目标
    best = calculator.find_best_last_hit(
        hero_damage,
        hero_position,
        creeps,
        ally_creeps_damage=40
    )

    if best:
        print(f"✓ Best target: Creep #{best.creep_handle}")
        print(f"  Priority: {best.priority:.2f}")
        print(f"  {best.reason}")
    else:
        print("✗ No good last hit target")
