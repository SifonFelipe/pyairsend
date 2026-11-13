import asyncio
import struct
import unittest

from pyairsend.protocol.messages import (
    CHUNK_HEADER,
    MAX_CHUNK_PAYLOAD_SIZE,
    MessageType
)
from pyairsend.transport.socket_io import receive_message, send_chunk, send_control


class SocketIOTests(unittest.IsolatedAsyncioTestCase):
    async def _start_server(self, handler):
        server = await asyncio.start_server(handler, "127.0.0.1", 0)
        self.addAsyncCleanup(server.wait_closed)
        self.addCleanup(server.close)
        host, port = server.sockets[0].getsockname()[:2]
        return host, port

    async def test_control_message_round_trip(self):
        received = asyncio.get_running_loop().create_future()

        async def handle_client(reader, writer):
            try:
                received.set_result(await receive_message(reader))
            except Exception as error:
                received.set_exception(error)
            finally:
                writer.close()
                await writer.wait_closed()

        host, port = await self._start_server(handle_client)
        _, writer = await asyncio.open_connection(host, port)
        self.addAsyncCleanup(self._close_writer, writer)

        await send_control(writer, MessageType.FILE_OFFER, '{"name":"photo.png"}')
        message = await asyncio.wait_for(received, timeout=1)

        self.assertEqual(message.message_type, MessageType.FILE_OFFER)
        self.assertEqual(message.payload, '{"name":"photo.png"}')
        self.assertEqual(message.payload_length, len(message.payload.encode()))

    async def test_chunk_round_trip(self):
        received = asyncio.get_running_loop().create_future()
        payload = b"a small part of a file"

        async def handle_client(reader, writer):
            try:
                received.set_result(await receive_message(reader))
            except Exception as error:
                received.set_exception(error)
            finally:
                writer.close()
                await writer.wait_closed()

        host, port = await self._start_server(handle_client)
        _, writer = await asyncio.open_connection(host, port)
        self.addAsyncCleanup(self._close_writer, writer)

        await send_chunk(writer, 3, payload)
        message = await asyncio.wait_for(received, timeout=1)

        self.assertEqual(message.message_type, MessageType.FILE_CHUNK)
        self.assertEqual(message.chunk_number, 3)
        self.assertEqual(message.payload_length, len(payload))
        self.assertEqual(message.payload, payload)

    async def test_closed_connection_raises_incomplete_read_error(self):
        async def handle_client(reader, writer):
            writer.write(b"\x01\x00\x00")
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        host, port = await self._start_server(handle_client)
        reader, writer = await asyncio.open_connection(host, port)
        self.addAsyncCleanup(self._close_writer, writer)

        with self.assertRaises(asyncio.IncompleteReadError):
            await receive_message(reader)

    async def test_rejects_oversized_chunk_before_reading_its_payload(self):
        async def handle_client(reader, writer):
            writer.write(
                struct.pack(
                    CHUNK_HEADER.format,
                    MessageType.FILE_CHUNK.value,
                    0,
                    MAX_CHUNK_PAYLOAD_SIZE + 1,
                )
            )
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        host, port = await self._start_server(handle_client)
        reader, writer = await asyncio.open_connection(host, port)
        self.addAsyncCleanup(self._close_writer, writer)

        with self.assertRaises(ValueError):
            await receive_message(reader)

    async def _close_writer(self, writer):
        writer.close()
        try:
            await writer.wait_closed()
        except ConnectionError:
            pass
