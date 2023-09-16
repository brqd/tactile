from abc import abstractmethod
import asyncio
import threading
import time
import pygame
import config


disp: 'Display' = None


class DisplayObject:
    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def draw(self, screen):
        ...

    @abstractmethod
    def handle_event(self, event):
        ...              


class Background(DisplayObject):
    def __init__(self, disp: 'Display'):
        self.game: 'Display' = disp

    async def update(self):
        ...

    async def draw(self, screen: pygame.Surface):
        screen.fill((0,0,0), screen.get_rect())

    async def handle_event(self, event):
        ...

class Picture(DisplayObject):
    def __init__(self, disp: 'Display', image_name: str, x:int, y: int, width: int, height: int):
        self.obj = pygame.image.load(image_name)
        self.obj = pygame.transform.scale(self.obj, (int(width), int(height)))        
        self.rect = self.obj.get_rect()
        self.rect = self.rect.move(x,y)
        self.speed = [2, 2]
        self.game = disp

    async def update(self):
        ...

    async def draw(self, screen):
        screen.blit(self.obj, self.rect)

    async def handle_event(self, event):
        ...

class Spot(DisplayObject):
    def __init__(self, disp: 'Display', x:int, y: int):
        self.obj = pygame.image.load('spot.png')
        self.obj = pygame.transform.scale(self.obj, (25, 25))        
        self.rect = self.obj.get_rect()
        self.rect = self.rect.move(x,y)
        self.speed = [2, 2]
        self.game = disp

    async def update(self):
        ...

    async def draw(self, screen):
        screen.blit(self.obj, self.rect)

    async def handle_event(self, event):
        ...        

class Hand(DisplayObject):
    def __init__(self, game: 'Display', image_name: str, width: int, height: int):
        self.obj = pygame.image.load(image_name)
        self.obj = pygame.transform.scale(self.obj, (int(width), int(height)))
        self.rect = self.obj.get_rect()
        self.game = game

    async def update(self):
        self.rect.x = self.game.hand_pos[0] - self.rect.width // 2
        self.rect.y = self.game.hand_pos[1] - self.rect.height // 2


    async def draw(self, screen: pygame.Surface):
        screen.blit(self.obj, self.rect)

    async def handle_event(self, event):
        ...                   


class Points(DisplayObject):
    def __init__(self, game: 'Display', display_scale):
        self.game = game
        self.point_size = 500       
        self.point_index = 0
        self.points: list[tuple(int, int)] = [(0,0)] * self.point_size
        self.colors:  list[tuple(int, int, int)] = [(0,0,0)] * self.point_size
        self._display_scale = display_scale

    async def update(self):
        ...


    async def draw(self, screen: pygame.Surface):
        for point, color in zip(self.points, self.colors):
            pygame.display.get_surface().set_at((int(point[0]),int(point[1])), color)

    async def handle_event(self, event):
        ...   

    def add_point(self, pos, color = (255,255,255)):
        scaled_pos = (int(pos[0]*self._display_scale), int(pos[1]*self._display_scale))
        self.points[self.point_index] = scaled_pos
        self.colors[self.point_index] = color
        self.point_index += 1
        if self.point_index == self.point_size:
            self.point_index = 0
       



class Display:

    def __init__(self, width, height, scale, pos_queue: asyncio.Queue):
        self._FPS = 100
        self._width = width * scale
        self._height = height * scale
        self._scale = scale
        self._screen: pygame.Surface = None        
        self._event_queue = asyncio.Queue()
        self._objects: list[DisplayObject] = []
        self._pos_queue = pos_queue
        self.hand_pos = (0,0)        

    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    @property
    def objects(self):
        return self._objects   

    @property
    def screen(self):
        return self._screen

    async def run(self):
        # start event handler in separate thread            
        loop = asyncio.get_event_loop()
        stop = threading.Event()
        ready = threading.Event()
        event_loop_thread = threading.Thread(target=self.event_loop, args=(loop, self._event_queue, ready, stop))
        event_loop_thread.start()
        ready.wait()

        draw_task = asyncio.create_task(self.draw_coroutine())
        event_task = asyncio.create_task(self.event_coroutine())
        
        try:
            await asyncio.wait([draw_task, event_task], return_when=asyncio.FIRST_COMPLETED)
        except asyncio.exceptions.CancelledError as e:
            print(f"quit game") 
        except Exception as e:
            print(f"Exception {e}")

        stop.set()
        event_loop_thread.join()
        draw_task.cancel()
        event_task.cancel()             


    def event_loop(
            self,
            loop,
            event_queue: asyncio.Queue,
            ready: threading.Event,
            stop: threading.Event
        ):
        pygame.init() 
        try:
            pygame.display.set_caption("pygame+asyncio")
            self._screen = pygame.display.set_mode((int(self.width), int(self.height))) # screen have to be created in the thread where events are collected
            ready.set()
            while not stop.is_set():          
                event = pygame.event.wait(100) # check stop once a 0.1s
                if event.type != pygame.NOEVENT:
                    asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)
        finally:
            pygame.quit()


    async def draw_coroutine(self):
        black = 0, 0, 0
        current_time = 0
        try:
            while True:
                last_time, current_time = current_time, time.time()
                await asyncio.sleep(1 / self._FPS - (current_time - last_time))  # tick                
                self._screen.fill(black)
                for obj in self._objects:
                    await obj.update()
                    await obj.draw(self._screen)
                pygame.display.flip()
        except asyncio.exceptions.CancelledError as e:
            print(f"draw_coroutine cancelled")
        except Exception as e:
            print(f"draw_coroutine exception {str(e)}")            


    async def event_coroutine(self):
        try:
            while True:
                event: pygame.event.Event = await self._event_queue.get()
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.dict['pos']                    
                    await self._pos_queue.put((pos[0]/self._scale, pos[1]/self._scale))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.dict['pos']                    
                    print(f"{pos[0]/self._scale}, {pos[1]/self._scale}")


                for obj in self._objects:
                    await obj.handle_event(event)

        except asyncio.exceptions.CancelledError as e:
            print(f"event_coroutine cancelled")
        except Exception as e:
            print(f"event_coroutine exception {str(e)}")              


    def add_object(self, obj: DisplayObject):
        self._objects.append(obj)

    def update(self, pos):
        self.hand_pos = (pos[0]*self._scale, pos[1]*self._scale)

points = None

async def configure(conf: config.Config, queue: asyncio.Queue):
    global disp, points, _display_scale

    disp = Display(conf.area_width, conf.area_height, conf.display_scale, queue)
    disp.add_object(Background(disp))
    # for painting in conf.paintings:
    #     disp.add_object(Picture(
    #         disp,
    #         painting.image_file,
    #         painting.x * conf.display_scale,
    #         painting.y * conf.display_scale,
    #         painting.width * conf.display_scale,
    #         painting.height * conf.display_scale            
    #     ))
    for param in conf.bank_params:
        for value in param.values:
            for spot in value.spots:
                disp.add_object(Spot(
                    disp,
                    spot.x * conf.display_scale,
                    spot.y * conf.display_scale
                ))       
    disp.add_object(Hand(disp, 'hand.png', 200*conf.display_scale, 200*conf.display_scale))
    points = Points(disp, conf.display_scale) 
    disp.add_object(points)    

async def run():
    await disp.run()

def update(pos: tuple[float,float]):
    disp.update(pos)
