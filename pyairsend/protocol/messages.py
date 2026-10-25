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
HEADER_FORMAT = "!BI"  # big-endian + Message type (1 byte) + Payload length (4 bytes)
FORMAT = "utf-8"
# CHUNKS_HEADER_FORMAT = "!BII"  # Message type + Chunk number + Payload length

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
# CHUNK_HEADER_SIZE = struct.calcsize(CHUNKS_HEADER_FORMAT)


def encode(message_type: MessageType, message: str) -> bytes:
    """
    Create a message with the given type and payload. Encodes.

    > message_type: The type of the message.
    > payload: The payload of the message as bytes.
    > return: The complete message as bytes.
    """
    payload = message.encode(FORMAT)
    payload_length = len(payload)
    header = struct.pack(HEADER_FORMAT, message_type.value, payload_length)
    return header + payload


def decode_header(header: bytes) -> tuple[MessageType, int]:
    """
    Decode a message header into its type and payload length.

    > header: The message header as bytes.
    > return: A tuple containing the message type and payload length.
    """
    msg_type_value, payload_length = struct.unpack(HEADER_FORMAT, header)
    msg_type = MessageType(msg_type_value)
    return msg_type, payload_length


def decode(message: bytes) -> tuple[MessageType, str]:
    """
    Decode a message into its type and payload.

    > message: The complete message as bytes.
    > return: A tuple containing the message type and payload as a string.
    """
    header = message[:HEADER_SIZE]
    payload = message[HEADER_SIZE:]

    msg_type_value, payload_length = struct.unpack(HEADER_FORMAT, header)
    msg_type = MessageType(msg_type_value)

    if len(payload) != payload_length:
        raise ValueError("Payload length does not match the length specified in the header.")

    return msg_type, payload.decode(FORMAT)
