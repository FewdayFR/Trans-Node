import pygame
import os
import sys
import subprocess
import threading
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")
VOICE_TEMP = os.path.join(BASE_DIR, "intro_tmp.wav")
NEXT_SCRIPT = os.path.join(BASE_DIR, "siv.py")

# --- LOGIQUE TTS (PIPER) ---
def piper_worker(text):
    piper_path = os.path.join(BASE_DIR, "piper", "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    lib_path = os.path.join(BASE_DIR, "piper")
    # Commande simplifiée (ajustez selon votre OS, ici format Linux/Pi)
    command = (
        f'export LD_LIBRARY_PATH="{lib_path}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{VOICE_TEMP}" --threads 4'
    )
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
    except:
        pass

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # Chargement Logo
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.4)
    logo_w = int(logo_img.get_width() * (h_logo / logo_img.get_height()))
    logo = pygame.transform.smoothscale(logo_img, (logo_w, h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2))

    # Lancement TTS en arrière plan
    threading.Thread(target=piper_worker, args=("Bonjour et bienvenue à bord.",)).start()

    clock = pygame.time.Clock()
    start_time = time.time()
    
    # Variables d'animation
    circle_radius = 0
    logo_alpha = 0
    audio_played = False
    phase = "CIRCLE" # CIRCLE -> LOGO -> WAIT -> END

    running = True
    while running:
        current_time = time.time()
        elapsed = current_time - start_time

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0)) # Fond noir de base

        if phase == "CIRCLE":
            # 1. Animation du cercle (Noir vers Blanc)
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), int(circle_radius))
            circle_radius += (sw * 0.05) # Vitesse d'ouverture
            if circle_radius > sw * 0.8: # Si le cercle couvre l'écran
                phase = "LOGO"
        
        elif phase == "LOGO":
            screen.fill((255, 255, 255))
            # 2. Fondu du logo
            logo.set_alpha(logo_alpha)
            screen.blit(logo, logo_rect)
            logo_alpha += 5
            if logo_alpha >= 255:
                logo_alpha = 255
                phase = "WAIT"
                wait_start = time.time()

        elif phase == "WAIT":
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            
            # Lecture audio dès que le fichier est prêt
            if not audio_played and os.path.exists(VOICE_TEMP):
                try:
                    pygame.mixer.Sound(VOICE_TEMP).play()
                    audio_played = True
                except: pass

            # Attendre 5 secondes après l'apparition du logo
            if current_time - wait_start > 5:
                running = False

        pygame.display.flip()
        clock.tick(60)

    # --- NETTOYAGE ET LANCEMENT DU SCRIPT SUIVANT ---
    pygame.quit()
    
    if os.path.exists(VOICE_TEMP):
        try: os.remove(VOICE_TEMP)
        except: pass

    # Lancement du script SIV.py
    print("Lancement du SIV...")
    subprocess.Popen([sys.executable, NEXT_SCRIPT])
    sys.exit()

if __name__ == "__main__":
    main()