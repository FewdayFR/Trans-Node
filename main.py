import pygame
import os
import sys
import subprocess
import platform
import time

# Forcer le dossier de travail
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

LOGO_PATH = os.path.join("assets", "trans-node-nobg.png")
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")

def pre_generate_voice():
    """Génère le fichier audio AVANT de commencer l'animation pour éviter les lags."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    text = "Bonjour et bienvenue à bord."
    
    print("Pré-génération de la voix...")

    if platform.system() == "Windows":
        piper_path = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        piper_path = os.path.join(piper_dir, "piper")
        # On force le volume
        subprocess.run(["amixer", "sset", "Master", "100%"], capture_output=True)
        # Commande Linux avec export
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
        )

    if os.path.exists(piper_path) and os.path.exists(model_path):
        try:
            # On attend que Piper finisse AVANT de continuer
            subprocess.run(command, shell=True, check=True)
            print("Voix prête.")
            return True
        except Exception as e:
            print(f"Erreur génération voix : {e}")
    return False

def main():
    # 1. Initialiser le mixer en premier
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    # 2. GÉNÉRATION DE LA VOIX (Écran noir, avant l'animation)
    # On le fait avant de créer la fenêtre ou juste après pour ne pas bloquer l'animation
    voice_ready = pre_generate_voice()

    # 3. Configuration écran
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Chargement des images (pendant que la voix est prête)
    if not os.path.exists(LOGO_PATH): return
    logo_img = pygame.image.load(LOGO_PATH).convert_alpha()
    h_logo = int(sh * 0.5)
    ratio = h_logo / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.SysFont("Arial", int(sh * 0.07), bold=True)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # 4. Début de l'animation
    duration = 2000 
    start_time = pygame.time.get_ticks()
    has_played_audio = False

    running = True
    clock = pygame.time.Clock() # Pour stabiliser les FPS

    while running:
        clock.tick(60) # Limite à 60 FPS pour libérer du CPU
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed < duration:
            screen.fill((0, 0, 0))
            prog = elapsed / duration
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
        else:
            # ICI : On joue le son instantanément car le fichier est DÉJÀ là
            if not has_played_audio:
                if os.path.exists(VOICE_TEMP):
                    speech = pygame.mixer.Sound(VOICE_TEMP)
                    speech.play()
                has_played_audio = True

            screen.fill((255, 255, 255))
            alpha = int(min((elapsed - duration) / duration, 1) * 255)
            
            l_tmp = logo.copy()
            l_tmp.set_alpha(alpha)
            screen.blit(l_tmp, logo_rect)

            t_tmp = txt_surf.copy()
            t_tmp.set_alpha(alpha)
            screen.blit(t_tmp, txt_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()