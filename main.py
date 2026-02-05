import pygame
import os
import sys
import subprocess
import platform
import threading
import hashlib

# Configuration des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# Dossier pour stocker les voix déjà générées
CACHE_DIR = os.path.join(BASE_DIR, "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")

def get_voice_path(text):
    """Calcule un nom de fichier unique pour le texte et le génère si besoin."""
    # On crée un nom de fichier unique basé sur la phrase (ex: a1b2c3.wav)
    text_hash = hashlib.md5(text.encode()).hexdigest()
    voice_path = os.path.join(CACHE_DIR, f"{text_hash}.wav")
    
    # Si le fichier existe déjà, on ne fait rien, on le réutilisera
    if os.path.exists(voice_path):
        return voice_path

    # Sinon, on génère avec Piper (Qualité réaliste)
    print(f"Génération de la voix (première fois)... : {text}")
    piper_dir = os.path.join(BASE_DIR, "piper")
    piper_path = os.path.join(piper_dir, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    if platform.system() == "Windows":
        piper_exe = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_exe}" --model "{model_path}" --output_file "{voice_path}"'
    else:
        # Utilisation de 4 threads pour aller plus vite sur Raspberry Pi
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | nice -n 10 "{piper_path}" --model "{model_path}" '
            f'--output_file "{voice_path}" --threads 4'
        )
    
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"Erreur Piper : {e}")
    
    return voice_path

def main():
    # 1. Initialisation Pygame
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # 2. Préparation de la voix (Cache ou Génération)
    # On définit la phrase ici. Si elle change, Piper se relancera une fois.
    phrase = "Bonjour et bienvenue à bord."
    
    # On lance la préparation dans un thread pour ne pas bloquer le chargement initial
    voice_data = {"path": None}
    def prepare():
        voice_data["path"] = get_voice_path(phrase)
    
    voice_thread = threading.Thread(target=prepare)
    voice_thread.start()

    # 3. Configuration Écran
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # 4. Chargement Assets
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * (h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.Font(FONT_PATH, int(sh * 0.07)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 50)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # 5. Boucle d'animation
    start_time = pygame.time.get_ticks()
    circle_dur, fade_dur = 2000, 2000
    has_played = False
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed < circle_dur:
            # Animation 1: Cercle noir vers blanc
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
            
        elif elapsed < (circle_dur + fade_dur):
            # Animation 2: Apparition Logo + Texte
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            t_tmp = txt_surf.copy()
            t_tmp.set_alpha(alpha)
            screen.blit(t_tmp, txt_rect)
            
        else:
            # État Final fixe
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            # Jouer le son
            if not has_played:
                voice_thread.join() # On attend que le fichier soit prêt (0ms si déjà en cache)
                if voice_data["path"] and os.path.exists(voice_data["path"]):
                    pygame.mixer.Sound(voice_data["path"]).play()
                has_played = True

        pygame.display.flip()

if __name__ == "__main__":
    main()