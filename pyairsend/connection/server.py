import asyncio

from pyairsend.connection.session import PeerSession


class PeerServer:
    host = "0.0.0.0"  # Listen on all available interfaces
    port = 12345  # Default port for the server

    async def start(self):
        """Start the server to listen for incoming connections."""
        self.server = await asyncio.start_server(
            self._handle_connection,
            host=self.host,
            port=self.port,
        )

    async def _handle_connection(self, reader, writer):
        session = PeerSession.from_streams(reader, writer)

        try:
            await session.receive_handshake()
            # TODO: notify controller/UI about this ready peer

            answer = True  # TODO: Implement UI logic to accept or reject the handshake
            await session.answer_handshake(accept=answer)

            # TODO: wait for file offer and pass it to file receiver

        finally:
            await session.close()

    async def stop(self):
        """ Stop the server and close all connections """
        self.server.close()
        await self.server.wait_closed()
