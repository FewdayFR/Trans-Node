from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] ❤️ Reçu du téléphone : Est-tu là ?")
    return jsonify({
        "reponse": "oui et toi ?",
        "heure_pi": now,
        "status": "OK"
    }), 200

if __name__ == '__main__':
    # On écoute sur 0.0.0.0 pour accepter les connexions venant de l'USB
    print("Démarrage du serveur SAEIV de test...")
    app.run(host='0.0.0.0', port=5000)