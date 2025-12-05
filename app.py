from flask import Flask, request, make_response, render_template_string, redirect
import ssl
import jwt
import datetime
import sys

app = Flask(__name__)

# La clé secrète utilisée pour signer les vrais tokens.
# Le hacker ne la connait pas, donc il ne peut pas générer de signature "HS256" valide.
SECRET_KEY = "StefanoLePlusBeau"

# Le nom du cookie (plus propre que 'token')
COOKIE_NAME = "auth_token"

# Interface HTML (Style "Terminal / Hacker")
HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Exagon Secure Corp - Admin Panel</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; margin-top: 50px; }
        .container { border: 1px solid #30363d; padding: 40px; background-color: #161b22; border-radius: 6px; box-shadow: 0 0 20px rgba(0,0,0,0.5); text-align: center; max-width: 600px; }
        h1 { color: #58a6ff; }
        .status { padding: 10px; margin: 20px 0; border-radius: 5px; font-weight: bold; }
        .status-guest { background-color: #8b949e; color: #0d1117; }
        .status-admin { background-color: #2ea043; color: white; border: 2px solid #3fb950; animation: blink 1s infinite alternate; }
        .status-error { background-color: #da3633; color: white; }
        .flag-box { margin-top: 20px; padding: 20px; border: 2px dashed #f0883e; color: #f0883e; font-size: 1.2em; }
        input { background: #0d1117; border: 1px solid #30363d; color: white; padding: 10px; border-radius: 4px; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background: #2ea043; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        @keyframes blink { from { box-shadow: 0 0 10px #2ea043; } to { box-shadow: 0 0 20px #2ea043; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Exagon Secure System v2.0</h1>
        <p>Authentification ExaAuth</p>

        <hr style="border-color: #30363d; margin: 20px 0;">

        {% if user %}
            <!-- ZONE CONNECTÉE -->
            <div class="status {% if role == 'admin' %}status-admin{% else %}status-guest{% endif %}">
                IDENTIFIÉ EN TANT QUE : {{ user.upper() }}<br>
                RÔLE ACTUEL : {{ role.upper() }}
            </div>

            {% if role == 'admin' %}
                <div class="flag-box">
                    ACCÈS ADMIN AUTORISÉ<br><br>
                    FLAG: <b>CTF{JWT_N0N3_4LG0_1S_D4NG3R0US}</b>
                </div>
                <p>Bien joué, le système a accepté un token non signé (Alg: None).</p>
            {% else %}
                <div class="status-error">
                    ACCÈS RESTREINT<br>
                    Le flag est réservé au rôle 'admin'.
                </div>
            {% endif %}

            <br>
            <a href="/logout">Se déconnecter</a>

        {% else %}
            <!-- ZONE DE LOGIN -->
            <p>Veuillez vous identifier pour accéder au portail.</p>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Nom d'utilisateur" value="guest" required>
                <button type="submit">Connexion</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

def verify_token_vulnerable(token):
    """
    Vérifie la validité du token JWT.
    C'est ICI que se trouve la faille de sécurité.
    """
    try:

        # On regarde d'abord l'entête pour savoir quel algo est utilisé.
        unverified_header = jwt.get_unverified_header(token)
        algo = unverified_header.get('alg', '').lower()

        # Si le header dit que l'algo est 'none', le code ci-dessous accepte le token SANS vérifier la signature !
        # C'est une erreur classique de développeur qui implémente JWT manuellement.
        if algo == 'none':
            print(f"\n[!!!] ALERTE SÉCURITÉ : Un token 'NONE' a été détecté et accepté !", file=sys.stderr)
            # options={"verify_signature": False} demande à la librairie de ne PAS vérifier la signature
            decoded_payload = jwt.decode(token, options={"verify_signature": False})
            return decoded_payload

        # Si l'algo n'est pas 'none', on vérifie la signature avec la SECRET_KEY.
        # Si le hacker modifie le token sans mettre 'alg: none', ça échouera ici.
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    except jwt.ExpiredSignatureError:
        print("[-] Token expiré", file=sys.stderr)
        return None
    except jwt.InvalidTokenError as e:
        print(f"[-] Token invalide : {e}", file=sys.stderr)
        return None

@app.route('/')
def home():
    token = request.cookies.get(COOKIE_NAME)
    user_data = None
    
    if token:
        user_data = verify_token_vulnerable(token)
    
    # On passe les infos au HTML pour l'affichage
    if user_data:
        return render_template_string(HTML, user=user_data.get('user'), role=user_data.get('role'))
    else:
        return render_template_string(HTML, user=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', 'guest')
    
    # Création du payload (les données du token)
    # Par défaut, on force le rôle à 'user'. Le but est de le changer en 'admin'.
    payload = {
        "user": username,
        "role": "user",  # <--- C'est ça qu'il faut modifier !
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }
    
    # Signature légitime du serveur (HS256)
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    resp = make_response(redirect('/'))
    resp.set_cookie(COOKIE_NAME, token)
    return resp

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie(COOKIE_NAME, '', expires=0)
    return resp


if __name__ == "__main__":
    # Configuration SSL (HTTPS)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    print("[+] Serveur Secure démarré sur le port 443 (HTTPS)")
    # 0.0.0.0 permet l'accès depuis l'extérieur du conteneur (IP publique)
    app.run(host='0.0.0.0', port=443, ssl_context=context)
