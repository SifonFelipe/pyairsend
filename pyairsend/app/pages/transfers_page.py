from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from pyairsend.app.styling import TOP, LEFT


class TransfersPage(QWidget):
    """ Transfers page for the PyAirSend application. """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h1>Transfers</h1>", alignment=TOP | LEFT))

        self.setLayout(layout)
