import socket

from pyairsend.connection.communicate import receive, send_message, receive_message

from pyairsend.protocol.messages import (
    decode_header, encode, decode, MessageType,
    FORMAT, HEADER_SIZE, MAX_MESSAGE_SIZE
)


class TransferNegotiator:
    """
    A class to handle the negotiation of a file transfer connection with a peer.
    """

    def __init__(self, peer_address):
        """
        Initialize the TransferNegotiator with the peer's address.

        Args:
            peer_address (str): The address of the peer to connect to.
        """
        self.peer_address = peer_address
        self.sock = None

    def connect_to_peer(self):
        """
        Establish a connection to the peer at the given address.

        Returns:
            socket: A socket object representing the connection to the peer.
        """
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the peer's address
        self.sock.connect(self.peer_address)

    def negotiate_connection(self):
        """
        Negotiate the connection with the peer by sending a HELLO message and waiting for a response

        Returns:
            bool: True if the negotiation was successful, False otherwise.
        """
        if not self.sock:
            raise ValueError("Socket is not connected. Call connect_to_peer() first.")

        # Send a HELLO message to the peer
        hello_message = "HELLO"
        send_message(self.sock, hello_message, MessageType.HELLO)

        # Wait for a response from the peer
        response_msg_type, response_msg = receive_message(self.sock)

        # Check if the response is a HELLO message
        if response_msg_type == MessageType.HELLO:
            return True

        return False

    def negotiate(self):
        """
        Negotiate the connection with the peer.

        Returns:
            bool: True if the negotiation was successful, False otherwise.
        """
        try:
            self.sock = self.connect_to_peer()
            return self.negotiate_connection()

        except Exception as e:
            print(f"Negotiation failed: {e}")
            return False

        finally:
            if self.sock:
                self.sock.close()
