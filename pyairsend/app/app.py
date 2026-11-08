from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
    QLabel,
    QListWidgetItem,
)

from pyairsend.app.styling import TOP, LEFT, BOTTOM, RIGHT
from pyairsend.app.pages import SendPage, TransfersPage, DevicesPage, SettingsPage


class MainWindow(QMainWindow):
    PAGES = ["Home", "Send", "Transfers", "Devices", "Settings"]

    def _set_sidebar(self):
        """ Set up the sidebar with the list of pages. """
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItems(self.PAGES)
        self.sidebar.setCurrentRow(0)  # Set the default selected page to "Home"

    def _set_stack(self):
        """ Set up the stacked layout for the content area. """
        self.pages = QStackedWidget()

        self.send_page = SendPage()
        self.transfers_page = TransfersPage()
        self.devices_page = DevicesPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(QLabel("<h1>Home</h1>", alignment=TOP | LEFT))
        self.pages.addWidget(self.send_page)
        self.pages.addWidget(self.transfers_page)
        self.pages.addWidget(self.devices_page)
        self.pages.addWidget(self.settings_page)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyAirSend")
        self.resize(800, 600)

        # main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # sidebar
        self._set_sidebar()

        # content area with stacked layout + connect sidebar selection to stacked layout
        self._set_stack()
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        # TODO: StatusBar for showing transfer progress, device status, etc.

        # add sidebar and stack to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)


def run_app():
    app = QApplication([])

    # Get the path to the assets directory
    # assets_dir = Path(__file__).parent / "assets"

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
