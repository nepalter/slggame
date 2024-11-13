from myslg import BattleMap, Unit  # Adjust imports to match your project structure

def basic_map():
    """Initialize a 5x5 map with a basic player and enemy unit setup."""
    battle_map = BattleMap(5, 5)
    player_unit = Unit("Knight", 100, 20, 2, 1, "Knight", allegiance="player")
    enemy_unit = Unit("Goblin", 50, 10, 2, 1, "Goblin", allegiance="enemy")
    battle_map.add_unit(player_unit, 0, 0)
    battle_map.add_unit(enemy_unit, 2, 2)
    return battle_map

def forest_map():
    """Initialize a 6x6 map with a more complex setup."""
    battle_map = BattleMap(6, 6)
    player_unit = Unit("Archer", 80, 15, 3, 2, "Archer", allegiance="player")
    enemy_unit_1 = Unit("Orc", 120, 25, 2, 1, "Orc", allegiance="enemy")
    enemy_unit_2 = Unit("Goblin", 50, 10, 2, 1, "Goblin", allegiance="enemy")
    battle_map.add_unit(player_unit, 1, 1)
    battle_map.add_unit(enemy_unit_1, 4, 4)
    battle_map.add_unit(enemy_unit_2, 3, 3)
    return battle_map

def desert_map():
    """Initialize an 8x8 map with several player and enemy units."""
    battle_map = BattleMap(8, 8)
    player_unit_1 = Unit("Cavalry", 120, 30, 4, 1, "Cavalry", allegiance="player")
    player_unit_2 = Unit("Mage", 60, 40, 2, 3, "Mage", allegiance="player")
    enemy_unit_1 = Unit("Sand Raider", 70, 15, 3, 1, "Raider", allegiance="enemy")
    enemy_unit_2 = Unit("Sand Raider", 70, 15, 3, 1, "Raider", allegiance="enemy")
    battle_map.add_unit(player_unit_1, 0, 7)
    battle_map.add_unit(player_unit_2, 7, 0)
    battle_map.add_unit(enemy_unit_1, 3, 4)
    battle_map.add_unit(enemy_unit_2, 5, 5)
    return battle_map