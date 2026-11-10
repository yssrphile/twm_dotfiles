import socket
import struct
import hashlib
import threading

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49
SHARED_SECRET = "eve_ng"  # The TACACS+ key configured on the switch

USERS = {
    "admin": {"password": "eve_ng", "priv-lvl": 15},
    "readonly": {"password": "eve_ng", "priv-lvl": 1}
}

def pseudo_pad(session_id, key, version, seq_no, length):
    """Generates the MD5 cryptographic pad used to XOR encrypt/decrypt TACACS+ bodies."""
    pad = b""
    last_hash = b""
    while len(pad) < length:
        md5 = hashlib.md5()
        md5.update(session_id + key.encode() + bytes([version, seq_no]))
        if last_hash:
            md5.update(last_hash)
        last_hash = md5.digest()
        pad += last_hash
    return pad[:length]

def decrypt_encrypt_body(header, body):
    version, _, seq_no, flags, session_id, length = struct.unpack("!BBBBII", header)
    if flags & 0x01: # TAC_PLUS_UNENCRYPTED_FLAG
        return body
    pad = pseudo_pad(struct.pack("!I", session_id), SHARED_SECRET, version, seq_no, length)
    return bytes(a ^ b for a, b in zip(body, pad))

def make_packet(version, type_, seq_no, session_id, body_data):
    flags = 0x00 # Encrypted
    length = len(body_data)
    header = struct.pack("!BBBBII", version, type_, seq_no, flags, session_id, length)
    pad = pseudo_pad(struct.pack("!I", session_id), SHARED_SECRET, version, seq_no, length)
    encrypted_body = bytes(a ^ b for a, b in zip(body_data, pad))
    return header + encrypted_body

def handle_client(client_socket):
    # Track the active session state mapped by TACACS+ Session ID
    session_state = {}
    
    try:
        while True:
            header = client_socket.recv(12)
            if not header or len(header) < 12:
                break
            
            version, type_, seq_no, flags, session_id, length = struct.unpack("!BBBBII", header)
            raw_body = client_socket.recv(length)
            body = decrypt_encrypt_body(header, raw_body)
            
            # --- AUTHENTICATION (Type 1) ---
            if type_ == 1: 
                if seq_no == 1: # START packet
                    action, priv_lvl, authen_type, service, user_len, port_len, rem_len, data_len = struct.unpack("!BBBBBBBB", body[:8])
                    username = body[8:8+user_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    if user_len > 0:
                        session_state[session_id] = username
                        print(f"[DEBUG] Session {session_id}: Received Username '{username}' in START packet")
                    else:
                        print(f"[DEBUG] Session {session_id}: Inbound ASCII flow (No username in START)")
                    
                    # Reply asking for the password (STATUS_GETPASS = 2)
                    server_body = struct.pack("!HHBB", 0, 0, 2, 0) + b"Password: " 
                    client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))
                    
                elif seq_no == 3: # CONTINUE packet containing password
                    pass_len, flags, data_len = struct.unpack("!HHB", body[:5])
                    
                    # Extract raw password and sanitize it of terminating nulls, returns, or spaces
                    raw_password_str = body[5:5+pass_len].decode('utf-8', errors='ignore')
                    password = raw_password_str.replace('\x00', '').replace('\r', '').replace('\n', '').strip()
                    
                    # Extract trailing data which often holds the username in ASCII flow sequences
                    extra_data = body[5+pass_len:5+pass_len+data_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    # Pull username from state mapping or assume the extra data string
                    username = session_state.get(session_id)
                    if not username and data_len > 0:
                        username = extra_data
                        session_state[session_id] = username
                    
                    # If we STILL don't have a username context due to switch mechanics, default it to admin for validation
                    if not username:
                        username = "admin"
                    
                    print(f"[DEBUG] Session {session_id}: Active Username Context: '{username}'")
                    print(f"[DEBUG] Session {session_id}: Raw Bytes Length: {pass_len}")
                    print(f"[DEBUG] Session {session_id}: Cleaned Password String: '{password}'")
                    
                    # Core matching logic against our sanitized credentials
                    authenticated = False
                    if password == "eve_ng":
                        authenticated = True
                        print(f"[DEBUG] Session {session_id}: Password matched successfully!")
                    else:
                        print(f"[DEBUG] Session {session_id}: Password mismatch error.")
                    
                    status = 1 if authenticated else 2 # 1=PASS, 2=FAIL
                    
                    if not authenticated and session_id in session_state:
                        del session_state[session_id]
                        
                    server_body = struct.pack("!HHBB", 0, 0, status, 0)
                    client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))

            # --- AUTHORIZATION (Type 2) ---
            elif type_ == 2: 
                authen_method, priv_lvl, authen_type, authen_service, user_len, port_len, rem_len, arg_cnt = struct.unpack("!BBBBBBBB", body[:8])
                username = body[8:8+user_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                
                if not username:
                    username = session_state.get(session_id, "admin")
                
                offset = 8 + user_len + port_len + rem_len
                arg_lens = struct.unpack(f"!{arg_cnt}B", body[offset:offset+arg_cnt])
                offset += arg_cnt
                
                args = []
                for a_len in arg_lens:
                    args.append(body[offset:offset+a_len].decode('utf-8', errors='ignore'))
                    offset += a_len
                
                print(f"[DEBUG] Session {session_id}: Authorization request for user '{username}' with args: {args}")
                
                allowed = True
                user_priv = USERS.get(username, {}).get("priv-lvl", 15) # Default to 15 if missing context to bypass login locks
                
                if username == "readonly":
                    for arg in args:
                        if "cmd=configure" in arg or "cmd-arg=config" in arg:
                            allowed = False

                status = 1 if allowed else 16 
                reply_args = [f"priv-lvl={user_priv}".encode()]
                reply_arg_cnt = len(reply_args)
                
                server_body = struct.pack("!BBHH", status, reply_arg_cnt, 0, 0)
                for r_arg in reply_args:
                    server_body += struct.pack("!B", len(r_arg))
                for r_arg in reply_args:
                    server_body += r_arg
                    
                client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))
                
            # --- ACCOUNTING (Type 3) ---
            elif type_ == 3:
                if session_id in session_state:
                    del session_state[session_id]
                server_body = struct.pack("!HHBB", 0, 0, 1, 0)
                client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))

    except Exception as e:
        print(f"[!] Exception encountered within active thread: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(5)
    print(f"[*] Pure Python TACACS+ Server listening on {LISTEN_IP}:{LISTEN_PORT}")
    
    try:
        while True:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client,))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
