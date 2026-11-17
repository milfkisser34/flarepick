
import sqlite3
import sys
import webbrowser
from pathlib import Path

from database import Database
from modules.userdata import Userdata

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QVBoxLayout, QHBoxLayout,

    QPushButton, QLabel,
    QListWidget, QListWidgetItem,

    QListView, QSizePolicy, QInputDialog, QMessageBox, QLineEdit,
    QAbstractItemView, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QPixmap, QIcon, QImageReader, QAction, QKeySequence

class GUI(QMainWindow):
    def __init__(self, userdata: Userdata, database: Database):
        super().__init__()
        self.pictures = []
        self.database = database
        self.active_collection_id = None
        self.folder = None
        self.folder_paths = []

    def initialize(self) -> None:
        self.setWindowTitle("flarepick")
        self.resize(700, 450)

        self.create_menu()
        self.create_ui()
        self.load_collections()
        self.show_folder()

    def create_menu(self) -> None:
        menu = self.menuBar()
        menu.setNativeMenuBar(True)

        file_menu = menu.addMenu("File")
        menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")

        open_action = QAction("Open Folder", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_folder)
        self.add_collection_action = QAction("Add to Collection", self)
        self.add_collection_action.triggered.connect(self.add_to_collection)

        exit_action = QAction("Quit flarepick", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setMenuRole(QAction.MenuRole.QuitRole)
        exit_action.triggered.connect(QApplication.instance().quit)

        file_menu.addAction(open_action)
        file_menu.addAction(self.add_collection_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        open_github = QAction("GitHub", self)
        open_github.setShortcut("F1")
        open_github.triggered.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/milfkisser34/flarepick"
            )
        )

        help_menu.addAction(open_github)

    def create_ui(self) -> None:
        central = QWidget()
        outer = QHBoxLayout(central)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(QLabel("Collections"))
        self.collections = QListWidget()
        self.collections.currentItemChanged.connect(self.select_collection)
        sidebar_layout.addWidget(self.collections, 1)

        controls = QHBoxLayout()
        create_button = QPushButton("+")
        create_button.setToolTip("Create Collection")
        create_button.clicked.connect(self.create_collection)
        self.rename_button = QPushButton("✎")
        self.rename_button.setToolTip("Rename Collection")
        self.rename_button.clicked.connect(self.rename_collection)
        self.delete_button = QPushButton("−")
        self.delete_button.setToolTip("Delete Collection")
        self.delete_button.clicked.connect(self.delete_collection)
        for button in (create_button, self.rename_button, self.delete_button):
            button.setFixedWidth(32)
            controls.addWidget(button)
        controls.addStretch()
        sidebar_layout.addLayout(controls)
        outer.addWidget(sidebar)

        content = QWidget()
        layout = QVBoxLayout(content)
        outer.addWidget(content, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)
        self.folder_button = QPushButton("Folder")
        self.folder_button.clicked.connect(self.show_folder)
        toolbar.addWidget(self.folder_button)
        self.add_collection_button = QPushButton("Add to Collection")
        self.add_collection_button.clicked.connect(self.add_to_collection)
        toolbar.addWidget(self.add_collection_button)
        toolbar.addStretch()

        self.preview = QLabel("Select a photo")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(200)
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview.setStyleSheet("""
            QLabel {
                background-color: #1c1c1e;
                color: #8e8e93;
                border-radius: 10px;
            }
        """)

        self.preview.installEventFilter(self)

        layout.addWidget(self.preview, 1)

        self.thumbnails = QListWidget()
        self.thumbnails.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.thumbnails.itemSelectionChanged.connect(self.update_selection)
        self.thumbnails.setViewMode(QListView.ViewMode.IconMode)
        self.thumbnails.setFlow(QListView.Flow.LeftToRight)
        self.thumbnails.setWrapping(False)
        self.thumbnails.setMovement(QListView.Movement.Static)
        self.thumbnails.setResizeMode(QListView.ResizeMode.Adjust)
        self.thumbnails.setIconSize(QSize(110, 80))
        self.thumbnails.setGridSize(QSize(125, 110))
        self.thumbnails.setFixedHeight(135)
        self.thumbnails.setSpacing(4)
        self.thumbnails.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.thumbnails.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.thumbnails.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }

            QListWidget::item {
                border-radius: 6px;
                padding: 4px;
            }

            QListWidget::item:selected {
                background: palette(highlight);
            }
        """)

        self.thumbnails.currentItemChanged.connect(
            self.select_picture
        )

        layout.addWidget(self.thumbnails)

        self.current_pixmap = None

        self.setCentralWidget(central)

    def clear_pictures(self, message: str) -> None:
        self.thumbnails.clear()
        self.pictures = []
        self.current_pixmap = None
        self.preview.clear()
        self.preview.setText(message)

    def load_collections(self, selected_id=None) -> None:
        if selected_id is None:
            selected_id = self.active_collection_id
        try:
            collections = self.database.get_collections()
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database error", str(error))
            return
        self.collections.blockSignals(True)
        self.collections.clear()
        for collection in collections:
            item = QListWidgetItem(collection["name"])
            item.setData(Qt.ItemDataRole.UserRole, collection["id"])
            self.collections.addItem(item)
            if collection["id"] == selected_id:
                self.collections.setCurrentItem(item)
        self.collections.blockSignals(False)
        enabled = self.collections.currentItem() is not None
        self.rename_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def select_collection(self, current, previous=None) -> None:
        self.active_collection_id = (
            current.data(Qt.ItemDataRole.UserRole) if current else None
        )
        enabled = current is not None
        self.rename_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        if enabled:
            self.load_pictures()

    def update_selection(self) -> None:
        enabled = bool(self.thumbnails.selectedItems())
        self.add_collection_button.setEnabled(enabled)
        self.add_collection_action.setEnabled(enabled)

    def open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if not folder:
            return
        try:
            paths = sorted(
                (str(path.resolve()) for path in Path(folder).iterdir()
                 if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}),
                key=str.casefold
            )
        except OSError as error:
            QMessageBox.warning(self, "Cannot open folder", str(error))
            return
        self.folder = Path(folder)
        self.folder_paths = paths
        self.show_folder()

    def show_folder(self) -> None:
        self.active_collection_id = None
        self.collections.blockSignals(True)
        self.collections.clearSelection()
        self.collections.setCurrentRow(-1)
        self.collections.blockSignals(False)
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.folder_button.setEnabled(self.folder is not None)
        self.load_pictures()

    def collection_name(self, title: str, name: str = ""):
        name, accepted = QInputDialog.getText(
            self, title, "Collection name:", QLineEdit.EchoMode.Normal, name
        )
        if not accepted:
            return None
        name = name.strip()
        if not name or len(name) > 80 or "\n" in name or "\r" in name:
            QMessageBox.warning(
                self, "Invalid name", "Enter a name of 1–80 characters on one line."
            )
            return None
        return name

    def create_collection(self) -> None:
        name = self.collection_name("Create Collection")
        if name is None:
            return
        try:
            collection_id = self.database.create_collection(name)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Invalid name", "A collection with this name already exists.")
            return
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.critical(self, "Cannot create collection", str(error))
            return
        self.load_collections()
        return collection_id

    def rename_collection(self) -> None:
        current = self.collections.currentItem()
        if current is None:
            return
        name = self.collection_name("Rename Collection", current.text())
        if name is None:
            return
        try:
            self.database.rename_collection(self.active_collection_id, name)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Invalid name", "A collection with this name already exists.")
            return
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.critical(self, "Cannot rename collection", str(error))
            return
        current.setText(name)

    def delete_collection(self) -> None:
        current = self.collections.currentItem()
        if current is None:
            return
        answer = QMessageBox.question(
            self, "Delete Collection",
            f'Delete "{current.text()}"? Original image files will be kept.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.database.delete_collection(self.active_collection_id)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Cannot delete collection", str(error))
            return
        self.show_folder()
        self.load_collections()

    def add_to_collection(self) -> None:
        paths = [item.data(Qt.ItemDataRole.UserRole)
                 for item in self.thumbnails.selectedItems()]
        if not paths:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Add to Collection")
        layout = QVBoxLayout(dialog)
        destinations = QListWidget()
        layout.addWidget(destinations)
        create_button = QPushButton("Create Collection")
        layout.addWidget(create_button)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)

        def refresh(selected_id=None):
            try:
                collections = self.database.get_collections()
            except sqlite3.Error as error:
                QMessageBox.critical(dialog, "Database error", str(error))
                return
            destinations.clear()
            for collection in collections:
                item = QListWidgetItem(collection["name"])
                item.setData(Qt.ItemDataRole.UserRole, collection["id"])
                destinations.addItem(item)
                if collection["id"] == selected_id:
                    destinations.setCurrentItem(item)
            if destinations.currentItem() is None and destinations.count():
                destinations.setCurrentRow(0)

        def create_destination():
            collection_id = self.create_collection()
            if collection_id is not None:
                refresh(collection_id)

        destinations.currentItemChanged.connect(
            lambda current, previous: ok_button.setEnabled(current is not None)
        )
        create_button.clicked.connect(create_destination)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        refresh()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        current = destinations.currentItem()
        if current is None:
            return
        destination_id = current.data(Qt.ItemDataRole.UserRole)
        failed = []
        try:
            for path in paths:
                reader = QImageReader(path)
                if reader.read().isNull():
                    failed.append(path)
                    continue
                self.database.add_photo(destination_id, path)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            QMessageBox.critical(self, "Cannot add photos", str(error))
        if failed:
            QMessageBox.warning(
                self, "Cannot open images",
                "These images were not added:\n" + "\n".join(failed)
            )

    def load_pictures(self) -> None:
        in_collection = self.active_collection_id is not None
        self.clear_pictures(
            "This collection has no photos" if in_collection else
            "No supported photos in this folder" if self.folder else
            "Open a folder to get started"
        )
        self.update_selection()
        if in_collection:
            try:
                paths = [photo["path"] for photo in
                         self.database.get_photos(self.active_collection_id)]
            except sqlite3.Error as error:
                self.preview.setText("Cannot load photos")
                QMessageBox.critical(self, "Database error", str(error))
                return
        else:
            paths = self.folder_paths

        first_valid = None
        failed = []
        for path in paths:
            self.pictures.append(Path(path))
            reader = QImageReader(path)
            reader.setAutoTransform(True)
            size = reader.size()
            if size.isValid():
                size.scale(QSize(110, 80), Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(size)
            image = reader.read()
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            if not image.isNull():
                item.setIcon(QIcon(QPixmap.fromImage(image)))
                if first_valid is None:
                    first_valid = self.thumbnails.count()
            else:
                failed.append(path)
                item.setText(f"{Path(path).name} (unavailable)")
            self.thumbnails.addItem(item)

        if first_valid is not None:
            self.thumbnails.setCurrentRow(first_valid)
        elif paths:
            self.preview.setText("No readable images")
        if failed:
            QMessageBox.warning(
                self, "Unavailable images",
                "These images could not be opened:\n" + "\n".join(failed)
            )

    def select_picture(self, current, previous=None) -> None:
        if current is None:
            return

        path = current.data(Qt.ItemDataRole.UserRole)

        reader = QImageReader(path)
        reader.setAutoTransform(True)

        image = reader.read()

        if image.isNull():
            self.current_pixmap = None
            self.preview.setPixmap(QPixmap())
            self.preview.setText("Cannot open image")
            QMessageBox.warning(
                self, "Cannot open image",
                f"The image may have been moved, deleted, or damaged:\n{path}\n{reader.errorString()}"
            )
            return

        self.current_pixmap = QPixmap.fromImage(image)
        self.update_preview()


    def update_preview(self) -> None:
        if self.current_pixmap is None:
            return

        size = self.preview.contentsRect().size()

        if size.width() <= 0 or size.height() <= 0:
            return

        self.preview.setPixmap(
            self.current_pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )


    def eventFilter(self, obj, event):
        if obj is self.preview and event.type() == QEvent.Type.Resize:
            self.update_preview()

        return super().eventFilter(obj, event)



class Application:
    def __init__(
        self, userdata: Userdata, database: Database, argv=sys.argv
    ):
        self.app = QApplication(argv)
        self.app.setApplicationName("flarepick")
        self.app.setOrganizationName("vinogradow")

        self.database = database
        self.userdata = userdata

        self.gui = GUI(self.userdata, self.database)
        self.gui.initialize()

    def show(self):
        self.gui.show()
        sys.exit(self.app.exec())
