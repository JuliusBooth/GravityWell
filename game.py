
from Heavenly_Bodies import *


#set-up environment

pygame.init()




gameDisplay = pygame.display.set_mode((display_width,display_height))
clock = pygame.time.Clock()

for i in range(1000):
    Planet()
Star()
running = True
while running:
    gameDisplay.fill((0, 0, 0))
    for instance in Heavenly_Body.instances:
        instance.update_pos()
        instance.draw(gameDisplay)
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    clock.tick(40)
    pygame.display.flip()