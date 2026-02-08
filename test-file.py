import webview
import xml.etree.ElementTree as ET
import os
import base64
from pathlib import Path

def get_image_base64(path):
    """Transforme une image en texte Base64 pour l'inclure dans le HTML"""
    try:
        with open(path, "rb") as img_file:
            ext = os.path.splitext(path)[1][1:] # récupère 'png' ou 'svg'
            prefix = f"data:image/{'svg+xml' if ext == 'svg' else ext};base64,"
            return prefix + base64.b64encode(img_file.read()).decode('utf-8')
    except:
        return "" # Retourne vide si l'image manque

def build_siv():
    base_path = Path(__file__).parent.absolute()
    
    # 1. ENCODAGE DES IMAGES EN TEXTE (BASE64)
    logo_data = get_image_base64(base_path / "assets" / "trans-node-nobg.png")
    gps_data = get_image_base64(base_path / "assets" / "fleche-gps.svg")
    
    # 2. LECTURE XML
    try:
        xml_path = base_path / "line" / "stops.xml"
        tree = ET.parse(xml_path)
        root = tree.getroot()
        num_ligne = root.find('.//numero_ligne').text
        dest = root.find('.//destination').text
        tous_les_noms = [idx.find('nom').text for idx in root.findall('.//index')]
        selection_arrets = tous_les_noms[:4]
    except Exception as e:
        return f"<html><body><h1>Erreur XML : {e}</h1></body></html>"

    # 3. GÉNÉRATION DES ARRÊTS
    arrets_html = ""
    for i, nom in enumerate(selection_arrets):
        if i == 0:
            arrets_html += '<div class="stop-container"><svg width="125" height="125"><circle cx="62.5" cy="62.5" r="50" fill="#007CC3" stroke="white" stroke-width="8" /></svg></div>'
        else:
            arrets_html += f'<div class="stop-container"><span class="stop-name" data-name="{nom}"></span><svg width="95" height="95"><circle cx="47.5" cy="47.5" r="38" fill="white" stroke="#00A651" stroke-width="8" /></svg></div>'

    # 4. INJECTION DANS LE TEMPLATE
    try:
        with open(base_path / 'siv_template.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Remplacements
        html = html.replace("{destination}", dest)
        html = html.replace("{num_ligne}", num_ligne)
        html = html.replace("{arrets_html}", arrets_html)
        html = html.replace("{prochain_arret}", selection_arrets[0] if selection_arrets else "Terminus")
        
        # Injection des images encodées
        html = html.replace("{logo_base64}", logo_data)
        html = html.replace("{gps_base64}", gps_data)
        
        return html
    except Exception as e:
        return f"<h1>Erreur Template : {e}</h1>"

# LANCEMENT
if __name__ == "__main__":
    window = webview.create_window('SIV TransNode', html=build_siv(), width=1280, height=720)
    webview.start()