"""
从dota2bot-OpenHyperAI提取所有英雄数据
生成完整的heroes.json
"""
import re
import json
import os
from pathlib import Path


def parse_spell_list(lua_file_path):
    """解析spell_list.lua获取所有英雄的技能权重"""
    with open(lua_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    heroes_spells = {}

    # 匹配每个英雄的技能块
    # 格式: ['npc_dota_hero_xxx'] = { ['ability_name'] = {weight = 0.8}, ... }
    # 使用更宽松的正则表达式
    hero_pattern = r"\['(npc_dota_hero_\w+)'\]\s*=\s*\{([\s\S]*?)\n\s*\},"

    for hero_match in re.finditer(hero_pattern, content):
        hero_id = hero_match.group(1)
        abilities_block = hero_match.group(2)

        # 提取技能和权重
        ability_pattern = r"\['(\w+)'\]\s*=\s*\{weight\s*=\s*([\d.]+)\}"
        abilities = {}

        for ability_match in re.finditer(ability_pattern, abilities_block):
            ability_name = ability_match.group(1)
            weight = float(ability_match.group(2))
            abilities[ability_name] = weight

        if abilities:
            heroes_spells[hero_id] = abilities

    return heroes_spells


def get_hero_display_name(hero_id):
    """从hero_id生成显示名称"""
    # npc_dota_hero_axe -> Axe
    # npc_dota_hero_crystal_maiden -> Crystal Maiden
    name = hero_id.replace('npc_dota_hero_', '')
    words = name.split('_')
    return ' '.join(word.capitalize() for word in words)


def guess_hero_attribute(hero_name):
    """猜测英雄主属性（简化版）"""
    # 这是一个简化的映射，实际应该从游戏数据中获取
    strength_heroes = [
        'abaddon', 'alchemist', 'axe', 'beastmaster', 'brewmaster', 'bristleback',
        'centaur', 'chaos_knight', 'clockwerk', 'dawnbreaker', 'doom_bringer',
        'dragon_knight', 'earth_spirit', 'earthshaker', 'elder_titan', 'huskar',
        'kunkka', 'legion_commander', 'life_stealer', 'lycan', 'magnus', 'marci',
        'mars', 'night_stalker', 'omniknight', 'phoenix', 'primal_beast', 'pudge',
        'sand_king', 'slardar', 'snapfire', 'spirit_breaker', 'sven', 'tidehunter',
        'timbersaw', 'tiny', 'treant', 'tusk', 'underlord', 'undying', 'wraith_king'
    ]

    agility_heroes = [
        'antimage', 'arc_warden', 'bloodseeker', 'bounty_hunter', 'broodmother',
        'clinkz', 'drow_ranger', 'ember_spirit', 'faceless_void', 'gyrocopter',
        'hoodwink', 'juggernaut', 'kez', 'luna', 'medusa', 'meepo', 'mirana',
        'monkey_king', 'morphling', 'naga_siren', 'nyx_assassin', 'pangolier',
        'phantom_assassin', 'phantom_lancer', 'razor', 'riki', 'shadow_fiend',
        'slark', 'sniper', 'spectre', 'templar_assassin', 'terrorblade', 'troll_warlord',
        'ursa', 'viper', 'weaver'
    ]

    # 其余为intelligence
    if hero_name in strength_heroes:
        return 'strength'
    elif hero_name in agility_heroes:
        return 'agility'
    else:
        return 'intelligence'


def guess_hero_roles(hero_name):
    """猜测英雄角色"""
    # 简化版，实际应该更详细
    role_map = {
        'axe': ['initiator', 'durable', 'disabler'],
        'crystal_maiden': ['support', 'disabler', 'nuker'],
        'antimage': ['carry', 'escape', 'nuker'],
        'invoker': ['carry', 'nuker', 'disabler', 'escape'],
        'pudge': ['disabler', 'initiator', 'durable'],
        'juggernaut': ['carry', 'pusher', 'escape'],
        'sniper': ['carry', 'nuker'],
        'lion': ['support', 'disabler', 'nuker'],
        'shadow_fiend': ['carry', 'nuker'],
        'mirana': ['carry', 'support', 'escape', 'nuker'],
    }

    return role_map.get(hero_name, ['carry'])


def generate_heroes_json(spell_list_path, output_path):
    """生成完整的heroes.json"""
    print("Parsing spell_list.lua...")
    heroes_spells = parse_spell_list(spell_list_path)

    print(f"Found {len(heroes_spells)} heroes")

    heroes_data = {}

    for hero_id, abilities in heroes_spells.items():
        hero_name = hero_id.replace('npc_dota_hero_', '')
        display_name = get_hero_display_name(hero_id)

        # 构建技能数据
        abilities_data = {}
        slot = 0
        for ability_name, weight in abilities.items():
            # 判断是否是大招
            is_ultimate = any(keyword in ability_name for keyword in [
                '_ultimate', 'black_hole', 'ravage', 'chronosphere', 'doom',
                'reaper_scythe', 'finger_of_death', 'laguna_blade'
            ])

            # 判断技能类型（简化）
            if 'passive' in ability_name or ability_name.endswith('_aura'):
                ability_type = 'passive'
                behavior = 'passive'
            elif any(word in ability_name for word in ['blink', 'leap', 'walk']):
                ability_type = 'no_target'
                behavior = 'self'
            else:
                ability_type = 'unit_target'
                behavior = 'enemy'

            abilities_data[ability_name] = {
                'slot': slot if not is_ultimate else 5,
                'type': ability_type,
                'behavior': behavior,
                'cast_range': 600,
                'cooldown': [16, 14, 12, 10] if not is_ultimate else [160, 140, 120],
                'mana_cost': [100, 110, 120, 130] if not is_ultimate else [200, 300, 400],
                'weight': weight,
                'ultimate': is_ultimate,
                'description': f"Ability: {ability_name}"
            }

            if not is_ultimate:
                slot += 1

        # 构建英雄数据
        heroes_data[hero_id] = {
            'name': display_name,
            'primary_attribute': guess_hero_attribute(hero_name),
            'roles': guess_hero_roles(hero_name),
            'abilities': abilities_data,
            'item_builds': {
                'pos_1': [
                    'item_tango', 'item_quelling_blade', 'item_wraith_band',
                    'item_power_treads', 'item_maelstrom', 'item_black_king_bar',
                    'item_manta', 'item_butterfly', 'item_satanic'
                ],
                'pos_2': [
                    'item_tango', 'item_bottle', 'item_null_talisman',
                    'item_arcane_boots', 'item_kaya', 'item_black_king_bar',
                    'item_octarine_core', 'item_shivas_guard'
                ],
                'pos_3': [
                    'item_tango', 'item_quelling_blade', 'item_bracer',
                    'item_phase_boots', 'item_vanguard', 'item_blade_mail',
                    'item_blink', 'item_heart', 'item_assault'
                ],
                'pos_4': [
                    'item_tango', 'item_clarity', 'item_ward_observer',
                    'item_magic_wand', 'item_tranquil_boots', 'item_glimmer_cape',
                    'item_force_staff', 'item_aghanims_shard'
                ],
                'pos_5': [
                    'item_tango', 'item_clarity', 'item_ward_observer',
                    'item_ward_sentry', 'item_magic_wand', 'item_arcane_boots',
                    'item_glimmer_cape', 'item_force_staff'
                ]
            },
            'skill_build': [1, 2, 1, 3, 1, 6, 1, 2, 2, 2, 6, 3, 3, 3, 6],
            'playstyle': {
                'early_game': f"Focus on farming and using abilities efficiently. {display_name} excels in the laning phase.",
                'mid_game': f"Join team fights and use {display_name}'s abilities to control the game.",
                'late_game': f"Position carefully and use {display_name}'s full potential in team fights.",
                'combos': [
                    f"Use abilities in sequence for maximum impact"
                ]
            }
        }

    # 生成完整JSON
    output_data = {
        'heroes': heroes_data,
        'item_data': {
            'item_blink': {'cost': 2250, 'category': 'mobility', 'active': True},
            'item_black_king_bar': {'cost': 4050, 'category': 'defensive', 'active': True},
            'item_blade_mail': {'cost': 2100, 'category': 'defensive', 'active': True},
            'item_force_staff': {'cost': 2200, 'category': 'mobility', 'active': True},
            'item_glimmer_cape': {'cost': 1950, 'category': 'defensive', 'active': True},
        }
    }

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated {output_path}")
    print(f"✓ Total heroes: {len(heroes_data)}")

    # 显示前10个英雄
    print("\nFirst 10 heroes:")
    for i, (hero_id, data) in enumerate(list(heroes_data.items())[:10], 1):
        print(f"  {i}. {data['name']} ({hero_id}) - {len(data['abilities'])} abilities")


if __name__ == '__main__':
    # 路径配置
    project_root = Path(__file__).parent.parent.parent
    spell_list_path = project_root / 'dota2bot-OpenHyperAI' / 'bots' / 'FunLib' / 'spell_list.lua'
    output_path = Path(__file__).parent / 'hero_knowledge' / 'heroes.json'

    if not spell_list_path.exists():
        print(f"Error: spell_list.lua not found at {spell_list_path}")
        print("Please check the path to dota2bot-OpenHyperAI project")
        exit(1)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成数据
    generate_heroes_json(spell_list_path, output_path)

    print("\n✅ All heroes data generated successfully!")
    print(f"Output: {output_path}")
