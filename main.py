import pygame
import os
import sys
import subprocess
import platform
import threading

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")

def generate_voice():
    """Génère la voix Piper directement."""
    text = "Idéliss, Bonjour et bienvenue à bord."
    piper_dir = os.path.join(BASE_DIR, "piper")
    piper_path = os.path.join(piper_dir, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    if platform.system() == "Windows":
        piper_exe = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_exe}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        # Optimisé pour RPi : 4 threads et priorité nice
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | nice -n 10 "{piper_path}" --model "{model_path}" '
            f'--output_file "{VOICE_TEMP}" --threads 4'
        )
    
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"Erreur TTS : {e}")

def main():
    # 1. Initialisation Audio & Vidéo
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # Masquer la souris immédiatement
    pygame.mouse.set_visible(False)

    # 2. Lancer le TTS en parallèle
    voice_thread = threading.Thread(target=generate_voice)
    voice_thread.start()

    # 3. Écran plein écran
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # 4. Chargement Assets (Logo et Texte)
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * (h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    # Police locale
    font = pygame.font.Font(FONT_PATH, int(sh * 0.07)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 50)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # 5. Paramètres Animations
    start_time = pygame.time.get_ticks()
    circle_dur = 2000
    fade_dur = 2000
    has_played = False
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        # Animation du cercle
        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
            
        # Animation Fondu Logo + Texte
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            
            # Copie pour l'alpha du texte
            t_tmp = txt_surf.copy()
            t_tmp.set_alpha(alpha)
            screen.blit(t_tmp, txt_rect)
            
        # État final et lecture audio
        else:
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            if not has_played:
                voice_thread.join() # Attend que Piper finisse
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                has_played = True

        pygame.display.flip()

if __name__ == "__main__":
    main()