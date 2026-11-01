# PeerSession stuff, connect, disconnect, status, etc.
import socket
from dataclasses import dataclass


@dataclass
class ConnectionStatus:
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"


class PeerSession:
    def __init__(self, peer_address: str, peer_port: int):
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.sock = None
        self.current_status = ConnectionStatus.DISCONNECTED

    @property
    def address(self):
        return (self.peer_address, self.peer_port)

    def assure_connected(self):
        if self.current_status != ConnectionStatus.CONNECTED:
            raise Exception("PeerSession is not connected.")

    def connect(self):
        if self.current_status == ConnectionStatus.CONNECTED:
            return  # Already connected

        self.current_status = ConnectionStatus.CONNECTING

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.address)
            self.current_status = ConnectionStatus.CONNECTED

        except Exception as e:
            self.current_status = ConnectionStatus.DISCONNECTED
            raise e

    def handshake(self):
        self.assure_connected()

        # Implement handshake logic here



