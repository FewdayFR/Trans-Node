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

def generate_voice_pico():
    """Génère l'audio instantanément avec Pico2Wave."""
    text = "Bonjour et bienvenue à bord."
    
    if platform.system() == "Windows":
        # Pico2Wave n'existe pas nativement sur Windows
        # On peut mettre un message ou garder un Piper basique pour les tests PC
        print("Pico2Wave non dispo sur Windows. Teste sur le Pi !")
    else:
        # Commande Linux : -l = langue, -w = fichier de sortie
        command = f'pico2wave -l fr-FR -w "{VOICE_TEMP}" "{text}"'
        try:
            subprocess.run(command, shell=True, check=True)
            print("Audio Pico2Wave généré.")
        except Exception as e:
            print(f"Erreur Pico2Wave : {e}")

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()

    # On lance la génération (c'est tellement rapide qu'on pourrait presque s'en passer)
    voice_thread = threading.Thread(target=generate_voice_pico)
    voice_thread.start()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Logo et Texte
    logo_path = os.path.join("assets", "trans-node-nobg.png")
    logo_img = pygame.image.load(logo_path).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * (h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.Font(FONT_PATH, int(sh * 0.07)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 50)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

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
                voice_thread.join() # On attend (ce sera très court)
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                has_played = True

        pygame.display.flip()

if __name__ == "__main__":
    main()