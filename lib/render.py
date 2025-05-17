import pygame
from PIL import Image
import numpy as np
from lib.graph import Subgraph
import time


def draw_point(screen, coord, intersection=False):
    if screen is not None:
        pygame.draw.circle(
            screen,
            (0, 255, 0) if intersection else (255, 0, 0),
            (coord[1], coord[0]),
            4 if intersection else 2,
        )
        pygame.display.flip()


def draw_traversal(
    screen, subgraph: Subgraph, index1: int, index2: int, other_color=False
):
    if screen is not None:
        draw_point(screen, subgraph.coords[index1], intersection=True)

        path = subgraph.paths[index1][index2]

        for i in range(len(path) - 1):
            pygame.draw.line(
                screen,
                (255, 0, 0) if not other_color else (255, 255, 0),
                (subgraph.coords[path[i]][1], subgraph.coords[path[i]][0]),
                (subgraph.coords[path[i + 1]][1], subgraph.coords[path[i + 1]][0]),
                2,
            )
            pygame.display.flip()

        draw_point(screen, subgraph.coords[index2], intersection=True)

    time.sleep(0.05)


def draw_subgraph(screen, subgraph: Subgraph):
    if screen is not None:
        for i in subgraph.paths:
            for j in subgraph.paths[i]:
                if i < j:
                    draw_traversal(screen, subgraph, i, j)

        for i in subgraph.edges:
            draw_point(screen, subgraph.coords[i], intersection=True)

    while True:
        pass


class PygameRecord:
    """
    PygameRecord - A utility for recording Pygame screens as GIFS.
    This module provides a class, PygameRecord, which can be used to record Pygame
    animations and save them as GIF files. It captures frames from the Pygame display
    and saves them as images, then combines them into a GIF file.
    Credits:
    - Author: Ricardo Ribeiro Rodrigues
    - Date: 21/03/2024
    - source: https://gist.github.com/RicardoRibeiroRodrigues/9c40f36909112950860a410a565de667
    Usage:
    1. Initialize PygameRecord with a filename and desired frames per second (fps).
    2. Enter a Pygame event loop.
    3. Add frames to the recorder at desired intervals.
    4. When done recording, exit the Pygame event loop.
    5. The recorded GIF will be saved automatically.
    """

    def __init__(self, filename: str, fps: int):
        self.fps = fps
        self.filename = filename
        self.frames = []

    def add_frame(self):
        curr_surface = pygame.display.get_surface()
        x3 = pygame.surfarray.array3d(curr_surface)
        x3 = np.moveaxis(x3, 0, 1)
        array = Image.fromarray(np.uint8(x3))
        self.frames.append(array)

    def save(self):
        self.frames[0].save(
            self.filename,
            save_all=True,
            optimize=False,
            append_images=self.frames[1:],
            loop=0,
            duration=int(1000 / self.fps),
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred: {exc_value}")
        self.save()
        # Return False if you want exceptions to propagate, True to suppress them
        return False
