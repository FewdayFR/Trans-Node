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

def get_annonces():
    """Extrait les phrases du XML proprement."""
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        return [index.find('tts').text.strip() for index in root.findall('index')]
    except Exception as e:
        print(f"Erreur XML : {e}")
        return []

def piper_worker(text, output_path):
    """Générateur Piper pur sans fioritures."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    piper_path = os.path.join(piper_dir, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    command = (
        f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{output_path}" --threads 4'
    )
    subprocess.run(command, shell=True, check=True, capture_output=True)

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    annonces = get_annonces()
    if not annonces: return

    # Fichiers temporaires pour le flux tendu
    temp_files = [os.path.join(BASE_DIR, "v1.wav"), os.path.join(BASE_DIR, "v2.wav")]

    # --- ÉTAPE 1 : Animation de démarrage ---
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.5)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width()*(h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))
    
    font = pygame.font.Font(FONT_PATH, int(sh * 0.05)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 40)
    
    # On lance la génération de la PREMIÈRE annonce pendant l'anim
    gen_thread = threading.Thread(target=piper_worker, args=(annonces[0], temp_files[0]))
    gen_thread.start()

    start_time = pygame.time.get_ticks()
    circle_dur, fade_dur = 3000, 3000
    anim_done = False
    clock = pygame.time.Clock()

    # Boucle d'animation initiale
    while not anim_done:
        clock.tick(30)
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: sys.exit()

        if elapsed < circle_dur:
            screen.fill((0, 0, 0))
            radius = int((elapsed / circle_dur) * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)
        elif elapsed < (circle_dur + fade_dur):
            screen.fill((255, 255, 255))
            alpha = int(((elapsed - circle_dur) / fade_dur) * 255)
            logo.set_alpha(alpha)
            screen.blit(logo, logo_rect)
        else:
            anim_done = True
        pygame.display.flip()

    # --- ÉTAPE 2 : Lecture en chaîne des annonces ---
    for i, text in enumerate(annonces):
        current_file = temp_files[i % 2]
        next_file = temp_files[(i + 1) % 2]

        # On attend que Piper ait fini de générer le fichier actuel
        if i == 0: gen_thread.join() 
        
        # Affichage du texte de l'annonce
        screen.fill((255, 255, 255))
        screen.blit(logo, logo_rect)
        txt_surf = font.render(text, True, (40, 40, 40))
        txt_rect = txt_surf.get_rect(center=(sw // 2, sh // 2 + 150))
        screen.blit(txt_surf, txt_rect)
        pygame.display.flip()

        # Lecture
        sound = pygame.mixer.Sound(current_file)
        channel = sound.play()
        
        # Suppression immédiate du fichier disque (il est en RAM)
        if os.path.exists(current_file): os.remove(current_file)

        # Génération de l'annonce SUIVANTE pendant la lecture
        if i + 1 < len(annonces):
            gen_thread = threading.Thread(target=piper_worker, args=(annonces[i+1], next_file))
            gen_thread.start()

        # Attente fin de lecture
        while channel.get_busy():
            clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: sys.exit()
        
        # On attend que la génération suivante soit prête avant de boucler
        if i + 1 < len(annonces): gen_thread.join()

    pygame.quit()

if __name__ == "__main__":
    main()