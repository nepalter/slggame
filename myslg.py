import random
from PyQt5.QtCore import QObject, pyqtSignal
from enemy_ai import Easy_EnemyAI

class Unit:
    def __init__(self, unit_type, max_hp, atk, movement, attack_range, name=None, skills=None, allegiance="player", has_moved=False, has_attacked=False):
        self.name = name if name else unit_type
        self.unit_type = unit_type
        self.max_hp = max_hp
        self.hp = max_hp  # Current HP starts at maximum HP
        self.atk = atk
        self.movement = movement
        self.attack_range = attack_range
        self.skills = []
        self.vision = 10 #no fog of war for now
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
        if self.skills:
            info += f"\nSkill:"
            for skill in self.skills:
                info += f"\n{skill.name}: {skill.description}"
        print(info)

    def attack(self, target):
        # Attack logic
        if target:
            target.hp -= self.atk
            print(f"{self.name} attacks {target.name} for {self.atk} damage. {target.name} has {target.hp} HP remaining.")

    def check_unit_defeated(self):
        return self.hp <= 0

class Skill:
    def __init__(self, name, damage, range, effect_type, cooldown, turns_until_ready = 0, description = ""):
        self.name = name
        self.damage = damage
        self.range = range
        self.effect_type = effect_type
        self.cooldown = cooldown
        self.turns_until_ready = turns_until_ready
        self.description = description

    def is_available(self):
        return self.turns_until_ready == 0

    def apply_effect(self, user, target):
        if self.effect_type == "damage":
            target.hp -= self.damage
        # Add other effect types like healing, buffs, etc.
        elif self.effect_type == "healing":
            target.hp += self.damage
        self.turns_until_ready = self.cooldown

class Passive_skill:
    def __init__(self, name, damage, range, effect_type, cooldown, turns_until_ready = 0, description = ""):
        self.name = name
        self.damage = damage
        self.range = range
        self.effect_type = effect_type
        self.cooldown = cooldown
        self.turns_until_ready = turns_until_ready
        self.description = description

    def is_available(self):
        return self.turns_until_ready == 0

    def apply_effect(self, user, target):
        if self.effect_type == "damage":
            target.hp -= self.damage
        # Add other effect types like healing, buffs, etc.
        elif self.effect_type == "healing":
            target.hp += self.damage
        self.turns_until_ready = self.cooldown   

class Buff:
    def __init__(self, name, align_type, effect_type, affect, turns, description = ""):
        self.name = name
        self.align_type = align_type
        self.effect_type = effect_type
        self.turns = turns
        self.affect = affect
        self.description = description

class BattleMap(QObject):
    game_over_signal = pyqtSignal(str) #signal to end the game

    def __init__(self, n, m, turn=1, territory="plain"):
        super().__init__()  # Properly initialize QObject
        self.rows = n
        self.columns = m
        self.grid = [[None for _ in range(m)] for _ in range(n)]
        self.enemy_ai = Easy_EnemyAI(self)
        self.turn = turn
        self.territory = territory
    
    def set_update_callback(self, callback):
        # Set the callback function for UI updates
        self.update_callback = callback

    def display_map(self):
        for row in self.grid:
            row_display = " | ".join(["." if cell is None else ("player" if cell.allegiance == "player" else "enemy") for cell in row])
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

    def able_to_attack(self, unit, start_x, start_y, target_x, target_y):
        # Check if there's an enemy unit at the target location
        if not unit:
            print("No unit selected!")
            return False

        if unit.has_attacked:
            print(f"{unit.name} has already attacked this turn!")
            return False
        target = self.grid[target_x][target_y]
        if target and target.allegiance != unit.allegiance:
            # Check if the target is within attack range
            distance = abs(target_x - start_x) + abs(target_y - start_y)
            if distance <= unit.attack_range:
                return True
            else:
                print("Target is out of attack range!")
                return False
        else:
            print("No enemy at the target location!")
            return False

    def attack_unit(self, unit, start_x, start_y, target_x, target_y):
        # Attack a target with the specified unit, if within range
        if self.able_to_attack(unit, start_x, start_y, target_x, target_y):
            target = self.grid[target_x][target_y]
            unit.attack(target)
            unit.has_attacked = True  # Set the has_attacked flag to True
            unit.has_moved = True # You cannot move after attacked.
            # function to check if unit is defeated  
            print(f"{target.name} defeated: {target.check_unit_defeated()}")       
            if target.check_unit_defeated():
                # Remove the target from the grid
                self.grid[target_x][target_y] = None
                print(f"{target.name} defeated!")
                if self.check_army_defeated(target.allegiance):
                    self.handle_gameover(target.allegiance)

    
    def use_skill(self, unit, skill, start_x, start_y, target_x, target_y):
        # Deploy a skill on a target.
        target = self.grid[target_x][target_y]
        if not target:
            print("No unit at the target location!")
            return False           

        if (target.allegiance != unit.allegiance and (skill.effect_type == "buff" or skill.effect_type == "heal")) \
        or (target.allegiance == unit.allegiance and (skill.effect_type == "debuff" or skill.effect_type == "attack")):
            print("Not a valid Target!")
            return False                      

        if skill.turns_until_ready > 0:
            print(f"Skill {skill.name} is on cooldown for {skill.turns_until_ready} turns.")
            return False

        # limit healing if units' hp is full
        if skill.effect_type == "heal" and target.hp >= target.max_hp:
            print(f"{target.name}'s HP is already full.")
            return False           

        distance = abs(start_x - target_x) + abs(start_y - target_y)  # Assuming grid coordinates
        if distance > skill.range:
            print(f"Target is out of range for skill {skill.name}.")
            return False

        # Apply the skill effect
        if skill.effect_type == "attack":
            damage = skill.damage
            target.hp -= damage
            print(f"{unit.name} used {skill.name} on {target.name}, dealing {damage} damage.")
        elif skill.effect_type == "heal": 
            heal_amount = skill.damage
            target.hp = min(target.max_hp , target.hp + heal_amount)
            print(f"{unit.name} used {skill.name} on {target.name}, heals {heal_amount} HP.")
        '''
        elif skill.effect_type == "buff": 
            buff = skill.buff
            target.buff.append(buff)
            print(f"{unit.name} used {skill.name} on {target.name}.")
        '''
        # Set the cooldown
        skill.turns_until_ready = skill.cooldown  # Assuming skills have a default cooldown value
        # Set unit complete its term
        unit.has_moved = True
        unit.has_attacked = True

    def end_turn(self):
        # End the player's turn, reset my units, and initiate enemy actions
        print("Ending turn. Resetting units and initiating enemy actions.")
        # Reset my units' movement and attack status
        self.reset_units_actions("player") # reset player's actions first for some skill to limit enemy action in next turn.

        # Enemy performs actions
        self.enemy_ai.execute_enemy_turn()
        # after enemy turn, check victory status
        self.check_army_defeated("player")
        print("Enemy's turn completed.")

        # Reset enemy units for the next turn
        self.reset_units_actions("enemy")
        self.turn += 1

        self.skill_cooldown() #decrement all units' skill's cooldown by 1

        print(f"Turn {self.turn}: Player's turn start.")

    def skill_cooldown(self):
        """Decreases the cooldown of all skills for every unit on the map."""
        for row in self.grid:
            for unit in row:
                if unit:  # Ensure there is a unit in the cell
                    for skill in unit.skills:
                        if skill.turns_until_ready > 0:
                            skill.turns_until_ready -= 1
                            print(f"Skill '{skill.name}' on unit '{unit.name}' cooldown decreased to {skill.turns_until_ready}.")


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
    
    def handle_gameover(self, allegiance):
        print (f"{allegiance} lost all units!")
        self.game_over_signal.emit(allegiance)
 
    
    def display_units(self):
        """Display all my units and their positions on the map."""
        for x in range(self.rows):
            for y in range(self.columns):
                unit = self.grid[x][y]
                if unit and unit.allegiance == "player":
                    print(f"{unit.name} at ({x}, {y}) - HP: {unit.hp}")
    
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
