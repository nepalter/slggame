import random
from enemy_ai import Easy_EnemyAI

class Unit:
    def __init__(self, unit_type, max_hp, atk, movement, attack_range, name=None, skill=None, allegiance="my", has_moved=False, has_attacked=False):
        self.name = name if name else unit_type
        self.unit_type = unit_type
        self.max_hp = max_hp
        self.hp = max_hp  # Current HP starts at maximum HP
        self.atk = atk
        self.movement = movement
        self.attack_range = attack_range
        self.skill = skill
        self.allegiance = allegiance
        self.has_moved = False  # Track if unit has moved during the turn
        self.has_attacked = False  # Track if unit has attacked during the turn
    
    def display_info(self):
        """Displays the full information of the unit."""
        info = (
            f"Name: {self.name}\n"
            f"Type: {self.unit_type}\n"
            f"HP: {self.hp}/{self.max_hp}\n"  # Display current HP and max HP
            f"Attack: {self.atk}\n"
            f"Movement: {self.movement}\n"
            f"Attack Range: {self.attack_range}\n"
            f"Allegiance: {self.allegiance}"
        )
        if self.skill:
            info += f"\nSkill: {self.skill}"
        print(info)

    def attack(self, target):
        """Attacks another unit, reducing their HP."""
        target.hp -= self.atk
        print(f"{self.name} attacks {target.name} for {self.atk} damage. {target.name} now has {target.hp} HP.")

class BattleMap:
    def __init__(self, n, m):
        self.rows = n
        self.columns = m
        self.grid = [[None for _ in range(m)] for _ in range(n)]
        self.enemy_ai = Easy_EnemyAI(self)
    
    def set_update_callback(self, callback):
        # Set the callback function for UI updates
        self.update_callback = callback

    def display_map(self):
        for row in self.grid:
            row_display = " | ".join(["." if cell is None else ("M" if cell.allegiance == "my" else "E") for cell in row])
            print(row_display)
            print("-" * (4 * self.columns - 1))

    def add_unit(self, unit, x, y):
        if 0 <= x < self.rows and 0 <= y < self.columns:
            if self.grid[x][y] is None:
                self.grid[x][y] = unit
                print(f"Unit '{unit.name}' placed at ({x}, {y}).")
            else:
                print("Cell is already occupied!")
        else:
            print("Invalid coordinates!")

    
    def is_within_bounds(self, unit, start_x, start_y, end_x, end_y):
        # Check if the move is within the unit’s movement range
        if unit.has_moved:
            print(f"{unit.name} has already moved this turn!")
            return
        move_distance = abs(start_x - end_x) + abs(start_y - end_y)
        if move_distance > unit.movement:
            return False

        if 0 > end_x or end_x >= self.rows or 0 > end_y or end_y >= self.columns:
            return False

        # Ensure the target cell is empty
        if self.grid[end_x][end_y] is not None:
            return False

        # Check if the path is clear (no enemies blocking the way)
        if not self.is_path_clear(start_x, start_y, end_x, end_y, unit.allegiance):
            return False

        return True        
    
    def move_unit(self, unit, start_x, start_y, end_x, end_y):
        # Move the specified unit from its current position to the target coordinates if valid
        print(f"Attempting to move {unit.name} from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        if not unit:
            print("No unit selected!")
            return

        if not self.is_within_bounds(unit, start_x, start_y, end_x, end_y):
            print("Cannot move there!")
            return

        # Move the unit if all checks pass
        print(f"Moving {unit.name} from ({start_x}, {start_y}) to ({end_x}, {end_y}) on the grid.")
        self.grid[end_x][end_y] = unit  # Place the unit at the destination
        self.grid[start_x][start_y] = None  # Clear the starting cell
        #unit = self.grid[end_x][end_y]
        unit.has_moved = True  # Set the has_moved flag to True
        print(f"Unit '{unit.name}' successfully moved to ({end_x}, {end_y}).")

    def attack_unit(self, unit, start_x, start_y, target_x, target_y):
        # Attack a target with the specified unit, if within range
        if not unit:
            print("No unit selected!")
            return

        if unit.has_attacked:
            print(f"{unit.name} has already attacked this turn!")
            return

        # Check if there's an enemy unit at the target location
        target = self.grid[target_x][target_y]
        if target and target.allegiance == "enemy":
            # Check if the target is within attack range
            distance = abs(target_x - start_x) + abs(target_y - start_y)
            if distance <= unit.attack_range:
                unit.attack(target)
                unit.has_attacked = True  # Set the has_attacked flag to True
                unit.has_moved = True # You cannot move after attacked.
                if target.hp <= 0:
                    print(f"{target.name} defeated!")
                    self.grid[target_x][target_y] = None  # Remove defeated unit from the map
                    self.check_for_defeat_or_victory()  # Check for game-ending conditions
                else:
                    print(f"{target.name} has {target.hp} HP remaining.")
            else:
                print("Target is out of attack range!")
        else:
            print("No enemy at the target location!")

    def end_turn(self):
        # End the player's turn, reset my units, and initiate enemy actions
        print("Ending turn. Resetting units and initiating enemy actions.")
        # Reset my units' movement and attack status
        self.reset_units_actions("my")

        # Enemy performs actions
        self.enemy_ai.execute_enemy_turn()
        # after enemy turn, check victory status
        self.check_army_defeated("my")
        print("Enemy's turn completed.")

        # Reset enemy units for the next turn
        self.reset_units_actions("enemy")

    def reset_units_actions(self, allegiance):
        # Reset has_moved and has_attacked flags for all units of the specified allegiance.
        for x in range(self.rows):
            for y in range(self.columns):
                unit = self.grid[x][y]
                if unit and unit.allegiance == allegiance:
                    unit.has_moved = False
                    unit.has_attacked = False

    def check_army_defeated(self, allegiance):
        # Check if all units of the specified allegiance ('my' or 'enemy') are defeated.
        for row in self.grid:
            for cell in row:
                if cell and cell.allegiance == allegiance:
                    return False  # Found a unit of the specified allegiance, army is not defeated
        return True  # No units found of the specified allegiance, army is defeated
 
    def check_for_defeat_or_victory(self):
        if self.check_army_defeated("enemy"):
            print("Victory! All enemy units have been defeated.")
        elif self.check_army_defeated("my"):
            print("Defeat! All of your units have been defeated.")
 
    '''
    def display_units(self):
        """Display all my units and their positions on the map."""
        for x in range(self.rows):
            for y in range(self.columns):
                unit = self.grid[x][y]
                if unit and unit.allegiance == "my":
                    print(f"{unit.name} at ({x}, {y}) - HP: {unit.hp}")
    '''
    def display_map(self):
        """Display the current battle map."""
        self.display_map()    

    def is_path_clear(self, start_x, start_y, end_x, end_y, allegiance):
        x, y = start_x, start_y
        while (x, y) != (end_x, end_y):
            if x < end_x: x += 1
            elif x > end_x: x -= 1
            if y < end_y: y += 1
            elif y > end_y: y -= 1

            if (x, y) != (end_x, end_y) and self.grid[x][y] is not None:
                if self.grid[x][y].allegiance != allegiance:
                    return False
        return True

    def auto_enemy_actions(self):
        """Automatically moves and attacks with enemy units."""
        for x in range(self.rows):
            for y in range(self.columns):
                unit = self.grid[x][y]
                if unit and unit.allegiance == "enemy":
                    self.enemy_move_and_attack(unit, x, y)

    def enemy_move_and_attack(self, unit, x, y):
        # Simplified enemy movement towards the nearest ally
        for dx in range(-unit.movement, unit.movement + 1):
            for dy in range(-unit.movement, unit.movement + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.columns and self.grid[nx][ny] and self.grid[nx][ny].allegiance == "my":
                    unit.attack(self.grid[nx][ny])
                    return

