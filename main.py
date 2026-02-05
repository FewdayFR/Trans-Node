import pygame
import os
import sys
import subprocess
import platform
import threading

# Configuration des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf") # Ton nouveau fichier

def generate_voice_thread():
    """Génère l'audio en arrière-plan avec priorité basse."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    text = "Bonjour et bienvenue à bord."
    
    # On prépare les variables proprement avant de créer la commande
    piper_path = os.path.join(piper_dir, "piper")
    
    if platform.system() == "Windows":
        piper_exe = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_exe}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        # Version Linux / Raspberry Pi avec optimisation threads
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | nice -n 15 "{piper_path}" --model "{model_path}" '
            f'--output_file "{VOICE_TEMP}" --threads 4'
        )
    
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"Erreur Piper : {e}")

def main():
    # Initialisation Audio (Buffer de 4096 pour éviter les craquements)
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # Lancement immédiat de Piper en tâche de fond
    voice_thread = threading.Thread(target=generate_voice_thread)
    voice_thread.daemon = True # S'arrête si le programme principal s'arrête
    voice_thread.start()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Chargement Logo
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    h_logo = int(sh * 0.5)
    ratio = h_logo / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    # Chargement Police Locale (Ubuntu-Medium)
    if os.path.exists(FONT_PATH):
        font = pygame.font.Font(FONT_PATH, int(sh * 0.07))
    else:
        print("Avertissement: Police Ubuntu introuvable, repli sur police par défaut.")
        font = pygame.font.Font(None, int(sh * 0.09))

    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # Chronologie
    circle_dur = 2500 
    fade_dur = 2000
    start_time = pygame.time.get_ticks()
    
    has_played = False
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        # 1. Animation Cercle
        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            prog = elapsed / circle_dur
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        # 2. Animation Fondu
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            
            txt_tmp = txt_surf.copy()
            txt_tmp.set_alpha(alpha)
            screen.blit(txt_tmp, txt_rect)

        # 3. Écran Fixe + Audio
        else:
            screen.fill((255, 255, 255))
            logo.set_alpha(255)
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            if not has_played:
                # Si Piper a fini de générer le fichier
                if not voice_thread.is_alive():
                    if os.path.exists(VOICE_TEMP):
                        pygame.mixer.Sound(VOICE_TEMP).play()
                    has_played = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()