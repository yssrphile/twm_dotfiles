
    
  
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

