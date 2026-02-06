import pygame
import os
import sys
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
XML_PATH = os.path.join(BASE_DIR, "line", "library-tts.xml")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")
VOICE_TEMP = os.path.join(BASE_DIR, "welcome_tmp.wav")

# --- VARIABLES GLOBALES (SYNCHRO) ---
info_retard = "À l'heure"
app = Flask(__name__)

# --- SERVEUR FLASK (COMMUNICATION APP INVENTOR) ---
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    global info_retard
    # Récupération du retard envoyé par l'app : ?retard=+2
    retard_query = request.args.get('retard')
    if retard_query:
        if str(retard_query) == "0":
            info_retard = "À l'heure"
        else:
            info_retard = f"Retard : {retard_query} min"
    
    return jsonify({
        "reponse": "oui et toi ?",
        "status_bus": info_retard
    }), 200

def run_flask():
    # Bloque les logs inutiles dans la console pour plus de clarté
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    # Écoute sur l'IP statique (USB0)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- FONCTIONS LOGIQUE (TTS / XML) ---
def get_first_annonce():
    """Lit l'index 1 du XML pour le message de bienvenue."""
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        first_index = root.find('index')
        if first_index is not None:
            return first_index.find('tts').text.strip()
    except Exception as e:
        print(f"Erreur lecture XML : {e}")
    return "Bienvenue à bord."

def piper_worker(text):
    """Génère la voix Piper sans bloquer l'affichage."""
    piper_path = os.path.join(BASE_DIR, "piper", "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    lib_path = os.path.join(BASE_DIR, "piper")
    
    command = (
        f'export LD_LIBRARY_PATH="{lib_path}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{VOICE_TEMP}" --threads 4'
    )
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
    except Exception as e:
        print(f"Erreur Piper : {e}")

# --- BOUCLE PRINCIPALE PYGAME ---
def main():
    global info_retard

    # 1. Démarrage du serveur Flask pour le pupitre (Thread séparé)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Initialisation Audio & Vidéo
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    # 3. Préparation TTS
    text_to_say = get_first_annonce()
    gen_thread = threading.Thread(target=piper_worker, args=(text_to_say,))
    gen_thread.start()

    # 4. Paramètres Écran
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # 5. Chargement Assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo_w = int(logo_img.get_width() * (h_logo / logo_img.get_height()))
    logo = pygame.transform.smoothscale(logo_img, (logo_w, h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))
    
    font_main = pygame.font.Font(FONT_PATH, int(sh * 0.08)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 60)
    font_status = pygame.font.Font(FONT_PATH, int(sh * 0.04)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 30)

    # 6. Variables Animation
    start_time = pygame.time.get_ticks()
    circle_dur = 3000
    fade_dur = 3000
    clock = pygame.time.Clock()
    has_played = False
    running = True

    while running:
        clock.tick(30) # Limite à 30 FPS pour soulager le Pi 3 B+
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- DESSIN ---
        if elapsed < circle_dur:
            # Animation 1 : Cercle blanc qui grandit
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
        
        elif elapsed < (circle_dur + fade_dur):
            # Animation 2 : Fondu enchaîné logo + texte
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            
            t_surf = font_main.render("Bienvenue à bord", True, (40, 40, 40))
            t_surf.set_alpha(alpha)
            screen.blit(t_surf, t_surf.get_rect(center=(sw // 2, logo_rect.bottom + 80)))
        
        else:
            # État Final Fixe
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            
            # Texte Bienvenue
            txt_surf = font_main.render("Bienvenue à bord", True, (40, 40, 40))
            screen.blit(txt_surf, txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 80)))
            
            # Affichage du Retard (Mis à jour par Flask/App via USB)
            color_retard = (220, 0, 0) if "Retard" in info_retard else (0, 120, 0)
            retard_surf = font_status.render(info_retard, True, color_retard)
            screen.blit(retard_surf, (sw - retard_surf.get_width() - 30, sh - 60))
            
            # Lancement de la voix une fois Piper prêt et animation finie
            if not has_played:
                gen_thread.join() # On s'assure que le son est généré
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                    os.remove(VOICE_TEMP)
                has_played = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()