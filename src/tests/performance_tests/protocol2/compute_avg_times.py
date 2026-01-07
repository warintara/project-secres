import re

client_log = "../log/nizkp_client_perf.log"
server_log = "../log/nizkp_server_perf.log"

client_times = []
server_times = []

# Regex EXACTES pour ton format protocole 2
client_pattern = re.compile(r"Execution time:\s*([0-9.]+)s")
server_pattern = re.compile(r"Time:\s*([0-9.]+)\s*seconde")

# Lecture log client (protocole 2)
with open(client_log, "r") as f:
    for line in f:
        match = client_pattern.search(line)
        if match:
            client_times.append(float(match.group(1)))

# Lecture log serveur (protocole 2)
with open(server_log, "r") as f:
    for line in f:
        match = server_pattern.search(line)
        if match:
            server_times.append(float(match.group(1)))

print("===== PROTOCOLE 2 – RÉSULTATS =====")

if client_times:
    avg_client = sum(client_times) / len(client_times)
    print(f"Execution time client moyen : {avg_client:.6f} s ({len(client_times)} mesures)")
else:
    print("Aucune donnée client trouvée")

if server_times:
    avg_server = sum(server_times) / len(server_times)
    print(f"Verification time server moyen : {avg_server:.6f} s ({len(server_times)} mesures)")
else:
    print("Aucune donnée serveur trouvée")
