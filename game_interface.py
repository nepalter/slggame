import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, QDialog, QTextEdit,  QRadioButton, QButtonGroup,  QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from myslg import BattleMap, Unit, Skill, Passive_skill

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
        self.skill_button = QPushButton("Skill")
        self.wait_button = QPushButton("Wait")
        self.cancel_button = QPushButton("Cancel")

        # Add buttons to the layout
        if(unit.allegiance == "player"):
            if(unit.has_moved == False):
                self.dialog_layout.addWidget(self.move_button)
            if(unit.has_attacked == False):           
                self.dialog_layout.addWidget(self.attack_button)
                if(unit.skills):
                    self.dialog_layout.addWidget(self.skill_button)
                self.dialog_layout.addWidget(self.wait_button)
        
        self.dialog_layout.addWidget(self.cancel_button)

        # Set layout to the dialog
        self.setLayout(self.dialog_layout)


        # Define actions, connecting each to the corresponding slot
        self.move_button.clicked.connect(lambda: self.accept_action("move"))
        self.attack_button.clicked.connect(lambda: self.accept_action("attack"))
        self.skill_button.clicked.connect(lambda: self.open_skill_selection_dialog(unit))
        self.wait_button.clicked.connect(self.wait_unit)
        self.cancel_button.clicked.connect(self.cancel)

    def accept_action(self, action_type):
        self.accept()
        self.parent().start_action_selection(action_type, self.unit)

    def open_skill_selection_dialog(self, unit):
        #Opens the skill selection dialog for the given unit.
        if not unit.skills:
            QMessageBox.information(self, "No Skills", f"{unit.name} has no skills available.")
            return

        dialog = SkillSelectionDialog(unit, self)
        if dialog.show():  # Check if the dialog was accepted
            selected_skill = dialog.selected_skill
            if selected_skill:
                # Perform actions with the selected skill, e.g., deploy it
                self.use_selected_skill(unit, selected_skill)
        

    def use_selected_skill(self, unit, skill):
        """Executes the selected skill."""
        # Implement the logic to use the skill (damage, effects, etc.)
        self.accept() #hide menu
        self.parent().start_action_selection("skill", unit, played_skill=skill)

    def wait_unit(self):
        self.unit.has_moved = True
        self.unit.has_attacked = True
        self.done(0)
        print(self.unit.name + " wait in this turn.")

    def cancel(self):
        self.done(0)

class SkillSelectionDialog(QDialog):
    def __init__(self, unit, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Skill")
        self.setFixedSize(300, 200)
        self.unit = unit
        self.selected_skill = None

        # Layout for skill options
        layout = QVBoxLayout()

        # Display unit name
        layout.addWidget(QLabel(f"Select a skill for {unit.name}:"))

        # Skill options using radio buttons
        self.skill_options = QButtonGroup(self)
        for skill in unit.skills:
            skill_button = QRadioButton(f"{skill.name} (Cooldown: {skill.cooldown})")
            skill_button.skill = skill  # Attach skill data to button
            layout.addWidget(skill_button)
            self.skill_options.addButton(skill_button)

        # OK and Cancel buttons
        button_layout = QVBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept_selection)
        cancel_button.clicked.connect(self.reject_selection)

        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def accept_selection(self):
        selected_button = self.skill_options.checkedButton()
        if selected_button:
            self.selected_skill = selected_button.skill
            print(f"Selected skill: {self.selected_skill.name}")
            # Perform actions with the selected skill, e.g., deploy it
            self.accept()
            self.parent().use_selected_skill(self.unit, self.selected_skill)

    def reject_selection(self):
        self.selected_skill = None
        self.reject()

# Show events of game
class Logger:
    def __init__(self, text_edit_widget):
        self.widget = text_edit_widget

    def write(self, message):
        self.widget.append(message.strip())  # Append and strip unnecessary newlines

    def flush(self):
        pass  # Compatibility with stdout

class MapDisplay(QWidget):
    return_to_main_menu_signal = pyqtSignal()
    def __init__(self, battle_map):
        super().__init__()        
        self.battle_map = battle_map
        self.selected_unit = None
        self.action_type = None
        self.selected_skill = None
        self.highlighted_cells = []

        # Show gameover popup if condition is met
        self.battle_map.game_over_signal.connect(self.gameover_popup)

        # Show notifications
        self.battle_map.notification_signal.connect(self.notification_popup)


        # Set the update callback to refresh the map after each action
        self.battle_map.set_update_callback(self.update_map_display)


        # Initialize the UI layout
        self.init_ui()

        # set background image
        image = os.path.join(os.path.dirname(__file__), "images", "background", f"{battle_map.territory}.png")
        self.set_background_image(image)
        
        print(f"Battleground: {battle_map.territory}")
        print(f"Good Luck!")        


    def init_ui(self):
        self.setWindowTitle("Battle Map")
        # Main layout: horizontal layout for map and log
        self.main_layout = QHBoxLayout(self)

        # Left side: Map layout
        self.map_layout = QVBoxLayout()

        # Create the map display area
        self.grid_layout = QGridLayout()
        self.map_layout.addLayout(self.grid_layout)
        self.update_map_display()

        # Add "End Turn" button
        end_turn_button = QPushButton("End Turn")
        end_turn_button.clicked.connect(self.end_turn)
        self.map_layout.addWidget(end_turn_button)

        # Add map layout to the main layout
        self.main_layout.addLayout(self.map_layout)

        # Right side: Log widget
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setStyleSheet("background-color: #f0f0f0;")
        self.main_layout.addWidget(self.log_widget, stretch=1)

        # Redirect stdout to log widget
        logger = Logger(self.log_widget)
        sys.stdout = logger
    def set_background_image(self, image_path):
        # Create a QLabel for the background image
        self.background_label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)  # Adjust image to fit the widget size
        self.background_label.resize(self.size())  # Cover the widget
        self.background_label.lower()  # Send to the bottom layer
        # print(f"Background image set to {image_path}")

    def resizeEvent(self, event):
        super(MapDisplay, self).resizeEvent(event)
        # Ensure the background resizes with the window
        self.background_label.resize(self.size())


    def update_map_display(self, action_type="other", highlight_range=False, range_value=0, origin_x=None, origin_y=None, using_skill=None):
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
                    # Check unit status and apply appropriate colors
                    if unit.has_moved and unit.has_attacked:
                        if unit.allegiance == "player":
                            color = "rgba(0, 0, 139, 150)"  # Dark Blue Transparency
                        else:
                            color = "rgba(139, 0, 0, 150)"  # Dark Red Transparency
                    else:
                        color = "rgba(173, 216, 230, 150)" if unit.allegiance == "player" else "rgba(240, 128, 128, 150)"
                else:
                    cell_text = ""
                    color = "rgba(211, 211, 211, 100)"  # Light grey with transparency

                label = QLabel(cell_text)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet(f"background-color: {color}; border: 1px solid black; padding: 5px;")
                label.setFixedSize(100, 100)


                # Check if we should highlight cells in range
                if highlight_range and self.is_within_range(origin_x, origin_y, row, col, range_value):
                    if action_type == "move":
                        label.setStyleSheet("background-color: rgba(144, 238, 144, 150); border: 1px solid black; padding: 5px;")
                    elif action_type == "attack":
                        label.setStyleSheet("background-color: rgba(255, 182, 193, 150); border: 1px solid black; padding: 5px;")
                    else:
                        label.setStyleSheet("background-color: rgba(173, 216, 230, 150); border: 1px solid black; padding: 5px;")
                    self.highlighted_cells.append((label, row, col))


                # Add click event
                label.mousePressEvent = lambda event, row=row, col=col: self.cell_clicked(event, row, col, skill=using_skill)


                # Add the label to the grid layout
                self.grid_layout.addWidget(label, row, col)



    def cell_clicked(self, event, row, col, skill=None):
        if self.action_type == "move":
            self.handle_move_click(row, col)
        elif self.action_type == "attack":
            self.handle_attack_click(row, col)
        elif self.action_type == "skill":
            self.handle_skill_click(row, col, skill)            
        else:
            unit = self.battle_map.grid[row][col]
            if event.button() == Qt.LeftButton and unit:
                self.selected_unit = unit
                self.show_unit_action_dialog(unit)


    def show_unit_action_dialog(self, unit):
        dialog = UnitActionDialog(unit, self)
        dialog.show()


    def start_action_selection(self, action_type, unit, played_skill=None):
        self.action_type = action_type
        self.selected_unit = unit
        start_x, start_y = self.find_unit_position(unit)
        if action_type == "move":
            range_value = unit.movement 
        elif action_type == "attack":
            range_value = unit.attack_range
        elif action_type == "skill":
            range_value = played_skill.range
        self.update_map_display(action_type=action_type, highlight_range=True, range_value=range_value, origin_x=start_x, origin_y=start_y, using_skill=played_skill)


    def handle_move_click(self, row, col):
        start_x, start_y = self.find_unit_position(self.selected_unit)
        if self.is_within_range(start_x, start_y, row, col, self.selected_unit.movement):
            self.battle_map.move_unit(self.selected_unit, start_x, start_y, row, col)
            self.clear_highlight()
            self.update_map_display()
        else:
            QMessageBox.warning(self, "Out of Range", "Selected block is out of range.")
            self.clear_highlight()
            self.update_map_display()
            # self.show_unit_action_dialog(self.selected_unit)


    def handle_attack_click(self, row, col):
        start_x, start_y = self.find_unit_position(self.selected_unit)
        if self.is_within_range(start_x, start_y, row, col, self.selected_unit.attack_range):
            self.battle_map.attack_unit(self.selected_unit, start_x, start_y, row, col)
            self.clear_highlight()
            self.update_map_display()
        else:
            QMessageBox.warning(self, "Out of Range", "Selected block is out of range.")
            self.clear_highlight()
            self.update_map_display()
            # self.show_unit_action_dialog(self.selected_unit)

    def handle_skill_click(self, row, col, skill=None):
        start_x, start_y = self.find_unit_position(self.selected_unit)
        if self.is_within_range(start_x, start_y, row, col, skill.range):
            self.battle_map.use_skill(self.selected_unit, skill, start_x, start_y, row, col)
            self.clear_highlight()
            self.update_map_display()
        else:
            QMessageBox.warning(self, "Out of Range", "Selected block is out of range.")
            self.clear_highlight()
            self.update_map_display()
            # self.show_unit_action_dialog(self.selected_unit)


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

    def gameover_popup(self, alligence):
        # Show a popup with the result and return to the main menu.
        if alligence == "enemy":
            QMessageBox.information(self, "Game Over", "You Win!", QMessageBox.Ok)
        elif alligence == "player":
            QMessageBox.information(self, "Game Over", "You Lose!", QMessageBox.Ok)
        self.return_to_main_menu()

    def notification_popup(self, message):
        # Display a pop-up with the notification message
        QMessageBox.warning(self, "Notification", message)

    def return_to_main_menu(self):
        # Return to the main menu.
        self.close()  # Close the current window
        self.return_to_main_menu_signal.emit()


def main():
    app = QApplication(sys.argv)
    battle_map = BattleMap(5, 5)
    my_unit = Unit("Knight", 100, 20, 2, 1, "Knight", allegiance="player")
    enemy_unit = Unit("Goblin", 50, 10, 2, 1, "Goblin", allegiance="enemy")
   
    battle_map.add_unit(my_unit, 0, 0)
    battle_map.add_unit(enemy_unit, 2, 2)


    window = MapDisplay(battle_map)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

