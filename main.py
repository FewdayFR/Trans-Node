import pygame
import os
import sys
import subprocess
import threading
import time
import socket
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
XML_PATH = os.path.join(BASE_DIR, "line", "library-tts.xml")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")
VOICE_TEMP = os.path.join(BASE_DIR, "welcome_tmp.wav")

# --- VARIABLES DE SYNCHRO ---
info_retard = "À l'heure"
last_heartbeat_time = time.time()
is_broadcasting = False
app = Flask(__name__)

# --- SERVEUR FLASK & HEARTBEAT ---
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    global info_retard, last_heartbeat_time
    last_heartbeat_time = time.time() # On note que le téléphone est là
    
    retard_query = request.args.get('retard')
    if retard_query:
        info_retard = "À l'heure" if str(retard_query) == "0" else f"Retard : {retard_query} min"
    
    return jsonify({"reponse": "oui et toi ?", "status": info_retard}), 200

def run_flask():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- GESTION DU BROADCAST IP ---
def get_my_ip():
    """Récupère l'IP locale du Pi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def connection_manager():
    """Surveille la connexion et lance le broadcast si besoin."""
    global last_heartbeat_time, is_broadcasting
    
    # Socket pour le broadcast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        # Si pas de heartbeat depuis plus de 6 secondes
        if time.time() - last_heartbeat_time > 6:
            is_broadcasting = True
            my_ip = get_my_ip()
            message = f"SAEIV_IP:{my_ip}"
            try:
                sock.sendto(message.encode(), ('<broadcast>', 5001))
                print(f"📡 Connexion perdue. Broadcast IP ({my_ip}) sur port 5001...")
            except:
                pass
        else:
            if is_broadcasting:
                print("✅ Connexion rétablie avec le pupitre.")
                is_broadcasting = False
        
        time.sleep(2) # On vérifie/broadcast toutes les 2 secondes

# --- LOGIQUE TTS ---
def get_first_annonce():
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        first_index = root.find('index')
        if first_index is not None:
            return first_index.find('tts').text.strip()
    except Exception as e:
        print(f"Erreur XML : {e}")
    return "Bienvenue à bord."

def piper_worker(text):
    piper_path = os.path.join(BASE_DIR, "piper", "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    lib_path = os.path.join(BASE_DIR, "piper")
    command = (
        f'export LD_LIBRARY_PATH="{lib_path}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{VOICE_TEMP}" --threads 4'
    )
    subprocess.run(command, shell=True, check=True, capture_output=True)

# --- MAIN ---
def main():
    # Threads de fond
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=connection_manager, daemon=True).start()

    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    # Préparation voix
    text_to_say = get_first_annonce()
    gen_thread = threading.Thread(target=piper_worker, args=(text_to_say,))
    gen_thread.start()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # Assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width()*(h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))
    font_main = pygame.font.Font(FONT_PATH, int(sh * 0.08)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 60)
    font_status = pygame.font.Font(FONT_PATH, int(sh * 0.04)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 30)

    start_time = pygame.time.get_ticks()
    has_played = False
    running = True

    while running:
        now_ticks = pygame.time.get_ticks()
        elapsed = now_ticks - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

        screen.fill((255, 255, 255))

        # Animation cercle -> logo
        if elapsed < 3000:
            radius = int((elapsed / 3000) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (0, 0, 0), (sw // 2, sh // 2), radius) # Inversion pour effet stylé
        else:
            screen.blit(logo, logo_rect)
            txt = font_main.render("Bienvenue à bord", True, (40, 40, 40))
            screen.blit(txt, txt.get_rect(center=(sw // 2, logo_rect.bottom + 80)))
            
            # Affichage Statut Connexion / Retard
            if is_broadcasting:
                stat_txt = font_status.render("⚠️ ATTENTE PUPITRE...", True, (255, 0, 0))
            else:
                color = (200, 0, 0) if "Retard" in info_retard else (0, 150, 0)
                stat_txt = font_status.render(info_retard, True, color)
            
            screen.blit(stat_txt, (sw - stat_txt.get_width() - 20, sh - 50))

            if not has_played and elapsed > 6000:
                gen_thread.join()
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                    os.remove(VOICE_TEMP)
                has_played = True

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()