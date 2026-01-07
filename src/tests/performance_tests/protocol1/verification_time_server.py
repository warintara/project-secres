#!/usr/bin/env python3
import socket
import secrets
import time
import logging

# Configuration du logging pour le serveur
logging.basicConfig(filename='../log/zkp_server_perf.log', level=logging.INFO,format='%(asctime)s - %(message)s')
# ============================
# Schnorr parameters (toy)
# ============================
# Group: Z_p* with subgroup of order q, generator g
# p, q, g must be the same on client and server.
# A is the public key of the prover (client).
# WARNING: these are tiny, insecure values, for demo only.


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
A = 128       # public key = G**a mod P, with a secret on client side

# ============================
# Network config
# ============================
HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000        # change if you want



def handle_client(conn, addr):
    """
    Handle a single Schnorr identification session with one client.
    Protocol (one round):
      1) Receive V from client.
      2) Choose random challenge c.
      3) Send c to client.
      4) Receive r.
      5) Verify V == g^r * A^c (mod p).
    """
    print(f"[+] Connection from {addr}")

    # Use file-like wrapper to read/write lines easily
    f = conn.makefile("rwb", buffering=0)

    try:
        # 1) Receive V
        line = f.readline()
        if not line:
            print("[-] No data received (V)")
            return
        V_str = line.strip().decode("ascii")
        V = int(V_str)
        print(f"[>] Received V = {V}")

        # 2) Choose challenge c (in [0, Q-1])

        c = secrets.randbelow(Q)
        print(f"[<] Sending challenge c = {c}")
        f.write(f"{c}\n".encode("ascii"))

        # 3) Receive r
        line = f.readline()
        if not line:
            print("[-] No data received (r)")
            return
        r_str = line.strip().decode("ascii")
        r = int(r_str)
        print(f"[>] Received r = {r}")

        # 4) Verify: V ?= g^r * A^c (mod p)
        start= time.time()
        left = V % P
        right = (pow(G, r, P) * pow(A, c, P)) % P
        ok = (left == right)
        end= time.time()
        print(f"[=] Check: left={left}, right={right}, ok={ok}")
        # Écriture dans le fichier log avec l'IP du client
        logging.info(f"Client {addr} | Result: {'OK' if ok else 'FAIL'} | Time: {end-start:.6f} seconde")

        # 5) Send result to client
        result = "OK" if ok else "FAIL"
        f.write(f"{result}\n".encode("ascii"))
        print(f"[<] Sent result: {result}")

        print(f"verification time : {end-start:.6f} seconde")

    except Exception as e:
        print(f"[!] Error while handling client {addr}: {e}")
    finally:
        f.close()
        conn.close()
        print(f"[x] Connection closed for {addr}")


def main():
    print(f"[+] Schnorr verifier listening on {HOST}:{PORT}")
    print(f"    Parameters: p={P}, q={Q}, g={G}, A={A}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    main()
