import pygame
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess # Pour lancer Piper (TTS)

# --- CONFIGURATION ---
PATH_XML = r"C:\Users\UTILISATEUR\Desktop\Trans node\Trans-Node\fichiers_xml\11.xml"
BASE_ASSETS = r"C:\Users\UTILISATEUR\Desktop\Trans node\Trans-Node\assets"
PATH_FONT = os.path.join(BASE_ASSETS, "Ubuntu-Medium.ttf")
PATH_LOGO = os.path.join(BASE_ASSETS, "trans-node-nobg.png")
PATH_FLECHE = os.path.join(BASE_ASSETS, "fleche-gps.svg")
# Chemin vers Piper et le modèle voix
PATH_PIPER = "piper" # Assure-toi que piper est installé sur le Pi
PATH_VOIX = r"C:\Users\UTILISATEUR\Desktop\Trans node\Trans-Node\models\fr_FR-siwis-medium.onnx"

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
    """Lance la synthèse vocale Piper"""
    phrase = f"Prochain arrêt, {nom_arret}"
    try:
        # Commande type pour Piper sur Raspberry Pi
        cmd = f'echo "{phrase}" | {PATH_PIPER} --model {PATH_VOIX} --output_raw | aplay -r 22050 -f S16_LE -t raw'
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Erreur TTS : {e}")

pygame.init()
sizes = pygame.display.get_desktop_sizes()
res = sizes[1] if len(sizes) > 1 else sizes[0]
if len(sizes) > 1:
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{sizes[0][0]},0"

screen = pygame.display.set_mode(res, pygame.NOFRAME)
clock = pygame.time.Clock()

dest_label, tous_les_arrets = charger_donnees_bus(PATH_XML)
index_actuel = 1
DERNIER_CHANGEMENT = pygame.time.get_ticks()
DELAI_CHANGEMENT = 5000 
TERMINE = False

# Annonce du premier arrêt au lancement
annoncer_arret(tous_les_arrets[index_actuel])

running = True
while running:
    W, H = screen.get_size()
    maintenant = pygame.time.get_ticks()

    # --- LOGIQUE DE CYCLE ---
    if maintenant - DERNIER_CHANGEMENT > DELAI_CHANGEMENT and not TERMINE:
        index_actuel += 1
        DERNIER_CHANGEMENT = maintenant
        
        # VERIFICATION SI DESTINATION ATTEINTE
        if index_actuel < len(tous_les_arrets):
            annoncer_arret(tous_les_arrets[index_actuel])
            if tous_les_arrets[index_actuel].lower() in dest_label.lower():
                TERMINE = True # On s'arrête ici, on ne boucle plus
        else:
            TERMINE = True

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    VERT_SIV = (0, 155, 100)
    BLEU_SIV = (0, 120, 190)
    GRIS_FOND = (220, 220, 220)
    BLANC = (255, 255, 255)
    NOIR = (0, 0, 0)

    screen.fill(GRIS_FOND)

    # 1. Bandeau Haut et Logo (Idem précédent)
    hauteur_bandeau = H * 0.18
    pygame.draw.rect(screen, VERT_SIV, (200, 0, W, hauteur_bandeau + 20), border_bottom_left_radius=30)
    if os.path.exists(PATH_LOGO):
        logo = pygame.image.load(PATH_LOGO).convert_alpha()
        ratio = (hauteur_bandeau * 1.29) / logo.get_height()
        logo = pygame.transform.smoothscale(logo, (int(logo.get_width() * ratio), int(hauteur_bandeau * 1.28)))
        screen.blit(logo, (0, (hauteur_bandeau - logo.get_height()) // 2))

    # 3. Destination Dynamique
    font_dest = pygame.font.Font(PATH_FONT, int(H * 0.08))
    txt_dest = font_dest.render(f"Destination : {dest_label}", True, BLANC)
    screen.blit(txt_dest, (W * 0.135, hauteur_bandeau * 0.25))

    # 5. Ligne de Trajet
    y_ligne = H * 0.58
    pygame.draw.line(screen, VERT_SIV, (200, y_ligne), (W - 2, y_ligne), int(H * 0.025))

    # 7. ARRÊTS SUIVANTS (On n'affiche que s'ils existent !)
    positions_x = [W * 0.4, W * 0.54, W * 0.68]
    for i, x_pos in enumerate(positions_x):
        idx_suivant = index_actuel + 1 + i
        if idx_suivant < len(tous_les_arrets): # Sécurité : n'affiche rien si index hors liste
            nom_a = tous_les_arrets[idx_suivant]
            pygame.draw.circle(screen, VERT_SIV, (int(x_pos), int(y_ligne)), int(H * 0.035))
            pygame.draw.circle(screen, BLANC, (int(x_pos), int(y_ligne)), int(H * 0.023))
            
            font_arret = pygame.font.Font(PATH_FONT, int(H * 0.05))
            txt_rot = pygame.transform.rotate(font_arret.render(nom_a, True, NOIR), 45)
            screen.blit(txt_rot, (x_pos - 2, y_ligne - txt_rot.get_height() - 25))

    # 8. BULLE BLEUE
    x_actuel = W * 0.27
    prochain_nom = tous_les_arrets[index_actuel]
    pygame.draw.circle(screen, VERT_SIV, (int(x_actuel), int(y_ligne)), int(H * 0.035))
    pygame.draw.circle(screen, BLEU_SIV, (int(x_actuel), int(y_ligne)), int(H * 0.025))
    pygame.draw.rect(screen, BLEU_SIV, (0, H * 0.75, W, H * 0.25))
    pygame.draw.polygon(screen, BLEU_SIV, [(x_actuel, y_ligne + 60), (x_actuel - 70, H * 0.75), (x_actuel + 70, H * 0.75)])

    font_p = pygame.font.Font(PATH_FONT, int(H * 0.05))
    txt_label_stop = "Terminus" if TERMINE else "Prochain arrêt | next stop"
    screen.blit(font_p.render(txt_label_stop, True, BLANC), (70, H * 0.76))
    
    font_gare = pygame.font.Font(PATH_FONT, int(H * 0.1))
    txt_gare = font_gare.render(prochain_nom.upper(), True, BLANC)
    screen.blit(txt_gare, (W // 2 - txt_gare.get_width() // 2, H * 0.82))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()