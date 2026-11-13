
import os, sys, webbrowser
from pathlib import Path

from database import Database
from modules.userdata import Userdata

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QVBoxLayout, QHBoxLayout,

    QPushButton, QLabel,
    QListWidget, QListWidgetItem,

    QListView, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QPixmap, QIcon, QImageReader, QAction, QKeySequence

from modules.picture import Picture
from modules.tags import Tags, Tag

class GUI(QMainWindow):
    def __init__(self, userdata: Userdata, database: Database):
        super().__init__()
        self.pictures = []

    def initialize(self) -> None:
        self.setWindowTitle("flarepick")
        self.resize(700, 450)

        self.create_menu()
        self.create_ui()

    def create_menu(self) -> None:
        menu = self.menuBar()
        menu.setNativeMenuBar(True)

        file_menu = menu.addMenu("File")
        menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")

        open_action = QAction("Open Folder", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_folder)

        exit_action = QAction("Quit flarepick", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setMenuRole(QAction.MenuRole.QuitRole)
        exit_action.triggered.connect(QApplication.instance().quit)

        file_menu.addAction(open_action)
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
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

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

    def load_pictures(self, folder: Path) -> None:
        self.thumbnails.clear()
        self.current_pixmap = None
        self.preview.setPixmap(QPixmap())
        self.preview.setText("Select a photo")

        files = [
            path
            for path in Path(folder).iterdir()
            if path.is_file()
        ]
        self.pictures = []

        for file in files:
            reader = QImageReader(str(file))
            if reader.canRead():
                picture = Picture(file)
                self.pictures.append(picture)
                reader.setAutoTransform(True)

                size = reader.size()

                if size.isValid():
                    size.scale(
                        QSize(110, 80),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                    reader.setScaledSize(size)

                image = reader.read()

                item = QListWidgetItem(picture.name)
                item.setData(Qt.ItemDataRole.UserRole, str(picture.path))
                item.setToolTip(str(picture.path))

                if not image.isNull():
                    item.setIcon(QIcon(QPixmap.fromImage(image)))

                self.thumbnails.addItem(item)

        if self.thumbnails.count():
            self.thumbnails.setCurrentRow(0)


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

    def open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )

        if folder:
            self.load_pictures(Path(folder))


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
