from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel
)

from pyairsend.app.styling import TOP, LEFT


class SendPage(QWidget):
    """ Send files page for the PyAirSend application. """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h1>Send Files</h1>", alignment=TOP | LEFT))

        self.peer_ip = QLineEdit(placeholderText="Enter peer IP address")
        # TODO: validator for IP address

        self.peer_port = QLineEdit(placeholderText="Enter peer port")

        self.send_button = QPushButton("Send Files")
        self.send_button.clicked.connect(self.send_files)

        # add widgets to layout
        layout.addWidget(self.peer_ip)
        layout.addWidget(self.peer_port)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    @Slot()
    def send_files(self):
        """ Send files to the specified peer. """
        ip = self.peer_ip.text()
        port = self.peer_port.text()

        # implement logic here.

