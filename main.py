import pygame
import os
import sys

LOGO_PATH = os.path.join("assets", "trans-node-nobg.png")

def main():
    pygame.init()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    if not os.path.exists(LOGO_PATH):
        pygame.quit()
        return

    logo_img = pygame.image.load(LOGO_PATH).convert_alpha()
    nouvelle_hauteur = int(sh * 0.5)
    ratio = nouvelle_hauteur / logo_img.get_height()
    logo = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * ratio), nouvelle_hauteur))
    logo_rect = logo.get_rect(center=(sw // 2, sh // 2 - 50))

    font = pygame.font.SysFont("Arial", int(sh * 0.07), bold=True)
    texte_surface = font.render("Bienvenue à bord", True, (40, 40, 40))
    texte_rect = texte_surface.get_rect(center=(sw // 2, logo_rect.bottom + 60))

    duration = 2000 
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: pygame.display.iconify()
                if event.key == pygame.K_ESCAPE: running = False

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed < duration:
            screen.fill((0, 0, 0))
            progression = elapsed / duration
            radius = int(progression * (max(sw, sh) * 0.8))
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), radius)

        else:
            screen.fill((255, 255, 255))
            logo_elapsed = elapsed - duration
            alpha = int(min(logo_elapsed / duration, 1) * 255)
            
            logo_temp = logo.copy()
            logo_temp.set_alpha(alpha)
            screen.blit(logo_temp, logo_rect)

            texte_temp = texte_surface.copy()
            texte_temp.set_alpha(alpha)
            screen.blit(texte_temp, texte_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()