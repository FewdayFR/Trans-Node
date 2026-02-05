import pygame
import os
import sys
import subprocess
import threading

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
VOICE_TEMP = os.path.join(BASE_DIR, "welcome.wav")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")

def generate_voice():
    """Génère la voix Piper - Optimisé Pi 3 B+"""
    text = "Idéliss, Bonjour et bienvenue à bord."
    piper_dir = os.path.join(BASE_DIR, "piper")
    piper_path = os.path.join(piper_dir, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    # Sur Pi 3 B+, on utilise LD_PRELOAD si possible pour accélérer les maths
    # Mais restons simple avec une priorité élevée (nice)
    command = (
        f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | nice -n -10 "{piper_path}" --model "{model_path}" '
        f'--output_file "{VOICE_TEMP}" --threads 4'
    )
    try:
        subprocess.run(command, shell=True, check=True)
    except: pass

def main():
    # Buffer à 4096 obligatoire sur Pi 3 pour éviter les craquements Jack/HDMI
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    voice_thread = threading.Thread(target=generate_voice)
    voice_thread.start()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # Assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width()*(h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.Font(FONT_PATH, int(sh * 0.07)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 50)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # TIMING AJUSTÉ POUR PI 3 B+
    # On allonge un peu pour que Piper ait le temps de finir pendant l'anim
    circle_dur = 3000  # 3s
    fade_dur = 3000    # 3s (Total 6s d'animation pour couvrir le calcul)
    
    start_time = pygame.time.get_ticks()
    has_played = False
    clock = pygame.time.Clock()

    while True:
        # On limite à 30 FPS. Sur Pi 3 B+, 60 FPS + Piper = Son qui saute.
        # 30 FPS est suffisant pour un logo et libère du CPU pour la voix.
        clock.tick(30) 
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            t_tmp = txt_surf.copy(); t_tmp.set_alpha(alpha); screen.blit(t_tmp, txt_rect)
        else:
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            if not has_played:
                # Si Piper n'a pas fini, l'image reste fixe. 
                # Avec 6s d'anim, l'attente sera quasi nulle.
                voice_thread.join() 
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                has_played = True

        pygame.display.flip()

if __name__ == "__main__":
    main()