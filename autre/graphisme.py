import pygame
import os
from datetime import datetime

def dessiner(screen):
    # Récupération de la taille de l'écran dynamique
    W, H = screen.get_size()

    # --- CHEMINS DES ASSETS ---
    base_path = r"C:\Users\UTILISATEUR\Desktop\Trans node\Trans-Node\assets"
    path_font = os.path.join(base_path, "Ubuntu-Medium.ttf")
    path_logo = os.path.join(base_path, "trans-node-nobg.png")
    path_fleche = os.path.join(base_path, "fleche-gps.svg")
    path_rond_svg = os.path.join(base_path, "rond-arret-actuel.svg")

    # --- COULEURS ---
    VERT_SIV = (0, 155, 100)
    BLEU_SIV = (0, 120, 190)
    GRIS_FOND = (220, 220, 220)
    BLANC = (255, 255, 255)
    NOIR = (0, 0, 0)

    # 1. Fond
    screen.fill(GRIS_FOND)

    # 2. Bandeau Vert (Haut)
    hauteur_bandeau = H * 0.18
    pygame.draw.rect(screen, VERT_SIV, (200, 0, W, hauteur_bandeau + 20), border_bottom_left_radius=30)

    # 3. Chargement et affichage du Logo
    if os.path.exists(path_logo):
        logo = pygame.image.load(path_logo).convert_alpha()
        # On garde ton ratio de 1
        ratio_logo = (hauteur_bandeau * 1.29) / logo.get_height()
        logo = pygame.transform.smoothscale(logo, (int(logo.get_width() * ratio_logo), int(hauteur_bandeau * 1.283)))
        screen.blit(logo, (0, (hauteur_bandeau - logo.get_height()) // 2))

    # 4. Polices, Destination et Heure Réelle
    if os.path.exists(path_font):
        font_dest = pygame.font.Font(path_font, int(H * 0.08))
        font_heure = pygame.font.Font(path_font, int(H * 0.07))
        font_arret = pygame.font.Font(path_font, int(H * 0.048))
        font_p_arret = pygame.font.Font(path_font, int(H * 0.05))
        font_gare = pygame.font.Font(path_font, int(H * 0.1))
    else:
        # Secours si Ubuntu est introuvable
        font_dest = font_heure = font_arret = font_p_arret = font_gare = pygame.font.SysFont("Arial", 40, bold=True)

    # Texte Destination
    txt_dest = font_dest.render("Destination : Gan le neez", True, BLANC)
    screen.blit(txt_dest, (W * 0.135, hauteur_bandeau * 0.25))

    # Affichage de l'HEURE RÉELLE
    heure_actuelle = datetime.now().strftime("%H:%M")
    txt_heure = font_heure.render(heure_actuelle, True, BLANC)
    screen.blit(txt_heure, (W - txt_heure.get_width() - 30, hauteur_bandeau * 0.28))

    # 5. La Ligne de Trajet (Verte)
    y_ligne = H * 0.58
    pygame.draw.line(screen, VERT_SIV, (200, y_ligne), (W - 2, y_ligne), int(H * 0.025))

    # 6. Les Arrêts et Noms inclinés
    arrets = [
        {"nom": "Bonaparte", "x": W * 0.4},
        {"nom": "Barthou beaumont", "x": W * 0.54},
        {"nom": "Bosquet Quai C", "x": W * 0.68},
    ]

    for a in arrets:
        # Cercles d'arrêts secondaires
        pygame.draw.circle(screen, VERT_SIV, (int(a["x"]), int(y_ligne)), int(H * 0.035), 0)
        pygame.draw.circle(screen, BLANC, (int(a["x"]), int(y_ligne)), int(H * 0.023))
        
        # Texte incliné à 45°
        txt_surface = font_arret.render(a["nom"], True, NOIR)
        txt_rot = pygame.transform.rotate(txt_surface, 45)
        screen.blit(txt_rot, (a["x"] - 2, y_ligne - txt_rot.get_height() - 25))

    # 7. Position Actuelle (Rond SVG et Bulle)
    x_actuel = W * 0.27
    
    # Dessin du rond d'arrêt (Vert à l'extérieur, Bleu au centre)
    rayon_stop = int(H * 0.035)
    pygame.draw.circle(screen, VERT_SIV, (int(x_actuel), int(y_ligne)), rayon_stop)
    pygame.draw.circle(screen, BLEU_SIV, (int(x_actuel), int(y_ligne)), int(rayon_stop * 0.7))

    # Bulle Bleue (Le grand bloc du bas)
    pygame.draw.rect(screen, BLEU_SIV, (0, H * 0.75, W, H * 0.25))
    
    # Triangle de la bulle (la pointe qui remonte vers l'arrêt)
    points_triangle = [
        (x_actuel, y_ligne + 60),    # Pointe du haut qui touche presque l'arrêt
        (x_actuel - 70, H * 0.75),  # Coin gauche sur le bloc bleu
        (x_actuel + 70, H * 0.75)   # Coin droit sur le bloc bleu
    ]
    pygame.draw.polygon(screen, BLEU_SIV, points_triangle)

    # Textes Prochain arrêt
    txt_prochain = font_p_arret.render("Prochain arrêt | next stop", True, BLANC)
    screen.blit(txt_prochain, (70, H * 0.76))

    # Nom de l'arrêt actuel (Gros)
    txt_gare = font_gare.render("GARE DE PAU", True, BLANC)
    screen.blit(txt_gare, (W // 2 - txt_gare.get_width() // 2, H * 0.82))

    # 8. Affichage de la flèche GPS (Fichier SVG)
    if os.path.exists(path_fleche):
        img_fleche = pygame.image.load(path_fleche).convert_alpha()
        largeur_fleche = int(H * 0.4) 
        ratio_f = largeur_fleche / img_fleche.get_width()
        hauteur_f = int(img_fleche.get_height() * ratio_f)
        
        img_fleche = pygame.transform.smoothscale(img_fleche, (largeur_fleche, hauteur_f))
        
        # Positionnement précis selon tes derniers réglages
        screen.blit(img_fleche, (W * 0.03, y_ligne - (img_fleche.get_height() // 2.67)))