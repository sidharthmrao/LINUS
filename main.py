import pygame
import time

from lib.serial_com import initialize, send_path
from lib.skeleton import gen_skel
from lib.render import PygameRecord
from lib.slicer import slice
import config

path = config.image_path

name = path.split("/")[-1].split(".")[0]
output = config.output_path or f"output/{name}_skel.png"

screen = None
if config.display:
    pygame.init()
    screen = pygame.display.set_mode((480, 480))

path = slice(
    gen_skel(path, output),
    screen if config.debug else None,
)

# output bounds are [0, 4]
for i in range(len(path)):
    path[i] = (path[i][0] / 120.0, path[i][1] / 120.0)

path = path[::1]

recorder = PygameRecord("output/skel.gif", 1000)

if config.display and screen is not None:
    screen.fill((0, 0, 0))

    last = (0, 0)
    for i in range(len(path)):
        # Color over last point
        if i > 0:
            pygame.draw.circle(screen, (255, 0, 0), last, 2)

        x, y = path[i]
        pygame.draw.line(screen, (255, 0, 0), last, (y * 120, x * 120), 2)
        last = (y * 120, x * 120)

        # Draw the current point
        pygame.draw.circle(screen, (0, 255, 0), (y * 120, x * 120), 2)

        pygame.display.flip()

        if i % 30 == 0:
            recorder.add_frame()

        time.sleep(config.frame_delay_s)

    recorder.save()

    if config.stay_open_post_render:
        while True:
            pass

    pygame.quit()
else:
    ser = initialize("/dev/serial0")
    send_path(ser, "/dev/serial0", path)
