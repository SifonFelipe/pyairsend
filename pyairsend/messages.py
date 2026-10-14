import struct
from enum import IntEnum


class MessageType(IntEnum):
    """
    Available message types for the file transfer protocol.
    """
    HELLO = 1
    FILE_OFFER = 2
    FILE_ACCEPT = 3
    FILE_REJECT = 4
    FILE_CHUNK = 5
    FILE_COMPLETE = 6


MAX_MESSAGE_SIZE = 100 * 1024 * 1024
HEADER_FORMAT = "!BI"  # Message type (1 byte) + Payload length (4 bytes)
# CHUNKS_HEADER_FORMAT = "!BII"  # Message type + Chunk number + Payload length

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
# CHUNK_HEADER_SIZE = struct.calcsize(CHUNKS_HEADER_FORMAT)


def create_message(message_type: MessageType, payload: bytes) -> bytes:
    """
    Create a message with the given type and payload.

    > message_type: The type of the message.
    > payload: The payload of the message as bytes.
    > return: The complete message as bytes.
    """
    payload_length = len(payload)
    header = struct.pack(HEADER_FORMAT, message_type.value, payload_length)
    return header + payload
