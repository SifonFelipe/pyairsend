import asyncio

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from qasync import asyncSlot

from pyairsend.app.styling import TOP, LEFT
from pyairsend.connection.session import PeerSession, PeerSessionError


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
        self.add_device_button.clicked.connect(self.add_device)

        self.add_device_status = QLabel()

        layout.addWidget(self.device_ip)
        layout.addWidget(self.device_port)
        layout.addWidget(self.add_device_button)
        layout.addWidget(self.add_device_status)

    def __init__(self):
        super().__init__()

        self.sessions: dict[tuple[str, int], PeerSession] = {}

        self._set_add_devices_section()

        # TODO: list devices stored in the app, and discovered devices
        self._set_layout()

    def _parse_device_address(self) -> tuple[str, int]:
        """ Read and validate the IP and port fields. """
        ip = self.device_ip.text().strip()
        port = self.device_port.text().strip()

        if not ip or not port:
            raise ValueError("IP address and port must be provided.")

        if not port.isdigit() or not 0 < int(port) < 65536:
            raise ValueError("Port must be a number between 1 and 65535.")

        return ip, int(port)

    @asyncSlot()
    async def add_device(self):
        try:
            ip, port = self._parse_device_address()
        except ValueError as error:
            self.add_device_status.setText(str(error))
            return

        self.add_device_status.setText(f"Connecting to {ip}:{port}...")
        self.add_device_button.setEnabled(False)  # avoid double clicks while connecting

        device_session = PeerSession(ip, port)

        try:
            await device_session.connect()  # Attempt to connect to the device
            await asyncio.wait_for(device_session.send_handshake(), timeout=5.0)

        except (OSError, TimeoutError, asyncio.IncompleteReadError, PeerSessionError) as error:
            await device_session.close()
            self.add_device_status.setText(f"Could not add {ip}:{port}: {error or type(error).__name__}")
            return

        finally:
            self.add_device_button.setEnabled(True)

        # replace any previous session to the same device
        previous = self.sessions.pop(device_session.address, None)
        if previous is not None:
            await previous.close()

        self.sessions[device_session.address] = device_session
        self.add_device_status.setText(f"Connected to {ip}:{port}")

    async def close_sessions(self):
        """ Close every open session, used when the app quits. """
        sessions = list(self.sessions.values())
        self.sessions.clear()

        for session in sessions:
            try:
                await session.close()
            except OSError:
                pass  # peer already gone
