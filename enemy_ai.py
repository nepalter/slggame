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
        # Updated movement and attack logic
        target = None
        closest_distance = float('inf')

        # Find the nearest target
        for dx in range(-unit.vision, unit.vision + 1):
            for dy in range(-unit.vision, unit.vision + 1):
                nx, ny = start_x + dx, start_y + dy
                if 0 <= nx < self.battle_map.rows and 0 <= ny < self.battle_map.columns:
                    target_unit = self.battle_map.grid[nx][ny]
                    if target_unit and target_unit.allegiance != "enemy":
                        distance = abs(dx) + abs(dy)
                        if distance < closest_distance:
                            closest_distance = distance
                            target = (nx, ny)

        # Move towards the target if not in range
        if target:
            target_x, target_y = target
            if closest_distance >= unit.attack_range:
                # Move closer to the target
                move_dx = 1 if target_x > start_x else -1 if target_x < start_x else 0
                move_dy = 1 if target_y > start_y else -1 if target_y < start_y else 0
                target_x, target_y = start_x + move_dx, start_y + move_dy

                if self.is_within_bounds(target_x, target_y) and self.battle_map.is_within_bounds(unit, start_x, start_y, target_x, target_y) and self.battle_map.grid[target_x][target_y] == None:
                    # Move the unit
                    self.battle_map.move_unit(unit, start_x, start_y, target_x, target_y)

            # Attack if in range
            if abs(target_x - start_x) + abs(target_y - start_y) <= unit.attack_range and self.battle_map.grid[target_x][target_y].allegiance != "enemy":
                self.battle_map.attack_unit(unit, start_x, start_y, target_x, target_y)

        # Otherwise, move to a random valid location
        if target and self.is_within_bounds(target_x, target_y) and self.battle_map.grid[target_x][target_y] == None:
            self.battle_map.move_unit(unit, start_x, start_y, target_x, target_y)

    def get_potential_moves(self, start_x, start_y, movement_range):
        # Get all possible moves within the unit's movement range
        potential_moves = []
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                if abs(dx) + abs(dy) <= movement_range:
                    potential_moves.append((start_x + dx, start_y + dy))
        return potential_moves

    def is_within_bounds(self, x, y):
        # Check if the given coordinates are within the map bounds
        return 0 <= x < self.battle_map.rows and 0 <= y < self.battle_map.columns