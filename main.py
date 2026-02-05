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

def speak_after_animation():
    """Génère et joue la voix une fois que l'écran est stable."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    text = "Bonjour et bienvenue à bord."
    
    if platform.system() == "Windows":
        piper_path = os.path.join(piper_dir, "piper.exe")
        command = f'echo {text} | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
    else:
        piper_path = os.path.join(piper_dir, "piper")
        subprocess.run(["amixer", "sset", "Master", "100%"], capture_output=True)
        command = (
            f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
            f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
        )

    # Exécution de Piper
    try:
        subprocess.run(command, shell=True, check=True)
        if os.path.exists(VOICE_TEMP):
            speech = pygame.mixer.Sound(VOICE_TEMP)
            speech.play()
    except Exception as e:
        print(f"Erreur audio : {e}")

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Chargement graphique
    if not os.path.exists(LOGO_PATH): return
    logo_img = pygame.image.load(LOGO_PATH).convert_alpha()
    h_logo = int(sh * 0.5)
    ratio = h_logo / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.SysFont("Arial", int(sh * 0.07), bold=True)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    # Chronologie
    circle_duration = 2000  # 2s pour le cercle
    fade_duration = 2000    # 2s pour le fondu du logo
    start_time = pygame.time.get_ticks()
    
    has_spoken = False
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        # 1. Animation du cercle (Fond noir)
        if elapsed < circle_duration:
            screen.fill((0, 0, 0))
            prog = elapsed / circle_duration
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        # 2. Animation du fondu (Fond blanc)
        elif elapsed < (circle_duration + fade_duration):
            screen.fill((255, 255, 255))
            fade_elapsed = elapsed - circle_duration
            alpha = int((fade_elapsed / fade_duration) * 255)
            
            l_tmp = logo.copy()
            l_tmp.set_alpha(alpha)
            screen.blit(l_tmp, logo_rect)
            
            t_tmp = txt_surf.copy()
            t_tmp.set_alpha(alpha)
            screen.blit(t_tmp, txt_rect)

        # 3. Écran fixe + Lancement du son
        else:
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            # On ne lance le son que quand tout est fini et stable
            if not has_spoken:
                pygame.display.flip() # On force le dernier affichage avant de bloquer pour Piper
                speak_after_animation()
                has_spoken = True

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()