#!/usr/bin/env python3
import socket
import secrets
import time
# ============================
# Schnorr parameters (toy)
# ============================
# Must match server: P, Q, G.
# The client additionally knows the secret a.
# Here: A = G**a mod P = 13 (as used on server).
# WARNING: tiny, insecure values.

P = 23
Q = 11
G = 2

A = 13      # public key (not actually needed here, but kept for clarity)
A_SECRET = 7  # private exponent a, known only on client


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
        end = time.time()
        print(f"execution time : {end-start} seconde")

def main():
    print(f"[+] Schnorr prover connecting to {SERVER_HOST}:{SERVER_PORT}")
    print(f"    Parameters: p={P}, q={Q}, g={G}, A={A}, a={A_SECRET}")
    schnorr_prove_once()


if __name__ == "__main__":
    main()
