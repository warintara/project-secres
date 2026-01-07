#!/usr/bin/env python3
import socket
import secrets
import time
import logging

# Configuration du logging pour le client
logging.basicConfig(filename='../log/zkp_client_perf.log', level=logging.INFO,format='%(asctime)s - %(message)s')
# ============================
# Schnorr parameters (toy)
# ============================
# Must match server: P, Q, G.
# The client additionally knows the secret a.
# Here: A = G**a mod P = 13 (as used on server).
# WARNING: tiny, insecure values.
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

A_SECRET = 7 # public key (not actually needed here, but kept for clarity)
A = pow(G, A_SECRET, P) # private exponent a, known only on client

# ============================
# Network config
# ============================
SERVER_HOST = "server"  # change to server IP if needed
SERVER_PORT = 5000         # must match server PORT





def schnorr_prove_once():
    """
    Run a single Schnorr identification round with the verifier.
    Protocol (one round):
      1) Choose random v, compute V = g^v (mod p), send V.
      2) Receive challenge c.
      3) Compute r = v - a*c (mod q), send r.
      4) Receive verification result.
    """
    start = time.time()
    # 1) Choose v and compute V
    v = secrets.randbelow(Q)  # v in [0, Q-1]
    V = pow(G, v, P)
    print(f"[+] Using v = {v}, V = {V}")

    with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
        f = sock.makefile("rwb", buffering=0)

        # Send V
        print(f"[<] Sending V = {V}")
        f.write(f"{V}\n".encode("ascii"))

        # Receive challenge c
        line = f.readline()
        if not line:
            raise RuntimeError("No challenge received from server")
        c_str = line.strip().decode("ascii")
        c = int(c_str)
        print(f"[>] Received challenge c = {c}")

        # Compute response r = v - a*c (mod q)
        r = (v - A_SECRET * c) % Q
        end = time.time()
        print(f"[+] Computed r = {r}")

        # Send r
        print(f"[<] Sending r = {r}")
        f.write(f"{r}\n".encode("ascii"))

        # Read result
        line = f.readline()
        if not line:
            raise RuntimeError("No result received from server")
        result = line.strip().decode("ascii")
        print(f"[>] Server result: {result}")
        # Écriture dans le fichier log
        logging.info(f"Execution time: {end-start:.6f} seconds | V={V}")
        print(f"execution time : {end-start:.6f} seconde")

def main():
    print(f"[+] Schnorr prover connecting to {SERVER_HOST}:{SERVER_PORT}")
    print(f"    Parameters: p={P}, q={Q}, g={G}, A={A}, a={A_SECRET}")
    schnorr_prove_once()


if __name__ == "__main__":
    main()
