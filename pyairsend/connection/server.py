import asyncio

from pyairsend.connection.session import PeerSession


class PeerServer:
    host = "0.0.0.0"  # Listen on all available interfaces
    port = 12345  # Default port for the server
    address = f"{host}:{port}"
    status = "stopped"

    class ServerStatus:
        STARTING = "starting"
        RUNNING = "running"
        STOPPED = "stopped"
        FAILED = "failed"

    async def start(self):
        """Start the server to listen for incoming connections."""

        self.status = self.ServerStatus.STARTING

        try:
            self.server = await asyncio.start_server(
                self._handle_connection,  # func to handle incoming connections
                host=self.host,
                port=self.port,
            )

        except Exception as e:
            self.status = self.ServerStatus.FAILED
            raise e

        self.status = self.ServerStatus.RUNNING

    async def stop(self):
        """ Stop the server and close all connections """
        self.server.close()
        self.status = self.ServerStatus.STOPPED

        await self.server.wait_closed()

    async def _handle_connection(self, reader, writer):
        session = PeerSession.from_streams(reader, writer)

        try:
            await session.receive_handshake()
            # TODO: notify controller/UI about this ready peer

            accepted = True  # TODO: Implement UI logic to accept or reject the handshake
            await session.answer_handshake(accept=accepted)

            if not accepted:
                return

            print(f"Handshake accepted from {session.peer_address}:{session.peer_port}. Session is ready.")
            await self._handle_ready_session(session)

            # TODO: wait for file offer and pass it to file receiver

        finally:
            await session.close()

    async def _handle_ready_session(self, session: PeerSession):
        """Handle a session that has completed the handshake and is ready for communication."""

        while True:
            try:
                message = await session.receive_message()

                # TODO: implement logic to handle different messages
                break  # For now, just break the loop to close the session

            except asyncio.IncompleteReadError:
                print("Peer disconnected.")
                break

            except Exception as error:
                print(f"Peer error: {error}")
                break
