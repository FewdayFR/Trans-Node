import pygame
import os
import sys
import subprocess
import threading
import xml.etree.ElementTree as ET
import time

# Config Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
XML_PATH = os.path.join(BASE_DIR, "line", "library-tts.xml")
FONT_PATH = os.path.join(BASE_DIR, "assets", "Ubuntu-Medium.ttf")

def get_annonces():
    """Extrait les phrases du fichier XML."""
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        return [index.find('tts').text for index in root.findall('index')]
    except Exception as e:
        print(f"Erreur XML: {e}")
        return []

def piper_worker(text, output_path):
    """Fonction de génération Piper isolée."""
    piper_dir = os.path.join(BASE_DIR, "piper")
    piper_path = os.path.join(piper_dir, "piper")
    model_path = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
    
    command = (
        f'export LD_LIBRARY_PATH="{piper_dir}:$LD_LIBRARY_PATH" && '
        f'echo "{text}" | "{piper_path}" --model "{model_path}" '
        f'--output_file "{output_path}" --threads 4'
    )
    subprocess.run(command, shell=True, check=True)

def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    pygame.mouse.set_visible(False)

    # Init Écran
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)

    # Assets
    logo_img = pygame.image.load(os.path.join("assets", "trans-node-nobg.png")).convert_alpha()
    h_logo = int(sh * 0.4)
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width()*(h_logo/logo_img.get_height())), h_logo))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))
    font = pygame.font.Font(FONT_PATH, int(sh * 0.05)) if os.path.exists(FONT_PATH) else pygame.font.Font(None, 40)

    annonces = get_annonces()
    
    # On utilise deux noms de fichiers pour alterner (Ping-Pong buffer)
    temp_files = [os.path.join(BASE_DIR, "v1.wav"), os.path.join(BASE_DIR, "v2.wav")]
    
    for i, text in enumerate(annonces):
        current_file = temp_files[i % 2]
        next_file = temp_files[(i + 1) % 2]
        
        # 1. Générer l'annonce actuelle si c'est la première, sinon elle est déjà prête
        if i == 0:
            piper_worker(text, current_file)

        # 2. Préparer l'affichage
        screen.fill((255, 255, 255))
        screen.blit(logo, logo_rect)
        txt_surf = font.render(text, True, (40, 40, 40))
        txt_rect = txt_surf.get_rect(center=(sw // 2, sh // 2 + 150))
        screen.blit(txt_surf, txt_rect)
        pygame.display.flip()

        # 3. Charger et jouer le son actuel
        sound = pygame.mixer.Sound(current_file)
        channel = sound.play()
        
        # Supprimer le fichier physique dès qu'il est chargé en RAM
        if os.path.exists(current_file):
            os.remove(current_file)

        # 4. PENDANT que ça joue : Générer l'annonce SUIVANTE en arrière-plan
        if i + 1 < len(annonces):
            next_text = annonces[i+1]
            gen_thread = threading.Thread(target=piper_worker, args=(next_text, next_file))
            gen_thread.start()
        
        # 5. Attendre la fin de la lecture ET de la génération suivante
        while channel.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return
            pygame.time.delay(100)
            
        if i + 1 < len(annonces):
            gen_thread.join() # On s'assure que la génération suivante est finie avant de boucler

    pygame.quit()

if __name__ == "__main__":
    main()