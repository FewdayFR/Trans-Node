import pygame
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess

# --- CONFIGURATION DES CHEMINS (RASPBERRY PI) ---
# On utilise /home/pi/ ou le chemin relatif si tu lances le script depuis le dossier
BASE_DIR = "/home/pi/Trans-Node" 
PATH_XML = os.path.join(BASE_DIR, "fichiers_xml/11.xml")
BASE_ASSETS = os.path.join(BASE_DIR, "assets")
PATH_FONT = os.path.join(BASE_ASSETS, "Ubuntu-Medium.ttf")
PATH_LOGO = os.path.join(BASE_ASSETS, "trans-node-nobg.png")
PATH_FLECHE = os.path.join(BASE_ASSETS, "fleche-gps.svg")

# Configuration Piper (TTS)
PATH_PIPER = "piper"  # Installé globalement ou chemin vers l'exécutable
PATH_VOIX = os.path.join(BASE_DIR, "models/fr_FR-siwis-medium.onnx")

def charger_donnees_bus(chemin_xml):
    if not os.path.exists(chemin_xml):
        return "Destination Inconnue", ["Erreur XML"] * 10
    try:
        tree = ET.parse(chemin_xml)
        root = tree.getroot()
        dest_element = root.find(".//destination/description")
        destination = dest_element.text if dest_element is not None else "Destination"
        liste_arrets = []
        for sequence in root.find(".//destination"):
            if 'sequence_' in sequence.tag:
                nom = sequence.find("nom_arret").text
                if not liste_arrets or liste_arrets[-1] != nom:
                    liste_arrets.append(nom)
        return destination, liste_arrets
    except Exception:
        return "Erreur", ["Erreur"] * 10

def annoncer_arret(nom_arret):
    """Lance la synthèse vocale Piper sur Raspberry Pi"""
    phrase = f"Prochain arrêt, {nom_arret}"
    try:
        # Commande optimisée pour la sortie audio du Raspberry Pi
        cmd = f'echo "{phrase}" | {PATH_PIPER} --model {PATH_VOIX} --output_raw | aplay -r 22050 -f S16_LE -t raw'
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Erreur TTS : {e}")

# --- INITIALISATION ---
pygame.init()
sizes = pygame.display.get_desktop_sizes()
res = sizes[1] if len(sizes) > 1 else sizes[0]

# Positionnement sur le 2ème écran si présent
if len(sizes) > 1:
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{sizes[0][0]},0"

screen = pygame.display.set_mode(res, pygame.NOFRAME)
clock = pygame.time.Clock()

dest_label, tous_les_arrets = charger_donnees_bus(PATH_XML)
index_actuel = 1
DERNIER_CHANGEMENT = pygame.time.get_ticks()
DELAI_CHANGEMENT = 5000 
TERMINE = False

# Première annonce
if len(tous_les_arrets) > index_actuel:
    annoncer_arret(tous_les_arrets[index_actuel])

running = True
while running:
    W, H = screen.get_size()
    maintenant = pygame.time.get_ticks()

    # --- LOGIQUE DE CYCLE ---
    if maintenant - DERNIER_CHANGEMENT > DELAI_CHANGEMENT and not TERMINE:
        index_actuel += 1
        DERNIER_CHANGEMENT = maintenant
        
        if index_actuel < len(tous_les_arrets):
            nom_actuel = tous_les_arrets[index_actuel]
            annoncer_arret(nom_actuel)
            
            # Si l'arrêt actuel correspond à la destination (Terminus)
            if nom_actuel.lower().strip() == dest_label.lower().strip():
                TERMINE = True
        else:
            TERMINE = True

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Couleurs
    VERT_SIV = (0, 155, 100)
    BLEU_SIV = (0, 120, 190)
    GRIS_FOND = (220, 220, 220)
    BLANC = (255, 255, 255)
    NOIR = (0, 0, 0)

    screen.fill(GRIS_FOND)

    # 1. Bandeau Haut
    hauteur_bandeau = H * 0.18
    pygame.draw.rect(screen, VERT_SIV, (200, 0, W, hauteur_bandeau + 20), border_bottom_left_radius=30)

    # 2. Logo
    if os.path.exists(PATH_LOGO):
        logo = pygame.image.load(PATH_LOGO).convert_alpha()
        ratio = (hauteur_bandeau * 1.29) / logo.get_height()
        logo = pygame.transform.smoothscale(logo, (int(logo.get_width() * ratio), int(hauteur_bandeau * 1.28)))
        screen.blit(logo, (0, (hauteur_bandeau - logo.get_height()) // 2))

    # 3. Destination (Taille Dynamique)
    taille_d = int(H * 0.08)
    if len(dest_label) > 30: taille_d = int(H * 0.05)
    font_dest = pygame.font.Font(PATH_FONT, taille_d)
    txt_dest = font_dest.render(f"Destination : {dest_label}", True, BLANC)
    screen.blit(txt_dest, (W * 0.135, hauteur_bandeau * 0.25))

    # 4. Heure
    font_h = pygame.font.Font(PATH_FONT, int(H * 0.07))
    txt_h = font_h.render(datetime.now().strftime("%H:%M"), True, BLANC)
    screen.blit(txt_h, (W - txt_h.get_width() - 30, hauteur_bandeau * 0.28))

    # 5. Ligne de Trajet
    y_ligne = H * 0.58
    pygame.draw.line(screen, VERT_SIV, (200, y_ligne), (W - 2, y_ligne), int(H * 0.025))

    # 6. Flèche GPS
    if os.path.exists(PATH_FLECHE):
        img_f = pygame.image.load(PATH_FLECHE).convert_alpha()
        img_f = pygame.transform.smoothscale(img_f, (int(H*0.4), int(H*0.25)))
        screen.blit(img_f, (W * 0.03, y_ligne - (img_f.get_height() // 2.67)))

    # 7. ARRÊTS SUIVANTS (Masqués si Terminus)
    if not TERMINE:
        positions_x = [W * 0.4, W * 0.54, W * 0.68]
        for i, x_pos in enumerate(positions_x):
            idx_suivant = index_actuel + 1 + i
            if idx_suivant < len(tous_les_arrets):
                nom_a = tous_les_arrets[idx_suivant]
                pygame.draw.circle(screen, VERT_SIV, (int(x_pos), int(y_ligne)), int(H * 0.035))
                pygame.draw.circle(screen, BLANC, (int(x_pos), int(y_ligne)), int(H * 0.023))
                
                taille_a = int(H * 0.05)
                if len(nom_a) > 14: taille_a = int(H * 0.035)
                
                font_a = pygame.font.Font(PATH_FONT, taille_a)
                txt_rot = pygame.transform.rotate(font_a.render(nom_a, True, NOIR), 45)
                screen.blit(txt_rot, (x_pos - 2, y_ligne - txt_rot.get_height() - 25))

    # 8. BULLE BLEUE
    x_actuel = W * 0.27
    prochain_nom = tous_les_arrets[index_actuel]
    
    pygame.draw.circle(screen, VERT_SIV, (int(x_actuel), int(y_ligne)), int(H * 0.035))
    pygame.draw.circle(screen, BLEU_SIV, (int(x_actuel), int(y_ligne)), int(H * 0.025))
    
    pygame.draw.rect(screen, BLEU_SIV, (0, H * 0.75, W, H * 0.25))
    pygame.draw.polygon(screen, BLEU_SIV, [(x_actuel, y_ligne + 60), (x_actuel - 70, H * 0.75), (x_actuel + 70, H * 0.75)])

    font_p = pygame.font.Font(PATH_FONT, int(H * 0.05))
    txt_status = "Terminus" if TERMINE else "Prochain arrêt | next stop"
    screen.blit(font_p.render(txt_status, True, BLANC), (70, H * 0.76))
    
    font_gare = pygame.font.Font(PATH_FONT, int(H * 0.1))
    txt_gare = font_gare.render(prochain_nom.upper(), True, BLANC)
    screen.blit(txt_gare, (W // 2 - txt_gare.get_width() // 2, H * 0.82))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()