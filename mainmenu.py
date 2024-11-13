import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QDialog, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from game_interface import MapDisplay  # Import the main game interface
from battle_maps import *

class MapSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Battle Map")
        self.setFixedSize(300, 200)

        # Layout for map options
        layout = QVBoxLayout()

        # Map options using radio buttons
        self.map_options = QButtonGroup(self)
        basic_map_button = QRadioButton("Basic Map")
        forest_map_button = QRadioButton("Forest Map")
        desert_map_button = QRadioButton("Desert Map")

        # Adding buttons to layout and button group
        layout.addWidget(basic_map_button)
        layout.addWidget(forest_map_button)
        layout.addWidget(desert_map_button)
        self.map_options.addButton(basic_map_button)
        self.map_options.addButton(forest_map_button)
        self.map_options.addButton(desert_map_button)
        
        # Confirm button
        confirm_button = QPushButton("Start Game")
        confirm_button.clicked.connect(self.accept)  # Close dialog on confirm
        layout.addWidget(confirm_button)

        # Set default selection and layout
        basic_map_button.setChecked(True)
        self.setLayout(layout)

    def get_selected_map(self):
        """Returns the selected map function based on user choice."""
        selected_button = self.map_options.checkedButton().text()
        if selected_button == "Basic Map":
            return basic_map
        elif selected_button == "Forest Map":
            return forest_map
        elif selected_button == "Desert Map":
            return desert_map

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setFixedSize(400, 300)

        # Set up layout
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Game Main Menu")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # New Game button
        new_game_button = QPushButton("New Game")
        new_game_button.clicked.connect(self.show_map_selection_dialog)
        layout.addWidget(new_game_button)

        # Load Game button
        load_game_button = QPushButton("Load Game")
        load_game_button.clicked.connect(self.load_game)
        layout.addWidget(load_game_button)

        # Settings button
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)

        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.exit_game)
        layout.addWidget(exit_button)

        # Set layout to the main window
        self.setLayout(layout)

    def show_map_selection_dialog(self):
        """Open the map selection dialog to choose a battle map."""
        dialog = MapSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_map_function = dialog.get_selected_map()
            self.start_new_game(selected_map_function)

    def start_new_game(self, selected_map_function):
        """Start a new game with the selected map."""
        self.hide()  # Hide main menu
        battle_map = selected_map_function()  # Initialize the selected map
        self.game_interface = MapDisplay(battle_map)  # Pass the map to the game interface
        self.game_interface.show()
        

    def load_game(self):
        QMessageBox.information(self, "Load Game", "Loading game...")
        # Logic for loading a saved game can be added here

    def open_settings(self):
        QMessageBox.information(self, "Settings", "Opening settings...")
        # Logic to open settings window can go here

    def exit_game(self):
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to exit?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

# Running the main menu
if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())