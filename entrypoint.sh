#!/bin/bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
    -subj "/C=FR/ST=Internet/L=Server/O=CTF/CN=CTF_Challenge"

echo "Lancement du serveur sur le port 443..."
python app.py
