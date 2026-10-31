import struct

from pyairsend.protocol.messages import (
    MessageType,
    CONTROL_HEADER,
    CHUNK_HEADER,
    MAX_MESSAGE_SIZE
)


def assert_message_size(payload_length):
    if payload_length > MAX_MESSAGE_SIZE:
        raise ValueError(
            f"Payload size exceeds maximum allowed size "
            f"of {MAX_MESSAGE_SIZE} bytes."
        )


class Encoder:
    @staticmethod
    def encode_control(message_type, message: str, encoding="utf-8") -> bytes:
        payload = message.encode(encoding)

        header = struct.pack(
            CONTROL_HEADER.format,
            message_type.value,
            len(payload)
        )

        return header + payload

    @staticmethod
    def encode_chunk(chunk_number, data: bytes) -> bytes:
        header = struct.pack(
            CHUNK_HEADER.format,
            MessageType.FILE_CHUNK.value,
            chunk_number,
            len(data)
        )

        return header + data


class Decoder:
    @staticmethod
    def decode_message_type(message_type_byte: bytes) -> MessageType:
        msg_type = struct.unpack("!B", message_type_byte)[0]
        return MessageType(msg_type)

    @staticmethod
    def decode_control_header(header: bytes) -> int:
        payload_length = struct.unpack(
            CONTROL_HEADER.get_format_after_message_type(),
            header
        )[0]

        assert_message_size(payload_length)

        return payload_length

    @staticmethod
    def decode_chunk_header(header: bytes) -> tuple[int, int]:
        chunk_number, payload_length = struct.unpack(
            CHUNK_HEADER.get_format_after_message_type(),
            header
        )

        assert_message_size(payload_length)

        return chunk_number, payload_length
