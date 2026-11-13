import struct
import unittest

from pyairsend.protocol.codec import Decoder, Encoder
from pyairsend.protocol.messages import (
    CHUNK_HEADER,
    CONTROL_HEADER,
    MAX_CONTROL_PAYLOAD_SIZE,
    MessageType,
)


class EncoderDecoderTests(unittest.TestCase):
    def test_control_message_encodes_type_length_and_payload(self):
        encoded = Encoder.encode_control(MessageType.HELLO, "hello")

        message_type, payload_length = struct.unpack(
            CONTROL_HEADER.format, encoded[: CONTROL_HEADER.size]
        )

        self.assertEqual(message_type, MessageType.HELLO.value)
        self.assertEqual(payload_length, len(b"hello"))
        self.assertEqual(encoded[CONTROL_HEADER.size :], b"hello")

    def test_chunk_encodes_type_number_length_and_payload(self):
        payload = b"file data"
        encoded = Encoder.encode_chunk(7, payload)

        message_type, chunk_number, payload_length = struct.unpack(
            CHUNK_HEADER.format, encoded[: CHUNK_HEADER.size]
        )

        self.assertEqual(message_type, MessageType.FILE_CHUNK.value)
        self.assertEqual(chunk_number, 7)
        self.assertEqual(payload_length, len(payload))
        self.assertEqual(encoded[CHUNK_HEADER.size :], payload)

    def test_control_header_rejects_an_oversized_payload(self):
        header = struct.pack("!I", MAX_CONTROL_PAYLOAD_SIZE + 1)

        with self.assertRaises(ValueError):
            Decoder.decode_control_header(header)

    def test_unknown_message_type_is_rejected(self):
        with self.assertRaises(ValueError):
            Decoder.decode_message_type(b"\xff")
