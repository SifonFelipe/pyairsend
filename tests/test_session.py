import asyncio
import unittest

from pyairsend.connection.session import (
    ConnectionStatus,
    InvalidMessageType,
    PeerSession,
    RejectedHandshake,
)
from pyairsend.protocol.messages import MessageType
from pyairsend.transport.socket_io import receive_message, send_control


class PeerSessionTests(unittest.IsolatedAsyncioTestCase):
    async def _handshake_peer(self, response_type):
        received = asyncio.get_running_loop().create_future()

        async def handle_client(reader, writer):
            try:
                received.set_result(await receive_message(reader))
                await send_control(writer, response_type, "")
            except Exception as error:
                received.set_exception(error)
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
        self.addAsyncCleanup(server.wait_closed)
        self.addCleanup(server.close)
        host, port = server.sockets[0].getsockname()[:2]
        return host, port, received

    def test_new_session_starts_disconnected(self):
        session = PeerSession("127.0.0.1", 45678)

        self.assertEqual(session.current_status, ConnectionStatus.DISCONNECTED)
        self.assertEqual(session.address, ("127.0.0.1", 45678))

    async def test_connect_and_accepted_handshake_make_session_ready(self):
        host, port, received = await self._handshake_peer(MessageType.HELLO_ACCEPT)
        session = PeerSession(host, port)
        self.addAsyncCleanup(session.close)

        await session.connect()
        self.assertEqual(session.current_status, ConnectionStatus.CONNECTED)

        await session.send_handshake()

        self.assertEqual(session.current_status, ConnectionStatus.READY)
        self.assertEqual((await asyncio.wait_for(received, timeout=1)).message_type, MessageType.HELLO)

    async def test_rejected_handshake_keeps_connection_open(self):
        host, port, _ = await self._handshake_peer(MessageType.HELLO_REJECT)
        session = PeerSession(host, port)
        self.addAsyncCleanup(session.close)

        await session.connect()

        with self.assertRaises(RejectedHandshake):
            await session.send_handshake()

        self.assertEqual(session.current_status, ConnectionStatus.CONNECTED)

    async def test_unexpected_handshake_message_is_rejected(self):
        host, port, _ = await self._handshake_peer(MessageType.FILE_ACCEPT)
        session = PeerSession(host, port)
        self.addAsyncCleanup(session.close)

        await session.connect()

        with self.assertRaises(InvalidMessageType):
            await session.send_handshake()

        self.assertEqual(session.current_status, ConnectionStatus.CONNECTED)

    async def test_answering_an_incoming_handshake_marks_session_ready(self):
        response = asyncio.get_running_loop().create_future()

        async def handle_client(reader, writer):
            try:
                response.set_result(await receive_message(reader))
            except Exception as error:
                response.set_exception(error)
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
        self.addAsyncCleanup(server.wait_closed)
        self.addCleanup(server.close)
        host, port = server.sockets[0].getsockname()[:2]
        reader, writer = await asyncio.open_connection(host, port)

        session = PeerSession(host, port)
        session.reader = reader
        session.writer = writer
        session.current_status = ConnectionStatus.CONNECTED
        self.addAsyncCleanup(session.close)

        accepted = await session.answer_handshake(accept=True)

        self.assertTrue(accepted)
        self.assertEqual(session.current_status, ConnectionStatus.READY)
        self.assertEqual(
            (await asyncio.wait_for(response, timeout=1)).message_type,
            MessageType.HELLO_ACCEPT,
        )
