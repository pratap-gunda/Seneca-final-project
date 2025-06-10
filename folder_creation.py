import os
import re
import shutil
import subprocess
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QWidget, 
                               QPushButton, 
                               QVBoxLayout, 
                               QHBoxLayout, QLabel, 
                               QListWidget, 
                               QMessageBox, 
                               QLineEdit, 
                               QFileDialog,
                               QInputDialog,
                               QDialogButtonBox,
                               QPlainTextEdit,
                               QDialog)

class ProjectInputDialog(QInputDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Project Title")
        self.setLabelText("Project Title:")
        self.setInputMode(QInputDialog.TextInput)


class ExistingScriptDialog(QDialog):
    def __init__(self, script_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Script Already Exists")
        
        self.layout = QVBoxLayout()

        self.message_label = QLabel(f"The script already exists in the following path:\n{script_path}", self)
        self.layout.addWidget(self.message_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

        self.setLayout(self.layout)

class FolderCreationApp(QWidget):
    def __init__(self, parent=None):
        super(FolderCreationApp, self).__init__(parent)
        self.setWindowTitle("Project Manager")
        self.setGeometry(100, 100, 400, 200)
        self.project_name = None        
        
        # Source footage folder
        self.footage_path_edit = QLineEdit()
        self.footage_path_edit.setPlaceholderText("Select path of the footages...")
        self.footage_browse_button = QPushButton("Browse")
        self.footage_browse_button.setFixedSize(70, 35)
        self.footage_browse_button.clicked.connect(self.browse_footage_path)
        
        footage_path_layout = QHBoxLayout()
        footage_path_layout.addWidget(self.footage_path_edit)
        footage_path_layout.addWidget(self.footage_browse_button)
        
        # Target project folder
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("Select path to create your project...")
        self.project_browse_button = QPushButton("Browse")
        self.project_browse_button.setFixedSize(70, 35)
        self.project_browse_button.clicked.connect(self.browse_project_path)

        project_path_layout = QHBoxLayout()
        project_path_layout.addWidget(self.project_path_edit)
        project_path_layout.addWidget(self.project_browse_button)

        self.info_label = QLabel()
        
        self.create_folders_button = QPushButton("Create Project")
        self.copy_footage_button = QPushButton("Copy Footage")
        self.load_script_button = QPushButton("Load Script")

        self.create_folders_button.clicked.connect(self.create_folders)
        self.copy_footage_button.clicked.connect(self.copy_footage)
        self.load_script_button.clicked.connect(self.load_script)

        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.create_folders_button)
        btn_layout.addWidget(self.copy_footage_button)
        # btn_layout.addWidget(self.load_script_button)
        
        layout = QVBoxLayout()
        layout.addLayout(footage_path_layout)
        layout.addLayout(project_path_layout)
        layout.addLayout(btn_layout)

        self.shot_list_widget = QListWidget()
        # self.populate_shot_list()
        layout.addWidget(self.shot_list_widget)
        layout.addWidget(self.load_script_button)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        
        # Load the stylesheet
        style_file = './style.qss'
        with open(style_file, 'r') as f:
            self.setStyleSheet(f.read())

    def showInputDialog(self):
        input_dialog = ProjectInputDialog(self)
        if input_dialog.exec() == QInputDialog.Accepted:
            self.project_name = input_dialog.textValue()
        return self.project_name

    def browse_footage_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "Select footage folder")
        if selected_path:
            self.footage_path_edit.setText(selected_path)
            
    def browse_project_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "Select a folder to create your project")
        if selected_path:
            self.project_path_edit.setText(selected_path)

    def create_folders(self):
        project_base_folder = self.project_path_edit.text()

        if not project_base_folder:
            self.info_label.setText("Please select a project folder.")
            return
        self.project_name = self.showInputDialog()
        project_folder = os.path.join(project_base_folder, self.project_name)

        try:
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)
                self.info_label.setText("Folders created successfully.")
            else:
                self.info_label.setText(f"{project_folder} already exists.")
                
            footage_list = self.get_footage_list()
            for footage in footage_list:
                shot_footage_folder = os.path.join(project_folder, footage)

                if not os.path.exists(shot_footage_folder):
                    os.makedirs(shot_footage_folder)

                    os.makedirs(os.path.join(shot_footage_folder, "input_footage"))
                    renders_folder = os.path.join(shot_footage_folder, "renders")
                    os.makedirs(renders_folder)

                    os.makedirs(os.path.join(renders_folder, "lighting"))

                    os.makedirs(os.path.join(shot_footage_folder, "scripts"))
                    

        except OSError as e:
            self.info_label.setText(f"Error: {e}")

        self.populate_shot_list()
        
    def get_footage_list(self):
        footage_list_path = self.footage_path_edit.text()
        if not footage_list_path:
            self.info_label.setText("No footage path is selected")
            return
        
        footage_list = os.listdir(footage_list_path)
        if not footage_list:
            self.info_label.setText("Footage folder is empty")
            return
        return footage_list
    
    def copy_footage(self):
        project_base_folder = self.project_path_edit.text()
        project_folder = os.path.join(project_base_folder, self.project_name)
        footage_list_path = self.footage_path_edit.text()
        footage_list = self.get_footage_list()

        try:
            for footage in footage_list:
                footage_folder = os.path.join(project_folder, footage, "input_footage")
                source_shot_folder = os.path.join(footage_list_path, footage)
                shutil.copytree(source_shot_folder, os.path.join(footage_folder, footage))
            self.info_label.setText("Footage copied successfully.")
        except OSError as e:
            self.info_label.setText(f"Error: {e}")

    def shot_selected(self, shot_number):
        print("Selected Shot {}".format(shot_number))
        
    
    def open_script(self, script_path):
        try:
            # Path to the Nuke executable
            nuke_path = r"C:\Program Files\Nuke15.0v1\Nuke15.0.exe"

            # Command to open Nuke and execute the script
            command = [nuke_path, "-t", script_path]

            # Run the command in a subprocess
            subprocess.Popen(command, shell=True)
            
            # Inform the user
            message = f"Opening script in Nuke: {script_path}"
            QMessageBox.information(self, "Script Loaded", message)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Nuke executable not found. Please provide the correct path.")
        except Exception as e:
            # Handle any other exceptions that may occur
            QMessageBox.critical(self, "Error", f"Error opening script: {e}")


    def load_script(self):
        selected_item = self.shot_list_widget.currentItem().text()

        if not selected_item:
            message = "Please select a shot to continue.."
            QMessageBox.information(self, "Message", message)
            return

        project_base_folder = self.project_path_edit.text()
        project_folder = os.path.join(project_base_folder, self.project_name)
        input_footage_folder = os.path.join(project_folder, selected_item, "input_footage", selected_item)
        script_folder = os.path.join(project_folder, selected_item, "scripts")
        shot_name = selected_item
        renders_folder = os.path.join(project_folder, selected_item, "renders")

        existing_script_pattern = re.compile(rf"{re.escape(shot_name)}_v(\d+)\.nk", re.IGNORECASE)

        existing_scripts = [
            script for script in os.listdir(script_folder)
            if os.path.isfile(os.path.join(script_folder, script)) and existing_script_pattern.match(script)
        ]

        if existing_scripts:
            highest_version_script = max(existing_scripts, key=lambda script: int(existing_script_pattern.match(script).group(1)))

            existing_script_path = os.path.join(script_folder, highest_version_script)

            dialog = ExistingScriptDialog(existing_script_path, self)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                # Open the existing script in Nuke
                self.open_script(existing_script_path)
            else:
                # Create a new version and open it in Nuke
                new_version = int(existing_script_pattern.match(highest_version_script).group(1)) + 1
                new_script_name = f"{shot_name}_v{new_version:03d}.nk"
                new_script_path = os.path.join(script_folder, new_script_name)

                # Copy the template script to create a new version
                shutil.copy(existing_script_path, new_script_path)

                # Open the new script in Nuke
                self.open_script(new_script_path)
        else:
            # No existing scripts, create a new one
            template_path = r"C:\Users\pratap\Documents\python_final_project\templete\templete.nk"
            ti = r"C:\Users\pratap\github-classroom\Python-For-Visual-Effects\final-project-pratap-gunda\template_load.py"
            new_script_path = os.path.join(script_folder, f"{shot_name}_v001.nk")

            # Copy the template script to create a new script
            shutil.copy(template_path, new_script_path)

            # Open the new script in Nuke
            self.open_script(new_script_path)

        # Display an information message
        message = f"Opening {selected_item} shot in Nuke...."
        QMessageBox.information(self, "Script Loaded", message)

   

        template_path = r"C:\Users\pratap\Documents\python_final_project\templete\templete.nk"
        ti = r"C:\Users\pratap\github-classroom\Python-For-Visual-Effects\final-project-pratap-gunda\template_load.py"
        args = [
            r"C:\Program Files\Nuke15.0v1\Nuke15.0.exe",
            f"{ti}",
            template_path,
            input_footage_folder,
            script_folder,
            shot_name,
            renders_folder,
        ]

        processed = subprocess.Popen(args=args)
        
        #message = f"Opening {selected_item} shot in Nuke...."
        #QMessageBox.information(self, "Script Loaded", message)

    def populate_shot_list(self):
        footage_list = self.get_footage_list()
        for footage in footage_list:
            self.shot_list_widget.addItem(footage)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FolderCreationApp()
    window.show()
    sys.exit(app.exec_())
