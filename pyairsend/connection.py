from pyairsend.messages import decode_header, encode, decode, FORMAT


def send_message(client, msg, msg_type):
    encoded_msg = encode(msg_type, msg)

    client.send(encoded_msg)

    # response = client.recv(1024).decode(FORMAT)


def receive_message(client):
    # receives header and decodes it to get the payload length
    header = client.recv(5)
    msg_type, payload_length = decode_header(header)

    # receives the payload based on the length specified in the header
    payload = client.recv(payload_length)
    msg_type, msg = decode(header + payload)

    return msg_type, msg

