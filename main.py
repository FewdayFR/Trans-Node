import pygame
import os
import sys
import subprocess
import threading
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "intro_tmp.wav")
NEXT_SCRIPT = os.path.join(BASE_DIR, "siv.py")

def piper_worker(text):
    """Génère le fichier audio avec Piper sur Linux"""
    # On utilise 'piper' tout court sur Linux, pas 'piper.exe'
    piper_path = os.path.join(BASE_DIR, "piper", "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    lib_path = os.path.join(BASE_DIR, "piper")
    
    # Commande Linux avec LD_LIBRARY_PATH pour charger les dépendances de Piper
    command = (
        f'export LD_LIBRARY_PATH="{lib_path}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    )
    try:
        # On exécute la commande
        subprocess.run(command, shell=True, check=True, executable='/bin/bash')
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
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    if os.path.exists(logo_path):
        logo_img = pygame.image.load(logo_path).convert_alpha()
        h_logo = int(sh * 0.4)
        logo_w = int(logo_img.get_width() * (h_logo / logo_img.get_height()))
        logo = pygame.transform.smoothscale(logo_img, (logo_w, h_logo))
        logo_rect = logo.get_rect(center=(sw // 2, sh // 2))
    else:
        print("Logo introuvable !")
        logo = None

    # Lancement de la génération audio
    threading.Thread(target=piper_worker, args=("Bonjour et bienvenue à bord.",)).start()

    clock = pygame.time.Clock()
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

        # 1. Animation Iris
        if circle_radius < sw * 1.2:
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), int(circle_radius))
            circle_radius += (sw * 0.04)
        else:
            screen.fill((255, 255, 255))
            
            # 2. Fondu du logo
            if logo and logo_alpha < 255:
                logo_alpha += 5
                logo.set_alpha(logo_alpha)
                screen.blit(logo, logo_rect)
            elif logo:
                screen.blit(logo, logo_rect)

            # 3. Surveillance de la fin du son
            if os.path.exists(VOICE_TEMP) and not audio_started:
                try:
                    pygame.mixer.Sound(VOICE_TEMP).play()
                    audio_started = True
                except:
                    pass
            
            # On quitte quand le son est fini et le logo bien visible
            if audio_started and not pygame.mixer.get_busy() and logo_alpha >= 255:
                time.sleep(1) # Petite pause de confort
                running = False

        pygame.display.flip()
        clock.tick(60)

    # --- TRANSITION ---
    pygame.quit()
    
    if os.path.exists(VOICE_TEMP):
        try: os.remove(VOICE_TEMP)
        except: pass

    # Lancement du SIV
    subprocess.Popen([sys.executable, NEXT_SCRIPT])
    sys.exit()

if __name__ == "__main__":
    main()