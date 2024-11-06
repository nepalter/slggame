import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, QDialog, QTextEdit
from PyQt5.QtCore import Qt
from myslg import BattleMap, Unit
from commands import GameCommands


class UnitActionDialog(QDialog):
    def __init__(self, unit, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.setWindowTitle(f"{unit.name} Actions")


        # Create a layout for the dialog
        self.dialog_layout = QVBoxLayout()


        # Display unit status
        self.unit_status = QTextEdit()
        self.unit_status.setReadOnly(True)
        self.unit_status.setPlainText(f"Name: {unit.name}\nHP: {unit.hp}/{unit.max_hp}\nAttack: {unit.atk}\n"
                                      f"Movement: {unit.movement}\nRange: {unit.attack_range}\nAllegiance: {unit.allegiance}")
        self.dialog_layout.addWidget(self.unit_status)


        # Action buttons
        self.move_button = QPushButton("Move")
        self.attack_button = QPushButton("Attack")
        self.wait_button = QPushButton("Wait")
        self.cancel_button = QPushButton("Cancel")

        # Add buttons to the layout
        if(unit.allegiance=="my"):
            self.dialog_layout.addWidget(self.move_button)
            self.dialog_layout.addWidget(self.attack_button)
            self.dialog_layout.addWidget(self.wait_button)
        
        self.dialog_layout.addWidget(self.cancel_button)

        # Set layout to the dialog
        self.setLayout(self.dialog_layout)


        # Define actions, connecting each to the corresponding slot
        self.move_button.clicked.connect(lambda: self.accept_action("move"))
        self.attack_button.clicked.connect(lambda: self.accept_action("attack"))
        self.wait_button.clicked.connect(self.wait_unit)
        self.cancel_button.clicked.connect(self.cancel)

    def accept_action(self, action_type):
        self.accept()
        self.parent().start_action_selection(action_type, self.unit)

    def wait_unit(self):
        self.unit.has_moved = True
        self.unit.has_attacked = True
        self.done(0)
        print(self.unit.name + " wait in this turn.")

    def cancel(self):
        self.done(0)

class MapDisplay(QWidget):
    def __init__(self, battle_map, game_commands):
        super().__init__()
        self.battle_map = battle_map
        self.game_commands = game_commands
        self.selected_unit = None
        self.action_type = None
        self.highlighted_cells = []



        # Set the update callback to refresh the map after each action
        self.game_commands.set_update_callback(self.update_map_display)


        # Initialize the UI layout
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("Battle Map")
        self.layout = QVBoxLayout()
       
        # Create a grid layout for the map
        self.grid_layout = QGridLayout()
        self.update_map_display()
       
        # End Turn button
        end_turn_button = QPushButton("End Turn")
        end_turn_button.clicked.connect(self.end_turn)


        self.layout.addLayout(self.grid_layout)
        self.layout.addWidget(end_turn_button)
        self.setLayout(self.layout)




    def update_map_display(self, highlight_range=False, range_value=0, origin_x=None, origin_y=None):
        # Clear existing widgets in the grid layout without setting it again
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


        # Populate the grid layout based on the battle map
        for row in range(self.battle_map.rows):
            for col in range(self.battle_map.columns):
                unit = self.battle_map.grid[row][col]
                if unit:
                    cell_text = f"{unit.name}\nHP: {unit.hp}/{unit.max_hp}\n{unit.allegiance}"
                    color = "lightblue" if unit.allegiance == "my" else "lightcoral"
                else:
                    cell_text = "Empty"
                    color = "lightgrey"

                label = QLabel(cell_text)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet(f"background-color: {color}; border: 1px solid black; padding: 5px;")
                label.setFixedSize(100, 100)


                # Check if we should highlight cells in range
                if highlight_range and self.is_within_range(origin_x, origin_y, row, col, range_value):
                    label.setStyleSheet("background-color: lightgreen; border: 1px solid black; padding: 5px;")
                    self.highlighted_cells.append((label, row, col))


                # Add click event
                label.mousePressEvent = lambda event, row=row, col=col: self.cell_clicked(event, row, col)


                # Add the label to the grid layout
                self.grid_layout.addWidget(label, row, col)



    def cell_clicked(self, event, row, col):
        if self.action_type == "move":
            self.handle_move_click(row, col)
        elif self.action_type == "attack":
            self.handle_attack_click(row, col)
        else:
            unit = self.battle_map.grid[row][col]
            if event.button() == Qt.LeftButton and unit:
                self.selected_unit = unit
                self.show_unit_action_dialog(unit)


    def show_unit_action_dialog(self, unit):
        dialog = UnitActionDialog(unit, self)
        dialog.exec_()


    def start_action_selection(self, action_type, unit):
        self.action_type = action_type
        self.selected_unit = unit
        start_x, start_y = self.find_unit_position(unit)
        range_value = unit.movement if action_type == "move" else unit.attack_range
        self.update_map_display(highlight_range=True, range_value=range_value, origin_x=start_x, origin_y=start_y)


    def handle_move_click(self, row, col):
        start_x, start_y = self.find_unit_position(self.selected_unit)
        if self.is_within_range(start_x, start_y, row, col, self.selected_unit.movement):
            self.battle_map.move_unit(self.selected_unit, start_x, start_y, row, col)
            self.clear_highlight()
            self.update_map_display()
        else:
            QMessageBox.warning(self, "Out of Range", "Selected block is out of range. Reopening action dialog.")
            self.clear_highlight()
            self.show_unit_action_dialog(self.selected_unit)


    def handle_attack_click(self, row, col):
        start_x, start_y = self.find_unit_position(self.selected_unit)
        if self.is_within_range(start_x, start_y, row, col, self.selected_unit.attack_range):
            self.battle_map.attack_unit(self.selected_unit, start_x, start_y, row, col)
            self.clear_highlight()
            self.update_map_display()
        else:
            QMessageBox.warning(self, "Out of Range", "Selected block is out of range. Reopening action dialog.")
            self.clear_highlight()
            self.show_unit_action_dialog(self.selected_unit)


    def is_within_range(self, start_x, start_y, target_x, target_y, range_value):
        return abs(start_x - target_x) + abs(start_y - target_y) <= range_value


    def clear_highlight(self):
        self.action_type = None
        self.highlighted_cells.clear()


    def find_unit_position(self, unit):
        for x in range(self.battle_map.rows):
            for y in range(self.battle_map.columns):
                if self.battle_map.grid[x][y] == unit:
                    return x, y
        return None, None


    def end_turn(self):
        # End the turn for the player and initiate enemy actions.
        self.battle_map.end_turn()
        self.update_map_display()  # Refresh the map after the turn ends


def main():
    app = QApplication(sys.argv)
    battle_map = BattleMap(5, 5)
    game_commands = GameCommands(5, 5)
    my_unit = Unit("Knight", 100, 20, 2, 1, "Knight", allegiance="my")
    enemy_unit = Unit("Goblin", 50, 10, 2, 1, "Goblin", allegiance="enemy")
   
    battle_map.add_unit(my_unit, 2, 1)
    battle_map.add_unit(enemy_unit, 2, 2)


    window = MapDisplay(battle_map, game_commands)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

