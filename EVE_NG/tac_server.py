import socket
import struct
import hashlib
import threading

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 49
SHARED_SECRET = "eve_ng"  # Must exactly match your 'tacacs-server key eve_ng' configuration

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
    
    # CISCO IOS COMPLIANCE FIX: If this is an Authentication packet (Type 1),
    # force the minor version flag to 1 (0xc1) so Cisco accepts the response step.
    if type_ == 1:
        version = 0xc1
        
    header = struct.pack("!BBBBII", version, type_, seq_no, flags, session_id, length)
    pad = pseudo_pad(struct.pack("!I", session_id), SHARED_SECRET, version, seq_no, length)
    encrypted_body = bytes(a ^ b for a, b in zip(body_data, pad))
    return header + encrypted_body

def handle_client(client_socket):
    # Track the active session steps and user mappings dynamically 
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
                if seq_no == 1: # START packet from Cisco IOS
                    action, priv_lvl, authen_type, service, user_len, port_len, rem_len, data_len = struct.unpack("!BBBBBBBB", body[:8])
                    username = body[8:8+user_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    if user_len > 0:
                        # Cisco explicitly sent the username on packet 1
                        session_state[session_id] = {"username": username, "step": "expect_pass"}
                        print(f"[DEBUG] Session {session_id}: Cisco sent Username '{username}' in START. Prompting for password.")
                        server_body = struct.pack("!HHBB", 0, 0, 2, 0) + b"Password: " # STATUS_GETPASS = 2
                    else:
                        # Cisco initiated a blind ASCII login. We MUST ask for Username first.
                        session_state[session_id] = {"username": "", "step": "expect_user"}
                        print(f"[DEBUG] Session {session_id}: Pure ASCII Flow. Prompting Cisco for Username.")
                        server_body = struct.pack("!HHBB", 0, 0, 1, 0) + b"Username: " # STATUS_GETUSER = 1
                    
                    client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))
                    
                elif seq_no == 3: # First CONTINUE packet from Cisco
                    pass_len, flags, data_len = struct.unpack("!HHB", body[:5])
                    payload = body[5:5+pass_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    state = session_state.get(session_id, {"username": "", "step": "expect_user"})
                    
                    if state["step"] == "expect_user":
                        # This payload is actually the Username string
                        username = payload
                        session_state[session_id] = {"username": username, "step": "expect_pass"}
                        print(f"[DEBUG] Session {session_id}: Received Username target: '{username}'. Now prompting for Password.")
                        
                        # Reply asking for the password
                        server_body = struct.pack("!HHBB", 0, 0, 2, 0) + b"Password: " # STATUS_GETPASS = 2
                        client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))
                        
                    elif state["step"] == "expect_pass":
                        # This payload is the Password string
                        password = payload
                        username = state["username"] if state["username"] else "admin"
                        
                        print(f"[DEBUG] Session {session_id}: Active Username Context: '{username}'")
                        print(f"[DEBUG] Session {session_id}: Cleaned Password String: '{password}'")
                        
                        authenticated = False
                        if password == "eve_ng":
                            authenticated = True
                            print(f"[DEBUG] Session {session_id}: Password matched successfully!")
                        else:
                            print(f"[DEBUG] Session {session_id}: Password mismatch error.")
                        
                        status = 1 if authenticated else 2 # 1=PASS, 2=FAIL
                        server_body = struct.pack("!HHBB", 0, 0, status, 0)
                        client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))
                
                elif seq_no == 5: # Second CONTINUE packet (Password step when Username came in seq 3)
                    pass_len, flags, data_len = struct.unpack("!HHB", body[:5])
                    password = body[5:5+pass_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                    
                    state = session_state.get(session_id, {"username": "admin"})
                    username = state.get("username", "admin")
                    
                    print(f"[DEBUG] Session {session_id}: Active Username Context: '{username}'")
                    print(f"[DEBUG] Session {session_id}: Cleaned Password String: '{password}'")
                    
                    authenticated = False
                    if password == "eve_ng":
                        authenticated = True
                        print(f"[DEBUG] Session {session_id}: Password matched successfully!")
                    else:
                        print(f"[DEBUG] Session {session_id}: Password mismatch error.")
                    
                    status = 1 if authenticated else 2 
                    server_body = struct.pack("!HHBB", 0, 0, status, 0)
                    client_socket.sendall(make_packet(version, type_, seq_no + 1, session_id, server_body))

            # --- AUTHORIZATION (Type 2) ---
            elif type_ == 2: 
                authen_method, priv_lvl, authen_type, authen_service, user_len, port_len, rem_len, arg_cnt = struct.unpack("!BBBBBBBB", body[:8])
                username = body[8:8+user_len].decode('utf-8', errors='ignore').replace('\x00', '').strip()
                
                if not username:
                    state = session_state.get(session_id, {"username": "admin"})
                    username = state.get("username", "admin")
                
                offset = 8 + user_len + port_len + rem_len
                arg_lens = struct.unpack(f"!{arg_cnt}B", body[offset:offset+arg_cnt])
                offset += arg_cnt
                
                args = []
                for a_len in arg_lens:
                    args.append(body[offset:offset+a_len].decode('utf-8', errors='ignore'))
                    offset += a_len
                
                print(f"[DEBUG] Session {session_id}: Authorization request for user '{username}' with args: {args}")
                
                allowed = True
                user_priv = USERS.get(username, {}).get("priv-lvl", 15)
                
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
    print(f"[*] Cisco-Optimized TACACS+ Server listening on {LISTEN_IP}:{LISTEN_PORT}")
    
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

if name == "main":
    main()
