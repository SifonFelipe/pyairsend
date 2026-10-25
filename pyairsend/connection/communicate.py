from pyairsend.protocol.messages import (
    decode_header, encode, decode,
    FORMAT, HEADER_SIZE, MAX_MESSAGE_SIZE
)


def receive(client, recv_exactly) -> bytes:
    """ receive payload_length bytes from the client socket """

    payload = bytearray()

    while len(payload) < recv_exactly:
        chunk = client.recv(recv_exactly - len(payload))

        if chunk == b'':
            raise ConnectionError("Socket connection broken")

        payload += chunk

    return bytes(payload)


def send_message(client, msg, msg_type):
    """ send encoded message to the client socket """
    encoded_msg = encode(msg_type, msg)

    client.sendall(encoded_msg)

    # response = client.recv(1024).decode(FORMAT)


def receive_message(client):
    # receives header and decodes it to get the payload length
    header = receive(client, HEADER_SIZE)
    msg_type, payload_length = decode_header(header)

    if payload_length > MAX_MESSAGE_SIZE:
        raise ValueError("Payload length exceeds maximum message size.")

    # receives the payload based on the length specified in the header
    payload = receive(client, payload_length)
    return decode(header + payload)
