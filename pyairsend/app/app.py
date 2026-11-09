import asyncio
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot, QObject
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
from qasync import QEventLoop, asyncSlot

from pyairsend.app.styling import TOP, LEFT, BOTTOM, RIGHT
from pyairsend.app.pages import SendPage, TransfersPage, DevicesPage, SettingsPage
from pyairsend.connection.server import PeerServer, PeerSession


class StatusOptions:
    """ Class to hold status messages for the application. """
    STARTING_SERVER = "Starting Server"
    SERVER_RUNNING = "Server Running, listening for connections"
    NEGOTIATING = "Negotiating with peer"
    READY = "Ready for Transfer"
    ERROR = "Error"


class StatusSignal(QObject):
    update_status = Signal(str)


class MainWindow(QMainWindow):
    PAGES = ["Home", "Send", "Transfers", "Devices", "Settings"]

    def closeEvent(self, event):
        """ Redefine closing event for async cleanup. """
        loop = asyncio.get_event_loop()
        loop.stop()
        event.accept()

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

    def _set_status_bar(self):
        """ Set up the status bar for showing transfer progress, device status, etc. """
        self.status_bar = self.statusBar()
        self.status = QLabel(StatusOptions.STARTING_SERVER)

        self.status_bar.addWidget(self.status)

        # Connect the status signal to the update method
        self.status_signal = StatusSignal()
        self.status_signal.update_status.connect(self._update_status_bar)

    def _set_main_layout(self):
        """ Set up the main layout with sidebar and stacked content. """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # add sidebar and stack to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
        # main_layout.addWidget(self.status_bar)  # FIXME: this should not be added here

    @Slot(str)
    def _update_status_bar(self, message: str):
        """ Update the status bar with a new message. """
        self.status.setText(message)

    async def _init_server(self):
        """ Initialize the server for receiving connections. """
        self.server = PeerServer()

        try:
            await self.server.start()
        except OSError as error:
            self.status_signal.update_status.emit(f"Error starting server: {error}")
            return

        asyncio.create_task(self._monitor_server_status())

    async def _monitor_server_status(self):
        """ Monitor the server status and update the status bar accordingly. """

        while True:
            if self.server.status == PeerServer.ServerStatus.RUNNING:
                self.status_signal.update_status.emit(StatusOptions.SERVER_RUNNING)

            elif self.server.status == PeerServer.ServerStatus.FAILED:
                self.status_signal.update_status.emit(StatusOptions.ERROR)

            await asyncio.sleep(5)  # Check every second

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyAirSend")
        self.resize(800, 600)

        # sidebar and stacked content
        self._set_sidebar()
        self._set_stack()
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        # status bar
        self._set_status_bar()

        # create main layout
        self._set_main_layout()


def run_app():
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    loop.create_task(window._init_server())  # Start the server in the background

    # Get the path to the assets directory
    # assets_dir = Path(__file__).parent / "assets"
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    run_app()
