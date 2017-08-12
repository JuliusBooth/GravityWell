from Heavenly_Bodies import *
from pygame.locals import *
from time import time,sleep

BLACK = (0,0,0)
WHITE = (255,255,255)



class Timer:
    def __init__(self):
        self.starting_time = time()
        self.time_paused = 0

    def reset(self):
        self.starting_time = time()
        self.time_paused = 0

    def pause(self):
        self.pause_time = time()

    def unpause(self):
        self.time_paused += (time() - self.pause_time)

    def get_time(self):
        return(time() - self.starting_time - self.time_paused)



class App:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self._running = True
        self._display = None
        self.time = Timer()
        self.size = self.weight, self.height = display_width, display_height

    def on_init(self):
        self.time.reset()
        pygame.init()
        pygame.key.set_repeat(500, 50)
        self._display = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('Gravity Well')
        self._running = True
        self.blackhole = BlackHole()
        self.spaceship = SpaceShip(self.blackhole,self)


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.spaceship.movedown()
            if event.key == pygame.K_UP:
                self.spaceship.moveup()
            if event.key == pygame.K_SPACE:
                self.clear_space()
                self.on_init()
            if event.key == pygame.K_p:
                self.pause()
            if event.key == pygame.K_t:
                self.crash()

    def pause(self):
        self.time.pause()
        self._display.fill(WHITE)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.time.unpause()

                        return
                if event.type == pygame.QUIT:
                    self._running = False
                    return
            self.addRect()
            self.addText("Paused", 0)
            self.addText("Press 'p' To Resume", 1)
            self.clock.tick(15)

    def clear_space(self):
        Heavenly_Body.instances = []
        Heavenly_Body.other_objects = []


    def addRect(self):
        self.rect = pygame.draw.rect(self._display,BLACK, (display_width/4,display_height/4,display_width/2,display_height/2) ,2)
        pygame.display.update()

    @staticmethod
    def message(text,color,fontsize):
        font = pygame.font.Font('freesansbold.ttf', fontsize)
        return(font.render(text, True, color))

    def addText(self,text,msg_number,FONTSIZE=60):
        msg =  self.message(text,BLACK,FONTSIZE)
        dimensions = msg.get_rect()
        width,height = dimensions[2],dimensions[3]
        self._display.blit(msg,((display_width-width)/2,(display_height-height)/2 + msg_number*height ))
        pygame.display.update()

    def show_score(self):
        score = str(self.spaceship.get_score())
        msg = self.message(score,BLACK,30)
        self._display.blit(msg, (0,0))

    def show_time(self,current_time):
        msg = self.message(str(current_time),BLACK,30)
        self._display.blit(msg,(display_width-60,0))


    def crash(self):
        crash_time = self.time.get_time()
        sleep(1)
        self._display.fill(WHITE)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.clear_space()
                        self.on_init()
                        return
                if event.type == pygame.QUIT:
                    self._running = False
                    return

            self.show_score()
            self.show_time(crash_time)
            self.addRect()
            self.addText("You Crashed!",0)
            self.addText("Play Again?", 1)
            self.clock.tick(15)

    def add_obstacles(self):
        time = min(int(self.time.get_time())*2,100)
        if random.randint(0, 150 - time) == 1:
            Planet()
        if random.randint(0, 150 - time) == 1:
            Star()

    def on_loop(self):
        self._display.fill(WHITE)
        self.add_obstacles()
        for instance in Heavenly_Body.instances:
            instance.update_pos()
        self.spaceship.update_pos()


    def on_render(self):
        for instance in Heavenly_Body.instances:
            instance.draw(self._display)
        for other_object in Heavenly_Body.other_objects:
            other_object.draw(self._display)
        self.show_score()
        self.show_time(self.time.get_time())
        pygame.display.flip()

    def on_cleanup(self):
        print("Thanks for playing!")
        pygame.quit()
        quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(40)
        self.on_cleanup()



theApp = App()
theApp.on_execute()