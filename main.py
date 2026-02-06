import pygame
import os
import sys
import subprocess
import threading
import xml.etree.ElementTree as ET

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
XML_PATH = os.path.join(BASE_DIR, "line", "library-tts.xml")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")
VOICE_TEMP = os.path.join(BASE_DIR, "welcome_tmp.wav")

def get_first_annonce():
    """Récupère uniquement le premier texte du XML."""
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        first_index = root.find('index')
        if first_index is not None:
            return first_index.find('tts').text.strip()
    except Exception as e:
        print(f"Erreur XML : {e}")
    return "Bienvenue à bord."

def piper_worker(text):
    """Génère le fichier audio temporaire."""
    piper_path = os.path.join(BASE_DIR, "piper", "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    lib_path = os.path.join(BASE_DIR, "piper")
    
    command = (
        f'export LD_LIBRARY_PATH="{lib_path}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{VOICE_TEMP}" --threads 4'
    )
    subprocess.run(command, shell=True, check=True, capture_output=True)

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    text_to_say = get_first_annonce()

    # --- ÉTAPE 1 : Init Écran et Lancement TTS ---
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # Lancement de la génération en arrière-plan pendant l'animation
    gen_thread = threading.Thread(target=piper_worker, args=(text_to_say,))
    gen_thread.start()

    # Assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width()*(h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))
    
    font = pygame.font.Font(FONT_PATH, int(sh * 0.08)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 60)
    txt_surf = font.render("Bienvenue à bord", True, (40, 40, 40))
    txt_rect = txt_surf.get_rect(center=(sw // 2, logo_rect.bottom + 80))

    # --- ÉTAPE 2 : Animation de démarrage ---
    start_time = pygame.time.get_ticks()
    circle_dur, fade_dur = 3000, 3000
    clock = pygame.time.Clock()

    running = True
    has_played = False

    while running:
        clock.tick(30)
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
        
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
            
            t_tmp = txt_surf.copy()
            t_tmp.set_alpha(alpha)
            screen.blit(t_tmp, txt_rect)
        
        else:
            # Écran final fixe
            screen.fill((255, 255, 255))
            screen.blit(logo, logo_rect)
            screen.blit(txt_surf, txt_rect)
            
            # Lecture du son une seule fois
            if not has_played:
                gen_thread.join() # On attend que Piper ait fini
                if os.path.exists(VOICE_TEMP):
                    pygame.mixer.Sound(VOICE_TEMP).play()
                    os.remove(VOICE_TEMP) # Suppression après chargement
                has_played = True

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()