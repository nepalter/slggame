from myslg import BattleMap, Unit

class GameCommands:
    def __init__(self, map_rows, map_columns):
        self.battle_map = BattleMap(map_rows, map_columns)
        self.units = []
        self.selected_unit = None
        self.update_callback = None  # This will hold the UI update function

    def set_update_callback(self, callback):
        # Set the callback function for UI updates
        self.update_callback = callback

    def move_selected_unit(self, unit, start_x, start_y, end_x, end_y):
        # Move the specified unit from its current position to the target coordinates if valid
        print(f"Attempting to move {unit.name} from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        if not unit:
            print("No unit selected!")
            return

        if unit.has_moved:
            print(f"{unit.name} has already moved this turn!")
            return

        # Check if the move is within the unit’s movement range
        move_distance = abs(start_x - end_x) + abs(start_y - end_y)
        if move_distance > unit.movement:
            print(f"Move is out of range! {unit.name} can move up to {unit.movement} spaces.")
            return

        # Ensure the target cell is empty
        if self.battle_map.grid[end_x][end_y] is not None:
            print("Cannot move to a cell that is already occupied!")
            return

        # Check if the path is clear (no enemies blocking the way)
        if not self.battle_map.is_path_clear(start_x, start_y, end_x, end_y, unit.allegiance):
            print("Path is blocked by an enemy unit!")
            return

        # Move the unit if all checks pass
        print(f"Moving {unit.name} from ({start_x}, {start_y}) to ({end_x}, {end_y}) on the grid.")
        self.battle_map.grid[end_x][end_y] = unit  # Place the unit at the destination
        self.battle_map.grid[start_x][start_y] = None  # Clear the starting cell
        #unit = self.battle_map.grid[end_x][end_y]
        unit.has_moved = True  # Set the has_moved flag to True
        print(f"Unit '{unit.name}' successfully moved to ({end_x}, {end_y}).")

        # Call the update callback after the move
        if self.update_callback:
            print("Calling update callback to refresh UI.")
            self.update_callback()

    def attack_with_selected_unit(self, unit, start_x, start_y, target_x, target_y):
        # Attack a target with the specified unit, if within range
        if not unit:
            print("No unit selected!")
            return

        if unit.has_attacked:
            print(f"{unit.name} has already attacked this turn!")
            return

        # Check if there's an enemy unit at the target location
        target = self.battle_map.grid[target_x][target_y]
        if target and target.allegiance == "enemy":
            # Check if the target is within attack range
            distance = abs(target_x - start_x) + abs(target_y - start_y)
            if distance <= unit.attack_range:
                unit.attack(target)
                unit.has_attacked = True  # Set the has_attacked flag to True
                if target.hp <= 0:
                    print(f"{target.name} defeated!")
                    self.battle_map.grid[target_x][target_y] = None  # Remove defeated unit from the map
                    self.check_for_defeat_or_victory()  # Check for game-ending conditions
                else:
                    print(f"{target.name} has {target.hp} HP remaining.")
            else:
                print("Target is out of attack range!")
        else:
            print("No enemy at the target location!")

        # Call the update callback after the attack
        if self.update_callback:
            print("Calling update callback to refresh UI.")
            self.update_callback()

    def end_turn(self):
        # End the player's turn, reset my units, and initiate enemy actions
        print("Ending turn. Resetting units and initiating enemy actions.")
        # Reset my units' movement and attack status
        self.reset_units_actions("my")

        # Enemy performs actions
        self.battle_map.auto_enemy_actions()
        print("Enemy's turn completed.")

        # Reset enemy units for the next turn
        self.reset_units_actions("enemy")

        # Call the update callback after ending the turn
        if self.update_callback:
            print("Calling update callback after end of turn to refresh UI.")
            self.update_callback()

        # Deselect any selected unit after turn ends
        self.selected_unit = None

    def reset_units_actions(self, allegiance):
        """Reset has_moved and has_attacked flags for all units of the specified allegiance."""
        for x in range(self.battle_map.rows):
            for y in range(self.battle_map.columns):
                unit = self.battle_map.grid[x][y]
                if unit and unit.allegiance == allegiance:
                    unit.has_moved = False
                    unit.has_attacked = False

    def check_army_defeated(self, allegiance):
        """Check if all units of the specified allegiance ('my' or 'enemy') are defeated."""
        for row in self.grid:
            for cell in row:
                if cell and cell.allegiance == allegiance:
                    return False  # Found a unit of the specified allegiance, army is not defeated
        return True  # No units found of the specified allegiance, army is defeated

    def display_units(self):
        """Display all my units and their positions on the map."""
        for x in range(self.battle_map.rows):
            for y in range(self.battle_map.columns):
                unit = self.battle_map.grid[x][y]
                if unit and unit.allegiance == "my":
                    print(f"{unit.name} at ({x}, {y}) - HP: {unit.hp}")

    def display_map(self):
        """Display the current battle map."""
        self.battle_map.display_map()

if __name__ == "__main__":
    # Initialize the game with a 5x5 map
    game = GameCommands(5, 5)

    # Add my and enemy units
    my_unit = Unit("Knight", 100, 20, 2, 1, "Knight", allegiance="my")
    enemy_unit = Unit("Goblin", 50, 10, 2, 1, "Goblin", allegiance="enemy")

    game.battle_map.add_unit(my_unit, 0, 0)
    game.battle_map.add_unit(enemy_unit, 3, 3)
    game.display_map()