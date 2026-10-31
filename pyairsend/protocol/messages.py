import struct
from enum import IntEnum
from dataclasses import dataclass


class MessageType(IntEnum):
    """
    Available message types for the file transfer protocol.
    """
    HELLO = 1
    FILE_OFFER = 2
    FILE_ACCEPT = 3
    FILE_REJECT = 4
    FILE_CHUNK = 5  # data message
    FILE_COMPLETE = 6


class MessageHeader:
    """
    Represents a message header in the file transfer protocol.
    """
    format: str
    size: int
    text_encoding: str = "utf-8"

    def __init__(self, format):
        self.format = format
        self.size = struct.calcsize(format)

    def get_format_after_message_type(self) -> str:
        return self.format.replace("B", "", 1)  # Remove the first 'B'

    def size_after_message_type(self) -> int:
        return self.size - struct.calcsize("!B")


@dataclass
class ControlMessage:
    message_type: int
    payload_length: int
    payload: str


@dataclass
class ChunkMessage:
    message_type: int
    chunk_number: int
    payload_length: int
    payload: bytes


CONTROL_HEADER = MessageHeader("!BI")  # Message type (1 byte) + Payload length (4 bytes)
CHUNK_HEADER = MessageHeader("!BII")  # Message type + Chunk number + Payload length

HEADER_BY_MESSAGE_TYPE = {
    MessageType.HELLO: CONTROL_HEADER,
    MessageType.FILE_OFFER: CONTROL_HEADER,
    MessageType.FILE_ACCEPT: CONTROL_HEADER,
    MessageType.FILE_REJECT: CONTROL_HEADER,
    MessageType.FILE_CHUNK: CHUNK_HEADER,
    MessageType.FILE_COMPLETE: CONTROL_HEADER,
}

MAX_MESSAGE_SIZE = 100 * 1024 * 1024


def get_header(message_type: MessageType) -> MessageHeader:
    return HEADER_BY_MESSAGE_TYPE[message_type]
