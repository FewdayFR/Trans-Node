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

def piper_worker(text):
    """Génère le fichier audio avec Piper"""
    piper_path = os.path.join(BASE_DIR, "piper", "piper.exe") # .exe pour Windows
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    # Commande adaptée pour Windows (sans export LD_LIBRARY_PATH)
    command = f'echo {text} | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"Erreur Piper: {e}")

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

    # Génération du message audio
    threading.Thread(target=piper_worker, args=("Bonjour et bienvenue à bord.",)).start()

    clock = pygame.time.Clock()
    start_time = time.time()
    
    circle_radius = 0
    logo_alpha = 0
    audio_started = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0)) 

        # 1. Animation Iris (Cercle blanc qui s'étend)
        if circle_radius < sw * 1.2:
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), int(circle_radius))
            circle_radius += (sw * 0.04)
        else:
            screen.fill((255, 255, 255))
            
            # 2. Apparition en fondu du logo
            if logo_alpha < 255:
                logo_alpha += 5
                logo.set_alpha(logo_alpha)
            
            screen.blit(logo, logo_rect)

            # 3. Gestion de l'audio et de la sortie
            if os.path.exists(VOICE_TEMP) and not audio_started:
                sound = pygame.mixer.Sound(VOICE_TEMP)
                sound.play()
                audio_started = True
            
            # CONDITION DE SORTIE : Audio fini ET logo totalement affiché
            if audio_started and not pygame.mixer.get_busy() and logo_alpha >= 255:
                # On attend 1 seconde de silence pour ne pas couper brutalement
                time.sleep(1)
                running = False

        pygame.display.flip()
        clock.tick(60)

    # --- RELAIS VERS LE SCRIPT SIV ---
    pygame.quit()
    
    if os.path.exists(VOICE_TEMP):
        try: os.remove(VOICE_TEMP)
        except: pass

    # Lancement du second script et arrêt immédiat de celui-ci
    subprocess.Popen([sys.executable, NEXT_SCRIPT])
    sys.exit()

if __name__ == "__main__":
    main()