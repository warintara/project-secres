# project-secres

Projet d'exemple démontrant deux variantes du protocole d'identification Schnorr :

- protocol1 : protocole interactif (challenge aléatoire envoyé par le vérifieur)
- protocol2 : version non-interactive (Fiat–Shamir transform) utilisant un hash pour calculer le challenge

Le code est volontairement simplifié et utilise des paramètres de groupe  très faibles (pour démonstration seulement) — NE PAS UTILISER EN PRODUCTION.

---

## Structure du dépôt

- `compose.yaml` : configuration de devcontainers (deux conteneurs: `server` et `client`) et réseau Docker.
- `src/protocol1/server.py` : vérifieur Schnorr interactif (écoute sur `0.0.0.0:5000` par défaut).
- `src/protocol1/client.py` : prouveur Schnorr interactif (se connecte à `server:5000` par défaut).
- `src/protocol2/server.py` : vérifieur Schnorr non-interactif (NIZKP) (écoute sur `0.0.0.0:5001` par défaut).
- `src/protocol2/client.py` : prouveur Schnorr non-interactif (NIZKP) (se connecte à `server:5001` par défaut).

---

## Prérequis

- Python 3.7+ (recommandé)
- (Optionnel) Docker & Docker Compose si vous voulez utiliser les conteneurs définis dans `compose.yaml`

---

## Exécution (mode local, simple)

Ces scripts se lancent directement avec Python, idéal pour tester rapidement sur la machine locale.

1) Ouvrez deux terminaux.

2) Dans le premier terminal, lancez le serveur :

```bash
python3 src/protocol1/server.py
# ou pour le second protocole
# python3 src/protocol2/server.py
```

3) Dans le deuxième terminal, éditez le client pour l'adapter à un test local (par défaut `SERVER_HOST = "server"` — qui fonctionne si vous utilisez Docker Compose). Pour tester en local (sans Docker), changez `SERVER_HOST` dans `src/protocol1/client.py` et `src/protocol2/client.py` en :

```python
SERVER_HOST = "localhost"
```

4) Lancez le client :

```bash
python3 src/protocol1/client.py
# ou pour le second protocole
# python3 src/protocol2/client.py
```

Vous verrez dans la sortie console les échanges et le résultat (`OK`/`FAIL`).

---

## Exécution via Docker Compose

Le fichier `compose.yaml` fournit deux conteneurs légers (basés sur l'image `mcr.microsoft.com/devcontainers/base:noble`) et monte le code source dans `/workspace`. Les conteneurs ne lancent pas automatiquement le serveur/client — ils sont utiles pour reproduire un environnement isolé et pour que l'hôte `server` soit résolu automatiquement par Docker.

1) Démarrez les conteneurs (en détaché) :

```bash
docker compose up -d
```

2) Lancez le serveur dans le conteneur `server` :

```bash
docker compose exec server bash
# depuis l'intérieur du conteneur
python3 src/protocol1/server.py
# ou
python3 src/protocol2/server.py
```

3) Dans un autre terminal, lancez le client depuis le conteneur `client` :

```bash
docker compose exec client bash
# depuis l'intérieur du conteneur
python3 src/protocol1/client.py
# ou
python3 src/protocol2/client.py
```

Le client utilise par défaut `SERVER_HOST = "server"`, ce qui résout correctement via le réseau par défaut de Docker Compose.

---

## Par défaut : paramètres et ports

- protocol1 : 0.0.0.0:5000
- protocol2 : 0.0.0.0:5001

Les paramètres algorithmiques (p, q, g, A, a) sont définis en clair dans les fichiers pour la démo. **Ce sont de très petites valeurs non-sécurisées**, uniquement pour l'enseignement.

---

## Comportement attendu / Exemples

- protocol1 (interactif) :
  - Client choisit `v`, envoie `V = g^v mod p`.
  - Serveur renvoie `c` (challenge aléatoire).
  - Client renvoie `r = v - a*c (mod q)`.
  - Serveur vérifie `V ?= g^r * A^c (mod p)` puis renvoie `OK` ou `FAIL`.

- protocol2 (NIZKP, Fiat–Shamir) :
  - Client choisit `v` et calcule `V`.
  - Client calcule `c = H(g||V||A||user_id||other_info) mod q`.
  - Client calcule `r = v - a*c (mod q)`, envoie `(user_id, other_info, c, r)` au serveur.
  - Serveur reconstruit `V` et recalcule le `c'` à l'aide du hash ; si `c == c'` la preuve est valide.

La sortie console vous montrera les valeurs échangées et le résultat `OK`/`FAIL`.

---

## Conseils / améliorations possibles

- Ajouter des arguments en ligne de commande pour `SERVER_HOST`, `PORT`, `A`/`a` et autres paramètres.
- Charger les paramètres à partir d'un fichier JSON/YAML plutôt que de valeurs codées en dur.
- Ajouter TLS pour la communication socket (sockets sécurisés) pour éviter l'exposition en clair.
- Remplacer les paramètres du groupe par des paramètres sécurisés (utiliser une bibliothèque crypto appropriée).

---

## Dépannage rapide

- Si le client affiche `Connection refused`:
  - Vérifiez que le serveur tourne et est accessible sur le port attendu.
  - Si vous utilisez Docker Compose, exécutez le client depuis le conteneur `client` (le nom de l'hôte `server` y est résolu). Pour test local, changez `SERVER_HOST` en `localhost`.

- Si la vérification renvoie `FAIL`:
  - Assurez-vous que les paramètres p/q/g/A et la valeur secrète du client a sont cohérents entre client et serveur.
  - Dans protocol2, vérifiez également la valeur `other_info` et `user_id` qui doivent correspondre à l'entrée `USER_DB` du serveur.

