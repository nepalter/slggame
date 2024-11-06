from random import choice

class Easy_EnemyAI:
    def __init__(self, battle_map):
        self.battle_map = battle_map

    def execute_enemy_turn(self):
        # Iterate through all cells in the battle map to find enemy units
        for x in range(self.battle_map.rows):
            for y in range(self.battle_map.columns):
                unit = self.battle_map.grid[x][y]
                if unit and unit.allegiance == "enemy":
                    self.move_and_attack(unit, x, y)

    def move_and_attack(self, unit, start_x, start_y):
        # Get potential moves within the unit's movement range
        potential_moves = self.get_potential_moves(start_x, start_y, unit.movement)
        target_move = None
        target_attack = None

        # Determine if there are any enemy units nearby to attack
        for move in potential_moves:
            target_x, target_y = move
            if self.battle_map.is_within_bounds(target_x, target_y):
                target_unit = self.battle_map.grid[target_x][target_y]
                if target_unit and target_unit.allegiance == "my":
                    target_attack = (target_x, target_y)
                    break
                elif target_unit is None:
                    target_move = move

        # Attack if an enemy unit is in range
        if target_attack:
            target_x, target_y = target_attack
            print(f"{unit.name} at ({start_x}, {start_y}) attacks enemy at ({target_x}, {target_y})")
            unit.attack(self.battle_map.grid[target_x][target_y])
            return

        # Otherwise, move to a random valid location
        if target_move:
            end_x, end_y = target_move
            print(f"{unit.name} moves from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            self.battle_map.grid[end_x][end_y] = unit
            self.battle_map.grid[start_x][start_y] = None
            unit.has_moved = True

    def get_potential_moves(self, start_x, start_y, movement_range):
        # Get all possible moves within the unit's movement range
        potential_moves = []
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                if abs(dx) + abs(dy) <= movement_range:
                    potential_moves.append((start_x + dx, start_y + dy))
        return potential_moves
