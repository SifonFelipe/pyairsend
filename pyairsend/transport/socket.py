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


def receive_exactly(client, size: int) -> bytes:
    """ receive exactly `size` bytes from the client socket """
    data = bytearray()

    while len(data) < size:
        chunk = client.recv(size - len(data))

        if chunk == b"":
            raise ConnectionError("Socket connection broken")

        data += chunk

    return bytes(data)


def receive_message(client):
    """ receive a message from the client socket """
    # receive message_type
    message_type_byte = receive_exactly(client, 1)
    message_type = Decoder.decode_message_type(message_type_byte)

    # get the header for the message type
    header = get_header(message_type)

    # receive the rest of the header
    remaining_header = receive_exactly(client, header.size_after_message_type())

    # decode according to message type
    if message_type == MessageType.FILE_CHUNK:
        chunk_number, payload_length = Decoder.decode_chunk_header(remaining_header)

        payload = receive_exactly(client, payload_length)

        return ChunkMessage(
            message_type=message_type,
            chunk_number=chunk_number,
            payload_length=payload_length,
            payload=payload,
        )

    # elif header == CONTROL_HEADER:
    payload_length = Decoder.decode_control_header(remaining_header)

    payload_bytes = receive_exactly(client, payload_length)
    payload = payload_bytes.decode(header.text_encoding)

    return ControlMessage(
        message_type=message_type,
        payload_length=payload_length,
        payload=payload,
    )


def send_control(client, message_type: MessageType, message: str):
    """ send a control message to the client socket """
    encoded = Encoder.encode_control(message_type, message)

    client.sendall(encoded)


def send_chunk(client, chunk_number: int, payload: bytes):
    """ send a chunk message to the client socket """
    encoded = Encoder.encode_chunk(chunk_number, payload)

    client.sendall(encoded)
