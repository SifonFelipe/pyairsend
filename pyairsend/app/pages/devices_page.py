from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from qasync import asyncSlot

from pyairsend.app.styling import TOP, LEFT
from pyairsend.connection.session import PeerSession


class DevicesPage(QWidget):
    """
    Devices page for the PyAirSend application.
    Discovery + saved devices.
    """
    def _set_layout(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<h1>Devices</h1>", alignment=TOP | LEFT))
        layout.addWidget(self.add_devices_section)

        self.setLayout(layout)

    def _set_add_devices_section(self):
        self.add_devices_section = QWidget()
        layout = QVBoxLayout(self.add_devices_section)

        layout.addWidget(QLabel("<h2>Add Device</h2>", alignment=TOP | LEFT))
        self.device_ip = QLineEdit(placeholderText="Enter device IP address")
        self.device_port = QLineEdit(placeholderText="Enter device port")

        self.add_device_button = QPushButton("Add Device")
        self.add_device_button.clicked.connect(self.test)

        layout.addWidget(self.device_ip)
        layout.addWidget(self.device_port)
        layout.addWidget(self.add_device_button)

    def __init__(self):
        super().__init__()

        self._set_add_devices_section()

        # TODO: list devices stored in the app, and discovered devices
        self._set_layout()

    @asyncSlot()
    async def test(self):
        ip = self.device_ip.text()
        port = self.device_port.text()

        if not ip or not port:
            raise ValueError("IP address and port must be provided.")

        device_info = f"{ip}:{port}"
        print("Attempting to add device:", device_info)

        device_session = PeerSession(ip, int(port))

        await device_session.connect()  # Attempt to connect to the device
        await device_session.send_handshake() # Send handshake to the device
