import pygame
import sys
from pathlib import Path


def get_project_name() -> str:
    return Path(__file__).resolve().parent.name


def main():
    pygame.init()

    project_name = get_project_name()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(project_name)

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((15, 15, 20))

        font = pygame.font.SysFont("consolas", 24)
        text = font.render(f"Blank project: {project_name}", True, (200, 200, 200))
        screen.blit(text, (20, 20))
        text2 = font.render("Remove this code to start", True, (200, 200, 200))
        screen.blit(text2, (20, 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
