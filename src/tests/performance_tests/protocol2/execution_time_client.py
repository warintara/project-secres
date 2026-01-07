#!/usr/bin/env python3
import socket
import secrets
import hashlib
import time
import logging

logging.basicConfig(filename='../log/nizkp_client_perf.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# ============================
# Schnorr parameters (toy)
# ============================
P = int("""
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B
80DC1CD1 29024E08 8A67CC74 020BBEA6
3B139B22 514A0879 8E3404DD EF9519B3
CD3A431B 302B0A6D F25F1437 4FE1356D
6D51C245 E485B576 625E7EC6 F44C42E9
A63A3620 FFFFFFFF FFFFFFFF
""".replace(" ", "").replace("\n", ""), 16)
Q = (P - 1) // 2
G = 2

# Prover secret (a) and public key A = g^a mod p
A_SECRET = 7
A = pow(G, A_SECRET, P)  # should be 13 with these parameters

USER_ID = "user1"
OTHER_INFO = "demo-info"  # must match server's stored value

# ============================
# Network config
# ============================
SERVER_HOST = "server"
SERVER_PORT = 5001


def compute_challenge(g, V, A, user_id, other_info):
    """
    Compute c = H(g || V || A || user_id || other_info) mod Q
    using SHA-256.
    """
    data = f"{g}|{V}|{A}|{user_id}|{other_info}".encode("utf-8")
    digest = hashlib.sha256(data).digest()
    c = int.from_bytes(digest, "big") % Q
    return c


def schnorr_nizkp_prove_once():
    """
    Non-interactive Schnorr proof:

      1) Choose v in [0, q-1]
      2) Compute V = g^v mod p
      3) Compute c = H(g, V, A, UserID, OtherInfo) mod q
      4) Compute r = v - a*c (mod q)
      5) Send (UserID, OtherInfo, c, r) to server.
    """
    start = time.time()
    # 1) Choose v
    v = secrets.randbelow(Q)
    # 2) Compute V
    V = pow(G, v, P)
    print(f"[+] v = {v}, V = {V}")

    # 3) Compute challenge c via Fiat–Shamir
    c = compute_challenge(G, V, A, USER_ID, OTHER_INFO)
    print(f"[+] Computed c = {c}")

    # 4) Compute response r
    r = (v - A_SECRET * c) % Q
    end = time.time()
    duration = end - start
    logging.info(f"Execution time: {duration:.6f}s | V={V} | User: {USER_ID}")
    print(f"[+] Computed r = {r}")

    # 5) Send (UserID, OtherInfo, c, r) to server
    with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
        f = sock.makefile("rwb", buffering=0)

        print(f"[<] Sending user_id = {USER_ID}")
        f.write(f"{USER_ID}\n".encode("utf-8"))

        print(f"[<] Sending other_info = {OTHER_INFO}")
        f.write(f"{OTHER_INFO}\n".encode("utf-8"))

        print(f"[<] Sending c = {c}")
        f.write(f"{c}\n".encode("ascii"))

        print(f"[<] Sending r = {r}")
        f.write(f"{r}\n".encode("ascii"))

        # Read verification result
        line = f.readline()
        if not line:
            raise RuntimeError("No result received from server")
        result = line.strip().decode("ascii")
        
        print(f"[>] Server result: {result}")
        
        print(f"execution time : {end-start} seconde")


def main():
    print(f"[+] Schnorr NIZKP prover connecting to {SERVER_HOST}:{SERVER_PORT}")
    print(f"    Parameters: p={P}, q={Q}, g={G}, A={A}, a={A_SECRET}")
    schnorr_nizkp_prove_once()


if __name__ == "__main__":
    main()
