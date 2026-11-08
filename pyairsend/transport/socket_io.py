"""Message-oriented I/O for connected sockets."""
import asyncio

from pyairsend.protocol.messages import (
    MessageType,
    ControlMessage,
    ChunkMessage,
    get_header,
)

from pyairsend.protocol.codec import (
    Encoder,
    Decoder,
)


async def receive_message(reader: asyncio.StreamReader):
    """ receive a message from the client socket """
    # receive message_type
    message_type_byte = await reader.readexactly(1)
    message_type = Decoder.decode_message_type(message_type_byte)

    # get the header for the message type
    header = get_header(message_type)

    # receive the rest of the header
    remaining_header = await reader.readexactly(header.size_after_message_type())

    # decode according to message type
    if message_type == MessageType.FILE_CHUNK:
        chunk_number, payload_length = Decoder.decode_chunk_header(remaining_header)

        payload = await reader.readexactly(payload_length)

        return ChunkMessage(
            message_type=message_type,
            chunk_number=chunk_number,
            payload_length=payload_length,
            payload=payload,
        )

    # elif header == CONTROL_HEADER:
    payload_length = Decoder.decode_control_header(remaining_header)

    payload_bytes = await reader.readexactly(payload_length)
    payload = payload_bytes.decode(header.text_encoding)

    return ControlMessage(
        message_type=message_type,
        payload_length=payload_length,
        payload=payload,
    )


async def send_control(writer: asyncio.StreamWriter, message_type: MessageType, message: str):
    """ send a control message to the client socket """
    encoded = Encoder.encode_control(message_type, message)

    writer.write(encoded)
    await writer.drain()


async def send_chunk(writer: asyncio.StreamWriter, chunk_number: int, payload: bytes):
    """ send a chunk message to the client socket """
    encoded = Encoder.encode_chunk(chunk_number, payload)

    writer.write(encoded)
    await writer.drain()
