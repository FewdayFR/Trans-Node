import pygame
import os
import sys
import subprocess
import platform
import threading # Pour générer l'audio sans bloquer l'image

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")

def generate_voice_thread():
    """Fonction qui sera lancée en arrière-plan."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    text = "Bonjour et bienvenue à bord."
    
    if platform.system() == "Windows":
        piper_path = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        piper_path = os.path.join(piper_dir, "piper")
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
        )
    
    try:
        subprocess.run(command, shell=True, check=True)
        print("Voix générée en arrière-plan.")
    except:
        print("Erreur de génération voix.")

def main():
    # 1. Initialisation Audio avec gros Buffer
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # 2. LANCER LA GÉNÉRATION DE LA VOIX IMMÉDIATEMENT (Thread séparé)
    # Cela tourne pendant que l'animation commence
    voice_thread = threading.Thread(target=generate_voice_thread)
    voice_thread.start()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Chargement assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * (h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    # Chronologie
    circle_duration = 2000 
    fade_duration = 2000
    start_time = pygame.time.get_ticks()
    
    has_played = False
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        # ÉTAPE 1 : Le cercle s'agrandit (Piper travaille en secret ici)
        if elapsed < circle_duration:
            screen.fill((0, 0, 0))
            prog = elapsed / circle_duration
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        # ÉTAPE 2 : Fondu du logo
        elif elapsed < (circle_duration + fade_duration):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_duration) / fade_duration) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)

        # ÉTAPE 3 : Écran fixe et Lecture du son
        else:
            screen.fill((255, 255, 255))
            logo.set_alpha(255)
            screen.blit(logo, logo_rect)
            
            if not has_played:
                # On attend juste que le thread Piper ait fini au cas où le Pi est lent
                voice_thread.join() 
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                has_played = True

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()