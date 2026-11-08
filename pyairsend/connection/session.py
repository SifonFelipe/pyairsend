# PeerSession stuff, connect, disconnect, status, etc.
import socket
from dataclasses import dataclass

from pyairsend.transport.socket_io import receive_message, send_control
from pyairsend.protocol.messages import MessageType


@dataclass
class ConnectionStatus:
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    NEGOTIATING = "negotiating"
    READY = "ready"


class PeerSessionError(Exception):
    """ Base class for exceptions in PeerSession. """
    pass


class RejectedHandshake(PeerSessionError):
    """ Exception raised when a handshake is rejected by the peer. """
    pass


class PeerIsNotAvailable(PeerSessionError):
    """ Exception raised when the peer is not available for connection. """
    pass


class InvalidMessageType(PeerSessionError):
    """ Exception raised when an unexpected message type is received. """
    pass


# TODO: pass to async
# TODO: FileReceiver and FileSender

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
            raise PeerIsNotAvailable("PeerSession is not connected.")

    def connect(self):
        if self.current_status == ConnectionStatus.CONNECTED:
            return  # Already connected

        self.current_status = ConnectionStatus.CONNECTING

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.sock.settimeout(10)  # (s) Set a timeout for the connection attempt
            self.sock.connect(self.address)
            self.sock.settimeout(None)

            self.current_status = ConnectionStatus.CONNECTED

        except Exception as e:
            self.current_status = ConnectionStatus.DISCONNECTED

            if self.sock is not None:
                self.sock.close()

            raise e

    def handshake(self):
        self.assure_connected()

        # Send a HELLO message to the peer, await response
        self.current_status = ConnectionStatus.NEGOTIATING
        send_control(self.sock, MessageType.HELLO, "")

        message = receive_message(self.sock)

        if message.message_type == MessageType.HELLO_ACCEPT:
            self.current_status = ConnectionStatus.READY

        elif message.message_type == MessageType.HELLO_REJECT:
            self.current_status = ConnectionStatus.CONNECTED
            raise RejectedHandshake("Handshake rejected by peer.")

        else:
            self.current_status = ConnectionStatus.CONNECTED
            raise InvalidMessageType("Unexpected message type received during handshake.")

    def answer_handshake(self, *, accept):
        self.assure_connected()

        self.current_status = ConnectionStatus.NEGOTIATING

        try:
            if accept:
                self.accept_handshake()
            else:
                self.reject_handshake()

        except Exception as e:
            self.current_status = ConnectionStatus.CONNECTED
            raise e

        return self.current_status == ConnectionStatus.READY

    def accept_handshake(self):
        self.assure_connected()

        send_control(self.sock, MessageType.HELLO_ACCEPT, "")
        self.current_status = ConnectionStatus.READY

    def reject_handshake(self):
        self.assure_connected()

        send_control(self.sock, MessageType.HELLO_REJECT, "")
        self.current_status = ConnectionStatus.CONNECTED
