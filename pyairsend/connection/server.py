import asyncio
from enum import StrEnum

from pyairsend.connection.session import PeerSession


class ServerStatus(StrEnum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class PeerServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.address = f"{host}:{port}"
        self.status = ServerStatus.STOPPED

    async def start(self):
        """Start the server to listen for incoming connections."""
        self.status = ServerStatus.STARTING

        try:
            self.server = await asyncio.start_server(
                self._handle_connection,  # func to handle incoming connections
                host=self.host,
                port=self.port,
            )

        except Exception as e:
            self.status = ServerStatus.FAILED
            raise e

        self.status = ServerStatus.RUNNING

    async def stop(self):
        """ Stop the server and close all connections """
        self.server.close()
        self.status = ServerStatus.STOPPED

        await self.server.wait_closed()

    async def _handle_connection(self, reader, writer):
        session = None

        try:
            session = PeerSession.from_streams(reader, writer)

            await asyncio.wait_for(
                session.receive_handshake(),
                timeout=5.0
            )

            # TODO: notify controller/UI about this ready peer

            accepted = True  # TODO: Implement UI logic to accept or reject the handshake
            await session.answer_handshake(accept=accepted)

            if not accepted:
                return

            print(
                f"Handshake accepted from {session.peer_address}:{session.peer_port}. "
                "Session is ready."
            )

            await self._handle_ready_session(session)

            # TODO: wait for file offer and pass it to file receiver

        except Exception as e:
            raise

        finally:
            if session is not None:
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
