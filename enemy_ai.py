from random import choice
from collections import deque 

class Easy_EnemyAI:
    def __init__(self, battle_map):
        self.battle_map = battle_map

    def execute_enemy_turn(self):
        # Iterate through all cells in the battle map to find enemy units
        occupied_positions = []
        for x in range(self.battle_map.rows):
            for y in range(self.battle_map.columns):
                unit = self.battle_map.grid[x][y]
                if unit:
                    occupied_positions.append((x, y))
        
        # Iterate through occupied positions and process enemy units
        for x, y in occupied_positions:
            unit = self.battle_map.grid[x][y]
            if unit and unit.allegiance == "enemy":
                self.move_and_attack(unit, x, y, occupied_positions)

    def move_and_attack(self, unit, start_x, start_y, occupied_positions):
        # Updated movement and attack logic
        target = None
        # move_and_attack_range = unit.movement + unit.attack_range
        chosen_enemy = []

        # find available enemy to attack
        for x,y in occupied_positions:
            unit_in_block = self.battle_map.grid[x][y]
            if unit_in_block and self.battle_map.is_within_bounds(unit,start_x,start_y,x,y) and unit_in_block.allegiance != "enemy":
                target=(x,y)
                chosen_enemy.append(target)
        if chosen_enemy:
            print(f"Enemy: {occupied_positions},{chosen_enemy}")
        else: # find nearest enemy
            # No enemies within range; find the closest enemy
            closest_distance = float('inf')
            closest_unit = None

            for x,y in occupied_positions:
                unit_in_block = self.battle_map.grid[x][y]
                if unit_in_block and unit_in_block.allegiance != "enemy":
                    print(f"enemy's target:{unit_in_block.name}")
                    distance = abs(x - start_x) + abs(y - start_y)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_unit = (x, y)

            if closest_unit:
                chosen_enemy.append(closest_unit)


        # move and attack the nearest enemy
        if chosen_enemy:                
            x,y = chosen_enemy[0] # for simple AI, find the first one in range
            if self.battle_map.able_to_attack(unit, start_x, start_y, x, y): # if don't need to move
                print(f"enemy going to attack :{unit.name}")
                self.battle_map.attack_unit(unit, start_x, start_y, x, y)
            else: #move closer to that unit and try to attack
                nearest_block = self.find_nearest_reachable_block(start_x, start_y, x, y, unit.movement, unit.attack_range, occupied_positions)
                if nearest_block:
                    dx, dy = nearest_block
                    print(f"enemy going to move close:{unit.name}")
                    self.battle_map.move_unit(unit, start_x, start_y, dx, dy)
                    self.battle_map.attack_unit(unit, dx, dy, x, y)        

    def is_within_bounds(self, new_position):
        # Check if the given coordinates are within the map bounds
        return 0 <= new_position[0] < self.battle_map.rows and 0 <= new_position[1] < self.battle_map.columns
    
    def find_nearest_reachable_block(self, start_x, start_y, target_x, target_y, movement_range, attack_range, occupied_positions):
        
        def distance(current_position, target):
            """Calculate Manhattan distance between two positions."""
            return abs(target[0] - current_position[0]) + abs(target[1] - current_position[1])

        enemy_position = (target_x,target_y)
        unit_position = (start_x, start_y)
        # Initialize BFS for finding reachable positions within movement range
        queue = deque([(unit_position, 0)])
        visited = set([unit_position])
        best_move = None
        farthest_distance = 9999999  # Track the farthest valid block within movement range

        while queue:
            current_position, current_distance = queue.popleft()
            
            # Check if we've reached maximum movement range
            if current_distance > movement_range:
                continue
            
            # Check if within attack range of the target
            if distance(current_position, enemy_position) <= attack_range:
                return current_position  # Return immediately if a block to attack is found
            
            # Update the best move if closer to the target and within bounds
            target_distance = distance(current_position, enemy_position)
            if target_distance < distance(unit_position, enemy_position) and target_distance < farthest_distance:
                best_move = current_position
                farthest_distance = target_distance
            
            # Explore neighbors within bounds and not occupied
            x, y = current_position
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_position = (x + dx, y + dy)
                if new_position not in visited and self.is_within_bounds(new_position) and new_position not in occupied_positions:
                    visited.add(new_position)
                    queue.append((new_position, current_distance + 1))
        
        # If no attack position was found, return the best available move to approach the target
        return best_move