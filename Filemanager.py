import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileSystemModel,QTreeView, QLabel, QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QLineEdit, QInputDialog,QHBoxLayout
from PyQt5.QtCore import Qt,QDir
from PyQt5.QtGui import QIcon  # Import QIcon
import os
import shutil
import subprocess

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Operating System File Manager")
        self.setGeometry(50, 50, 1100, 700)
        self.setWindowIcon(self.style().standardIcon(QApplication.style().SP_DirHomeIcon))

        self.current_path = os.path.expanduser("://") # Starting from the root directory

        self.central_widget = QTreeWidget()  # Change here to QTreeWidget
        self.setCentralWidget(self.central_widget)
        self.central_widget.setHeaderLabels([""])
        self.central_widget.setColumnWidth(0, 300)
        self.setup_ui()


    def setup_ui(self):
        self.layout = QVBoxLayout()
        
        
        
        self.path_label = QLabel()
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("QLabel { font-size: 15px; }")
        self.layout.addWidget(self.path_label)

        self.tree_view = QTreeView()
        self.model = QFileSystemModel()
        self.create_buttons()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.search_bar)
        
        # self.create_back_button()
        self.model.setRootPath(self.current_path)
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        self.tree_view.setColumnWidth(0, 380)
        self.tree_view.doubleClicked.connect(self.on_double_click)
        self.layout.addWidget(self.tree_view)

        # self.create_buttons()
        self.central_widget.setLayout(self.layout)
        # self.create_buttons()
        # self.central_widget.setLayout(self.layout)

    
    def create_buttons(self):
        self.buttons_layout = QHBoxLayout()

        self.home_button  =  QPushButton("This Pc")
        self.home_button.setIcon(self.style().standardIcon(QApplication.style().SP_ComputerIcon))
        self.home_button.clicked.connect(self.go_home)
        
        self.back_button = QPushButton("Back")
        self.back_button.setIcon(QIcon('back.png')) 
        self.back_button.clicked.connect(self.go_back)

        
        self.rename_button = QPushButton("Rename")
        self.rename_button.setIcon(QIcon('edit.png')) 
        self.rename_button.clicked.connect(self.rename_file)


        self.delete_button = QPushButton("Delete")
        self.delete_button.setIcon(QIcon('delete.png')) 
        self.delete_button.clicked.connect(self.delete_file)


        self.copy_button = QPushButton("Copy")
        self.copy_button.setIcon(QIcon('copy.png')) 
        self.copy_button.clicked.connect(self.copy_file)


        self.move_button = QPushButton("Move")
        self.move_button.setIcon(QIcon('cut.png')) 
        self.move_button.clicked.connect(self.move_file)

        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(self.style().standardIcon(QApplication.style().SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refresh_view)


        self.new_folder_button = QPushButton("New Folder")
        self.new_folder_button.setIcon(self.style().standardIcon(QApplication.style().SP_DirIcon))
        self.new_folder_button.clicked.connect(self.create_new_folder)
        
        self.create_file_button = QPushButton("Create File")
        self.create_file_button.setIcon(self.style().standardIcon(QApplication.style().SP_FileIcon))
        self.create_file_button.clicked.connect(self.create_file)

        
        self.buttons_layout.addWidget(self.back_button)
        self.buttons_layout.addWidget(self.home_button)
        self.buttons_layout.addWidget(self.new_folder_button)   
        self.buttons_layout.addWidget(self.create_file_button)       
        self.buttons_layout.addWidget(self.rename_button)
        self.buttons_layout.addWidget(self.copy_button)
        self.buttons_layout.addWidget(self.move_button)
        self.buttons_layout.addWidget(self.delete_button)  
        self.buttons_layout.addWidget(self.refresh_button)
            

        
        self.layout.addLayout(self.buttons_layout)
        
    def filter_items(self, text):
    # Filter items in the QTreeView based on the search text
        root_index = self.model.index(self.current_path)
        self.tree_view.setRootIndex(root_index)

        if text:
            # Create a filter to match the search text
            filter_text = text.lower()  # Convert both text and file name to lowercase for case-insensitive comparison
            self.model.setNameFilters(["*" + filter_text + "*"])
            self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)

            # Show only the matching items in the tree view
            for row in range(self.model.rowCount(root_index)):
                index = self.model.index(row, 0, root_index)
                item_path = self.model.filePath(index)
                if filter_text not in self.model.fileName(index).lower():
                    self.tree_view.setRowHidden(row, index.parent(), True)
                else:
                    self.tree_view.setRowHidden(row, index.parent(), False)
        else:
            # If the search text is empty, clear the filters and show all items
            self.model.setNameFilters([])
            self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)

            # Show all items in the tree view
            for row in range(self.model.rowCount(root_index)):
                self.tree_view.setRowHidden(row, root_index, False)


        
    def create_new_folder(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            current_path = self.model.filePath(index)
            new_name, ok = QInputDialog.getText(self, "Create Folder", "Enter folder name:", QLineEdit.Normal)
            if ok and new_name.strip():
                new_folder_path = os.path.join(current_path, new_name)
                try:
                    os.makedirs(new_folder_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                else:
                    self.model.setRootPath(self.current_path)
                    self.soft_refresh_view()
                
    def create_file(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            current_path = self.model.filePath(index)
            new_name, ok = QInputDialog.getText(self, "Create File", "Enter file name:", QLineEdit.Normal)
            if ok and new_name.strip():
                new_file_path = os.path.join(current_path, new_name)
                try:
                    with open(new_file_path, 'w'):
                        pass  # Create an empty file
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                else:
                    self.model.setRootPath(self.current_path)
                    self.soft_refresh_view()
    
    def soft_refresh_view(self):
        self.model.setRootPath(self.current_path)
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        # self.path_label.setText(self.current_path)
        # self.tree_view.collapseAll()
        self.search_bar.clear()
        
    def refresh_view(self):
        self.model.setRootPath(self.current_path)
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        self.path_label.setText(self.current_path)
        self.tree_view.collapseAll()
        self.search_bar.clear()
        

    def go_back(self):
        self.current_path = self.model.filePath(self.model.parent(self.model.index(self.current_path)))
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        self.path_label.setText(self.current_path)

    def go_home(self):
        home_index = self.model.index(os.path.expanduser("://"))
        self.current_path = self.model.filePath(home_index)
        self.tree_view.setRootIndex(home_index)
        self.path_label.setText(self.current_path)

    def on_double_click(self, index):
        file_path = self.model.filePath(index)
        if self.model.isDir(index):
            self.current_path = file_path
            self.tree_view.setRootIndex(index)
            self.path_label.setText(self.current_path)
        else:
            self.open_file_with_default_app(file_path)


   
    def show_drives_and_folders(self):
        self.central_widget.clear()

        drive_items = []
        drives = [os.path.abspath(os.path.join('%s:' % d)) for d in 'ABDCEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists('%s:' % d)]
        for drive in drives:
            drive_item = QTreeWidgetItem(self.central_widget, [drive, "Drive", ""])
            drive_items.append(drive_item)
            self.list_files_in_directory(drive, drive_item)

        self.central_widget.insertTopLevelItems(0, drive_items)


    def list_files_in_directory(self, path, parent):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    file_item = QTreeWidgetItem(parent, [item, "File", f"{size} bytes"])
                elif os.path.isdir(item_path):
                    dir_item = QTreeWidgetItem(parent, [item, "Folder", ""])
                    self.list_files_in_directory(item_path, dir_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def open_file_with_default_app(self, file_path):
        try:
            if sys.platform.startswith('darwin'):  # For macOS
                subprocess.run(['open', file_path])
            elif os.name == 'nt':  # For Windows
                os.startfile(file_path)
            else:  # For Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def rename_file(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            old_path = self.model.filePath(index)
            new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", QLineEdit.Normal, self.model.fileName(index))
            if ok and new_name.strip():
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                else:
                    self.model.setRootPath(self.current_path)


    def delete_file(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            path = self.model.filePath(index)

            # Ask for confirmation before deleting
            confirm_msg = f"Are you sure you want to delete {os.path.basename(path)}?"
            confirm_reply = QMessageBox.question(self, "Confirm Deletion", confirm_msg, QMessageBox.Yes | QMessageBox.No)

            if confirm_reply == QMessageBox.Yes:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    self.model.setRootPath(self.current_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete: {e}")


    def copy_file(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            source = self.model.filePath(index)
            destination = QFileDialog.getExistingDirectory(self, "Select destination folder")
            if destination:
                try:
                    if os.path.isdir(source):
                        shutil.copytree(source, os.path.join(destination, self.model.fileName(index)))
                    else:
                        shutil.copy2(source, destination)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                else:
                    self.model.setRootPath(self.current_path)


    def move_file(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            source = self.model.filePath(index)
            destination = QFileDialog.getExistingDirectory(self, "Select destination folder")
            if destination:
                try:
                    shutil.move(source, os.path.join(destination, self.model.fileName(index)))
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                else:
                    self.model.setRootPath(self.current_path)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    file_explorer = FileExplorer()
    file_explorer.show()
    sys.exit(app.exec_())
