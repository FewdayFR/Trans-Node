import pygame
import os
import sys
import subprocess
import platform
import threading

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")

def generate_voice_thread():
    """Génère l'audio en arrière-plan pendant l'animation."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    text = "Trans node, service d'informations voyageurs.Bonjour et bienvenue à bord."
    
    if platform.system() == "Windows":
        piper_path = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        piper_path = os.path.join(piper_dir, "piper")
        # On s'assure que le volume est à 100%
        subprocess.run(["amixer", "sset", "Master", "100%"], capture_output=True)
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
        )
    
    try:
        subprocess.run(command, shell=True, check=True)
    except:
        pass

def main():
    # 1. Initialisation Audio (Buffer large pour éviter les sauts)
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # 2. Lancer la voix en parallèle
    voice_thread = threading.Thread(target=generate_voice_thread)
    voice_thread.start()

    # 3. Écran et curseur
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # 4. Chargement Logo
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    if not os.path.exists(logo_path): return
    logo_img = pygame.image.load(logo_path).convert_alpha()
    h_logo = int(sh * 0.5)
    ratio = h_logo / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    # 5. Chargement Texte (Le revoilà !)
    font = pygame.font.SysFont("Arial", int(sh * 0.07), bold=True)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # Chronologie
    circle_dur = 2000 
    fade_dur = 2000
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

        # Étape 1 : Le cercle (C'est ici que Piper travaille en tâche de fond)
        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            prog = elapsed / circle_dur
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        # Étape 2 : Fondu enchaîné (Logo + Texte)
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            
            # Application de l'alpha au logo
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            
            # Application de l'alpha au texte
            txt_temp = txt_surf.copy()
            txt_temp.set_alpha(alpha)
            screen.blit(txt_temp, txt_rect)

        # Étape 3 : Fixe + Audio
        else:
            screen.fill((255, 255, 255))
            logo.set_alpha(255)
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            if not has_played:
                # On attend que Piper ait fini avant de lancer le son
                voice_thread.join() 
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                has_played = True

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()