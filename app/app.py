from flask import Flask, render_template_string

app = Flask(__name__)

# La page HTML que ton téléphone affichera
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>TranNode Remote</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background: #f4f4f4; }
        button { 
            display: block; width: 100%; padding: 20px; margin: 10px 0; 
            font-size: 18px; cursor: pointer; border: none; border-radius: 10px;
            background: #2c3e50; color: white; 
        }
        .dest { background: #27ae60; }
    </style>
</head>
<body>
    <h1>TranNode Remote</h1>
    <p>Choisir la destination :</p>
    <a href="/set/Pau, Gare Multimodale"><button class="dest">Pau, Gare Multimodale</button></a>
    <a href="/set/Jurancon Lycee Andre Campa"><button class="dest">Jurançon Lycée André Campa</button></a>
    <br>
    <a href="/set/Bienvenue a bord"><button>Réinitialiser</button></a>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/set/<destination>')
def set_destination(destination):
    # On décode proprement pour éviter les erreurs de navigateur
    import urllib.parse
    dest_propre = urllib.parse.unquote(destination) 
    
    with open("current_dest.txt", "w", encoding="utf-8") as f:
        f.write(dest_propre)
    return f"Destination : {dest_propre} prise en compte."

if __name__ == "__main__":
    # On lance le serveur sur le port 5000, accessible par tout le réseau
    app.run(host='0.0.0.0', port=5000)