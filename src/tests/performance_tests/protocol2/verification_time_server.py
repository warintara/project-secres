#!/usr/bin/env python3
import socket
import hashlib
import time
import logging

logging.basicConfig(filename='../log/nizkp_server_perf.log', level=logging.INFO, format='%(asctime)s - %(message)s')
# ============================
# Schnorr parameters (toy)
# ============================
# Group parameters (must match client)
P = int("""
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B
80DC1CD1 29024E08 8A67CC74 020BBEA6
3B139B22 514A0879 8E3404DD EF9519B3
CD3A431B 302B0A6D F25F1437 4FE1356D
6D51C245 E485B576 625E7EC6 F44C42E9
A63A3620 FFFFFFFF FFFFFFFF
""".replace(" ", "").replace("\n", ""), 16)

G = 2
# CORRECT : Q doit être l'ordre du sous-groupe pour P
Q = (P - 1) // 2

# Public keys by user id (here, single user)
# A = g^a mod p, with a secret known only to the client.
USER_DB = {
    "user1": {
        "A": 128,           # public key
        "other_info": "demo-info",  # expected OtherInfo (can be any string)
    }
}

# ============================
# Network config
# ============================
HOST = "0.0.0.0"
PORT = 5001  # different from previous demo if you want both running


def compute_challenge(g, V, A, user_id, other_info):
    """
    Compute c = H(g || V || A || user_id || other_info) mod Q
    using SHA-256 as the hash function.
    """
    data = f"{g}|{V}|{A}|{user_id}|{other_info}".encode("utf-8")
    digest = hashlib.sha256(data).digest()
    c = int.from_bytes(digest, "big") % Q
    return c


def handle_client(conn, addr):
    """
    Handle a single non-interactive Schnorr proof.

    Client sends (each as one line):
      1) user_id (string)
      2) other_info (string)
      3) c (int, decimal)
      4) r (int, decimal)

    Server:
      - looks up A from user_id
      - computes V = g^r * A^c mod p
      - recomputes c' = H(g, V, A, user_id, other_info) mod q
      - checks c == c'
    """
    print(f"[+] Connection from {addr}")
    f = conn.makefile("rwb", buffering=0)

    try:
        
        # 1) Read user_id
        line = f.readline()
        if not line:
            print("[-] No user_id received")
            return
        user_id = line.strip().decode("utf-8")
        print(f"[>] user_id = {user_id}")

        # 2) Read other_info
        line = f.readline()
        if not line:
            print("[-] No other_info received")
            return
        other_info = line.strip().decode("utf-8")
        print(f"[>] other_info = {other_info}")

        # 3) Read c
        line = f.readline()
        if not line:
            print("[-] No c received")
            return
        c_str = line.strip().decode("ascii")
        c = int(c_str)
        print(f"[>] c (claimed) = {c}")

        # 4) Read r
        line = f.readline()
        if not line:
            print("[-] No r received")
            return
        r_str = line.strip().decode("ascii")
        r = int(r_str)
        print(f"[>] r = {r}")

        # Lookup user
        if user_id not in USER_DB:
            print("[-] Unknown user_id")
            f.write(b"FAIL\n")
            return

        user_entry = USER_DB[user_id]
        A = user_entry["A"]
        expected_other_info = user_entry["other_info"]

        if other_info != expected_other_info:
            print("[-] other_info mismatch")
            f.write(b"FAIL\n")
            return

        # Reconstruct V from r and c
        start = time.time()
        V = (pow(G, r, P) * pow(A, c, P)) % P
        print(f"[=] Reconstructed V = {V}")

        # Recompute challenge
        c_check = compute_challenge(G, V, A, user_id, other_info)
        print(f"[=] Recomputed c' = {c_check}")

        ok = (c == c_check)
        end = time.time()
        # Écriture dans le fichier log avec l'IP du client
        logging.info(f"Client {addr} | Result: {'OK' if ok else 'FAIL'} | Time: {end-start:.6f} seconde")

        print(f"[=] Verification result: {ok}")
        
        result = "OK" if ok else "FAIL"
        f.write(f"{result}\n".encode("ascii"))
        print(f"[<] Sent result: {result}")

        print(f"execution time : {end-start} seconde")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        f.close()
        conn.close()
        print(f"[x] Connection closed for {addr}")


def main():
    print(f"[+] Schnorr NIZKP verifier listening on {HOST}:{PORT}")
    print(f"    Parameters: p={P}, q={Q}, g={G}")
    print(f"    Users: {list(USER_DB.keys())}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    main()
