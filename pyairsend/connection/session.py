# PeerSession stuff, connect, disconnect, status, etc.
import asyncio
from enum import StrEnum

from pyairsend.transport.socket_io import receive_message, send_control
from pyairsend.protocol.messages import MessageType


class ConnectionStatus(StrEnum):
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


# TODO: FileReceiver and FileSender

class PeerSession:
    def __init__(self, peer_address: str, peer_port: int):
        self.peer_address = peer_address
        self.peer_port = peer_port

        self.reader = None  # asyncio.StreamReader
        self.writer = None  # asyncio.StreamWriter

        self.current_status = ConnectionStatus.DISCONNECTED

    @classmethod
    def from_streams(cls, reader, writer):
        """ Create a PeerSession from existing streams. """
        peername = writer.get_extra_info('peername')
        if peername is None:
            raise ValueError("Cannot determine peer address and port from streams.")

        peer_address, peer_port = peername[0], peername[1]
        session = cls(peer_address, peer_port)

        session.reader = reader
        session.writer = writer
        session.current_status = ConnectionStatus.CONNECTED
        return session

    @property
    def address(self):
        return (self.peer_address, self.peer_port)

    def assure_connected(self):
        """
        Assures that the session is connected
        before performing operations that require a connection.
        """
        if self.current_status in [ConnectionStatus.DISCONNECTED, ConnectionStatus.CONNECTING] or \
            self.reader is None or self.writer is None:
            raise PeerIsNotAvailable("PeerSession is not connected.")

    async def close(self):
        """ closes the session and cleans up resources """
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()

        self.reader = None
        self.writer = None
        self.current_status = ConnectionStatus.DISCONNECTED

    async def connect(self):
        """ Establishes a connection to the peer. """
        if self.current_status == ConnectionStatus.CONNECTED:
            return  # Already connected

        self.current_status = ConnectionStatus.CONNECTING

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.peer_address, self.peer_port),
                timeout=10
            )

            self.current_status = ConnectionStatus.CONNECTED

        except Exception:
            await self.close()  # Ensure resources are cleaned up
            raise

    async def send_handshake(self):
        """ Send a handshake message to the peer and await response. """
        self.assure_connected()

        # Send a HELLO message to the peer, await response
        self.current_status = ConnectionStatus.NEGOTIATING
        await send_control(self.writer, MessageType.HELLO, "")

        message = await receive_message(self.reader)

        if message.message_type == MessageType.HELLO_ACCEPT:
            self.current_status = ConnectionStatus.READY

        elif message.message_type == MessageType.HELLO_REJECT:
            self.current_status = ConnectionStatus.CONNECTED
            raise RejectedHandshake("Handshake rejected by peer.")

        else:
            self.current_status = ConnectionStatus.CONNECTED
            raise InvalidMessageType("Unexpected message type received during handshake.")

    async def answer_handshake(self, *, accept):
        """ answers to handshake request from peer, either accept or reject """
        self.assure_connected()

        self.current_status = ConnectionStatus.NEGOTIATING

        try:
            if accept:
                await self.accept_handshake()
            else:
                await self.reject_handshake()

        except Exception:
            self.current_status = ConnectionStatus.CONNECTED
            raise

        return self.current_status == ConnectionStatus.READY

    async def accept_handshake(self):
        await send_control(self.writer, MessageType.HELLO_ACCEPT, "")
        self.current_status = ConnectionStatus.READY

    async def reject_handshake(self):
        await send_control(self.writer, MessageType.HELLO_REJECT, "")
        self.current_status = ConnectionStatus.CONNECTED

    async def receive_handshake(self):
        """ wait for and validate a HELLO sent by the connected peer """
        self.assure_connected()

        # Wait for a HELLO message from the peer
        message = await receive_message(self.reader)

        if message.message_type != MessageType.HELLO:
            raise InvalidMessageType("Expected HELLO message from peer.")

        self.current_status = ConnectionStatus.NEGOTIATING
