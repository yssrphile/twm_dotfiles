#!/usr/bin/env python3
"""
Minimal TACACS+ server for a Cisco/EVE-NG lab.

Supports:
  - TACACS+ ASCII login authentication (GETUSER / GETPASS)
  - Basic shell authorization and privilege-level attributes
  - Accounting acknowledgements

This is a lab implementation, not a production-hardened TACACS+ server.
For production, use a maintained TACACS+ daemon with proper logging,
configuration management, TLS/network protections where applicable, etc.
"""

import hashlib
import hmac
import logging
import socket
import struct
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49
SHARED_SECRET = "eve_ng"

# Usernames and passwords are case-sensitive.
USERS = {
    "admin": {"password": "eve_ng", "priv_lvl": 15, "role": "admin"},
    "readonly": {"password": "eve_ng", "priv_lvl": 1, "role": "readonly"},
}

MAX_BODY_LENGTH = 1_048_576

# TACACS+ packet types
AUTHEN = 1
AUTHOR = 2
ACCT = 3

# Authentication reply status values
AUTHEN_STATUS_PASS = 1
AUTHEN_STATUS_FAIL = 2
AUTHEN_STATUS_GETDATA = 3
AUTHEN_STATUS_GETUSER = 4
AUTHEN_STATUS_GETPASS = 5
AUTHEN_STATUS_ERROR = 7

# Authentication methods/types/services
AUTHEN_TYPE_ASCII = 1
AUTHEN_SERVICE_LOGIN = 1

# Authorization reply status values
AUTHOR_STATUS_PASS_ADD = 1
AUTHOR_STATUS_FAIL = 16

# Accounting reply status
ACCT_STATUS_SUCCESS = 1

TAC_PLUS_UNENCRYPTED_FLAG = 0x01


def recv_exact(sock, count):
    """Read exactly count bytes from a TCP stream, or raise if it closes."""
    chunks = []
    remaining = count
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Peer closed the connection")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def crypt_body(session_id, secret, version, seq_no, body):
    """Apply the TACACS+ MD5 XOR pad (the same operation encrypts/decrypts)."""
    secret_bytes = secret.encode("utf-8")
    pad = bytearray()
    previous = b""

    while len(pad) < len(body):
        material = struct.pack("!I", session_id) + secret_bytes
        material += bytes((version, seq_no))
        if previous:
            material += previous
        previous = hashlib.md5(material).digest()
        pad.extend(previous)

    return bytes(a ^ b for a, b in zip(body, pad))


def decode_body(header, wire_body):
    version, packet_type, seq_no, flags, session_id, body_length = struct.unpack(
        "!BBBBII", header
    )
    if flags & TAC_PLUS_UNENCRYPTED_FLAG:
        return wire_body
    return crypt_body(session_id, SHARED_SECRET, version, seq_no, wire_body)


def make_packet(version, packet_type, seq_no, flags, session_id, body):
    """Build a reply using the request's version and session ID."""
    if flags & TAC_PLUS_UNENCRYPTED_FLAG:
        wire_body = body
    else:
        wire_body = crypt_body(session_id, SHARED_SECRET, version, seq_no, body)

    header = struct.pack(
        "!BBBBII",
        version,
        packet_type,
        seq_no,
        flags,
        session_id,
        len(wire_body),
    )
    return header + wire_body


def authen_reply(version, seq_no, flags, session_id, status,
                 server_msg=b"", data=b""):
    body = struct.pack("!HHBB", len(server_msg), len(data), status, 0)
    body += server_msg + data
    return make_packet(version, AUTHEN, seq_no, flags, session_id, body)


def parse_authen_start(body):
    if len(body) < 8:
        raise ValueError("Authentication START body is shorter than 8 bytes")

    action, priv_lvl, authen_type, service, user_len, port_len, rem_len, data_len = (
        struct.unpack("!BBBBBBBB", body[:8])
    )

    expected = 8 + user_len + port_len + rem_len + data_len
    if len(body) < expected:
        raise ValueError("Authentication START contains truncated fields")

    offset = 8
    username = body[offset:offset + user_len].decode("utf-8", "replace")
    offset += user_len
    port = body[offset:offset + port_len]
    offset += port_len
    remote_addr = body[offset:offset + rem_len]
    offset += rem_len
    data = body[offset:offset + data_len]

    return {
        "action": action,
        "priv_lvl": priv_lvl,
        "authen_type": authen_type,
        "service": service,
        "username": username,
        "port": port,
        "remote_addr": remote_addr,
        "data": data,
    }


def parse_authen_continue(body):
    if len(body) < 5:
        raise ValueError("Authentication CONTINUE body is shorter than 5 bytes")

    user_msg_len, data_len, flags = struct.unpack("!HHB", body[:5])
    expected = 5 + user_msg_len + data_len
    if len(body) < expected:
        raise ValueError("Authentication CONTINUE contains truncated fields")

    user_msg = body[5:5 + user_msg_len]
    data = body[5 + user_msg_len:expected]
    return user_msg, data, flags


def parse_author_request(body):
    if len(body) < 8:
        raise ValueError("Authorization request is shorter than 8 bytes")

    method, priv_lvl, authen_type, service, user_len, port_len, rem_len, arg_cnt = (
        struct.unpack("!BBBBBBBB", body[:8])
    )

    offset = 8
    fixed_total = offset + user_len + port_len + rem_len + arg_cnt
    if len(body) < fixed_total:
        raise ValueError("Authorization request has truncated fields")

    username = body[offset:offset + user_len].decode("utf-8", "replace")
    offset += user_len
    port = body[offset:offset + port_len]
    offset += port_len
    remote_addr = body[offset:offset + rem_len]
    offset += rem_len

    arg_lengths = body[offset:offset + arg_cnt]
    offset += arg_cnt

    args = []
    for arg_len in arg_lengths:
        if offset + arg_len > len(body):
            raise ValueError("Authorization argument is truncated")
        args.append(body[offset:offset + arg_len].decode("utf-8", "replace"))
        offset += arg_len

    return username, args


def author_reply(version, seq_no, flags, session_id, status, args=None,
                 server_msg=b"", data=b""):
    args = args or []
    encoded_args = [arg.encode("utf-8") for arg in args]

    if len(encoded_args) > 255 or any(len(arg) > 255 for arg in encoded_args):
        raise ValueError("Too many or oversized authorization reply arguments")

    body = struct.pack(
        "!BBHH",
        status,
        len(encoded_args),
        len(server_msg),
        len(data),
    )
    body += bytes(len(arg) for arg in encoded_args)
    body += b"".join(encoded_args)
    body += server_msg + data

    return make_packet(version, AUTHOR, seq_no, flags, session_id, body)


def handle_authentication(body, version, seq_no, flags, session_id, sessions):
    # START packets use odd sequence numbers; server replies use the next even number.
    if seq_no == 1:
        start = parse_authen_start(body)

        if start["authen_type"] != AUTHEN_TYPE_ASCII:
            logging.warning(
                "Session %08x requested unsupported authentication type %d",
                session_id, start["authen_type"]
            )
            return authen_reply(
                version, seq_no + 1, flags, session_id,
                AUTHEN_STATUS_ERROR, b"Only ASCII authentication is supported"
            )

        username = start["username"].strip()
        sessions[session_id] = {
            "username": username,
            "stage": "password" if username else "username",
        }

        if username:
            logging.info("Session %08x: requesting password for user %r",
                         session_id, username)
            return authen_reply(
                version, seq_no + 1, flags, session_id,
                AUTHEN_STATUS_GETPASS, b"Password: "
            )

        logging.info("Session %08x: requesting username", session_id)
        return authen_reply(
            version, seq_no + 1, flags, session_id,
            AUTHEN_STATUS_GETUSER, b"Username: "
        )

    if seq_no < 3 or seq_no % 2 == 0:
        logging.warning("Session %08x: unexpected authentication sequence %d",
                        session_id, seq_no)
        return authen_reply(
            version, seq_no + 1, flags, session_id,
            AUTHEN_STATUS_ERROR, b"Unexpected authentication sequence"
        )

    state = sessions.get(session_id)
    if not state:
        logging.warning("Session %08x: CONTINUE received without START", session_id)
        return authen_reply(
            version, seq_no + 1, flags, session_id,
            AUTHEN_STATUS_ERROR, b"Missing authentication session"
        )

    user_msg, _data, _continue_flags = parse_authen_continue(body)
    value = user_msg.decode("utf-8", "replace").strip()

    if state["stage"] == "username":
        state["username"] = value
        state["stage"] = "password"
        logging.info("Session %08x: received username %r; requesting password",
                     session_id, value)
        return authen_reply(
            version, seq_no + 1, flags, session_id,
            AUTHEN_STATUS_GETPASS, b"Password: "
        )

    username = state["username"]
    user_record = USERS.get(username)

    # Do not log the password.
    authenticated = bool(
        user_record
        and hmac.compare_digest(
            value.encode("utf-8"),
            user_record["password"].encode("utf-8"),
        )
    )

    sessions.pop(session_id, None)

    if authenticated:
        logging.info("Session %08x: authentication PASS for user %r",
                     session_id, username)
        return authen_reply(
            version, seq_no + 1, flags, session_id,
            AUTHEN_STATUS_PASS
        )

    logging.warning("Session %08x: authentication FAIL for user %r",
                    session_id, username)
    return authen_reply(
        version, seq_no + 1, flags, session_id,
        AUTHEN_STATUS_FAIL, b"Authentication failed"
    )


def handle_authorization(body, version, seq_no, flags, session_id):
    username, args = parse_author_request(body)
    user_record = USERS.get(username)

    logging.info("Session %08x: authorization request user=%r args=%s",
                 session_id, username, args)

    if not user_record:
        return author_reply(
            version, seq_no + 1, flags, session_id,
            AUTHOR_STATUS_FAIL, server_msg=b"Unknown user"
        )

    # Basic lab policy: readonly users cannot execute configure commands.
    if user_record.get("role") == "readonly":
        command = next(
            (arg.split("=", 1)[1] for arg in args if arg.startswith("cmd=")),
            ""
        ).strip().lower()

        if command in {"configure", "conf"}:
            logging.info("Authorization denied: readonly user %r requested %r",
                         username, command)
            return author_reply(
                version, seq_no + 1, flags, session_id,
                AUTHOR_STATUS_FAIL, server_msg=b"Command not permitted"
            )

    reply_args = [f"priv-lvl={user_record['priv_lvl']}"]
    return author_reply(
        version, seq_no + 1, flags, session_id,
        AUTHOR_STATUS_PASS_ADD, args=reply_args
    )


def handle_accounting(body, version, seq_no, flags, session_id):
    # A minimal accounting acknowledgement. This does not persist accounting records.
    reply_body = struct.pack("!HHB", 0, 0, ACCT_STATUS_SUCCESS)
    return make_packet(
        version, ACCT, seq_no + 1, flags, session_id, reply_body
    )


def handle_client(client_socket, address):
    sessions = {}
    logging.info("Connection from %s:%s", *address)

    try:
        while True:
            header = recv_exact(client_socket, 12)
            version, packet_type, seq_no, flags, session_id, body_length = (
                struct.unpack("!BBBBII", header)
            )

            if body_length > MAX_BODY_LENGTH:
                raise ValueError(f"Packet body too large: {body_length}")

            wire_body = recv_exact(client_socket, body_length)
            body = decode_body(header, wire_body)

            logging.debug(
                "RX type=%d seq=%d session=%08x version=0x%02x length=%d flags=0x%02x",
                packet_type, seq_no, session_id, version, body_length, flags
            )

            if packet_type == AUTHEN:
                response = handle_authentication(
                    body, version, seq_no, flags, session_id, sessions
                )
            elif packet_type == AUTHOR:
                response = handle_authorization(
                    body, version, seq_no, flags, session_id
                )
            elif packet_type == ACCT:
                response = handle_accounting(
                    body, version, seq_no, flags, session_id
                )
            else:
                logging.warning("Unsupported TACACS+ packet type %d", packet_type)
                break

            client_socket.sendall(response)

    except ConnectionError:
        logging.info("Connection closed by %s:%s", *address)
    except Exception:
        logging.exception("Error handling connection from %s:%s", *address)
    finally:
        client_socket.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(20)
        logging.info("TACACS+ lab server listening on %s:%d", LISTEN_IP, LISTEN_PORT)
        logging.info("Configured users: %s", ", ".join(USERS))

        while True:
            client, address = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True,
            )
            thread.start()

    except KeyboardInterrupt:
        logging.info("Shutting down")
    finally:
        server.close()


if __name__ == "__main__":
    main()
