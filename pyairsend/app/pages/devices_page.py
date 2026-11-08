from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from pyairsend.app.styling import TOP, LEFT


class DevicesPage(QWidget):
    """
    Devices page for the PyAirSend application.
    Discovery + saved devices.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h1>Devices</h1>", alignment=TOP | LEFT))

        self.setLayout(layout)
