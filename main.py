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

def speak_with_pygame():
    """Génère la voix avec Piper et la joue avec Pygame de manière robuste."""
    if platform.system() == "Windows":
        piper_path = os.path.join("piper", "piper.exe")
    else:
        piper_path = os.path.join("piper", "piper")
        subprocess.run(["amixer", "sset", "Master", "100%"], capture_output=True)

    model_path = os.path.join("models", "fr_FR-siwis-medium.onnx")
    text = "Bonjour et bienvenue a bord."

    if os.path.exists(piper_path) and os.path.exists(model_path):
        # Suppression de l'ancien fichier s'il existe pour éviter les conflits
        if os.path.exists(VOICE_TEMP):
            try: os.remove(VOICE_TEMP)
            except: pass

        # Lancement de Piper (on attend qu'il finisse avec .run)
        command = f'echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{VOICE_TEMP}"'
        subprocess.run(command, shell=True)
        
        # Petite pause de sécurité pour laisser le système libérer le fichier
        time.sleep(0.2)

        if os.path.exists(VOICE_TEMP):
            try:
                speech = pygame.mixer.Sound(VOICE_TEMP)
                speech.set_volume(1.0)
                speech.play()
                print("Audio lancé avec succès !")
            except pygame.error as e:
                print(f"Erreur Pygame Audio : {e}")

def main():
    # Initialisation audio avant l'init général pour éviter les délais
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    if not os.path.exists(LOGO_PATH):
        pygame.quit()
        return

    # Préparation graphique
    logo_img = pygame.image.load(LOGO_PATH).convert_alpha()
    h_logo = int(sh * 0.5)
    ratio = h_logo / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.SysFont("Arial", int(sh * 0.07), bold=True)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    duration = 2000 
    start_time = pygame.time.get_ticks()
    has_spoken = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed < duration:
            screen.fill((0, 0, 0))
            prog = elapsed / duration
            radius = int(prog * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        else:
            # Lancement de la voix au moment de l'apparition du logo
            if not has_spoken:
                speak_with_pygame()
                has_spoken = True

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