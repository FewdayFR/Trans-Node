import pygame
import os
import sys

LOGO_PATH = os.path.join("assets", "trans-node-nobg.png")

def main():
    pygame.init()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    
    if not os.path.exists(LOGO_PATH):
        pygame.quit()
        return

    logo_img = pygame.image.load(LOGO_PATH).convert_alpha()
    
    nouvelle_hauteur = int(sh * 0.5)
    ratio = nouvelle_hauteur / logo_img.get_height()
    nouvelle_largeur = int(logo_img.get_width() * ratio)
    
    logo = pygame.transform.smoothscale(logo_img, (nouvelle_largeur, nouvelle_hauteur))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font_size = int(sh * 0.07)
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    
    texte_surface = font.render("Bienvenue à bord", True, (40, 40, 40))
    texte_rect = texte_surface.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    pygame.display.iconify()
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((255, 255, 255))
        screen.blit(logo, logo_rect)
        screen.blit(texte_surface, texte_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()