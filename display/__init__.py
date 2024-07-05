from abc import abstractmethod
import os
import asyncio
import threading
import time
import pygame

import state
import models

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


class BackgroundObj(DisplayObject):
    def __init__(self, disp: 'Display'):
        self.game: 'Display' = disp

    async def update(self):
        ...

    async def draw(self, screen: pygame.Surface):
        screen.fill((0,0,0), screen.get_rect())

    async def handle_event(self, event):
        ...

class PictureObj(DisplayObject):
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

class AreasObj(DisplayObject):

    def __init__(self, game: 'Display', scale: float, st: state.State):
        self._game = game
        self._state = st
        self._scale = scale

    async def update(self):
        ...

    async def draw(self, screen: pygame.Surface):
        for area in self._state._areas:
            if area == self._state.get_current_area():
                color = (255,255,255)
            else:
                color = (0,0,128)
            rect = pygame.Rect(
                area.rect.x * self._scale,
                area.rect.y * self._scale,
                area.rect.w * self._scale,
                area.rect.h * self._scale
            )
            pygame.draw.rect(screen, color, rect, 2)

    async def handle_event(self, event):
        ...


class HandObj(DisplayObject):
    def __init__(self, game: 'Display', image_name: str, width: int, height: int):
        self.obj = pygame.image.load(image_name)
        self.obj = pygame.transform.scale(self.obj, (int(width), int(height)))
        self.rect = self.obj.get_rect()
        self.game = game

    async def update(self):
        ...


    async def draw(self, screen: pygame.Surface):
        screen.blit(self.obj, self.rect)

    async def handle_event(self, event):
        ...                      


class PointsObj(DisplayObject):
    def __init__(self, game: 'Display', scale: float, st: state.State):

        self._state = st
        self.game = game
        self.point_size = 500       
        self.point_index = 0
        self._scale = scale

    async def update(self):
        ...


    async def draw(self, screen: pygame.Surface):
        for point in self._state.get_points():
            pygame.display.get_surface().set_at(
                (
                    int(point.pos[0] * self._scale),
                    int(point.pos[1] * self._scale)
                ),
                point.color
            )

    async def handle_event(self, event):
        ...   

    def add_point(self, pos, color = (255,255,255)):
        scaled_pos = (int(pos[0]*self._scale), int(pos[1]*self._scale))
        self.points[self.point_index] = scaled_pos
        self.colors[self.point_index] = color
        self.point_index += 1
        if self.point_index == self.point_size:
            self.point_index = 0
       



class Display:

    def configure(self, conf: models.ConfigFile, painting_conf: models.PaintingFile):

        self._FPS = 100
        self._state = state.app_state
        self._scale = conf.display.scale
        self._width = painting_conf.area.w * self._scale
        self._height =  painting_conf.area.h * self._scale
        self._screen: pygame.Surface = None        
        self._event_queue = asyncio.Queue()
        self._objects: list[DisplayObject] = [] 

        self.add_object(BackgroundObj(self))

        if conf.display.show_paintings:
            for painting in painting_conf.paintings:
                self.add_object(PictureObj(
                    self,
                    os.path.join(state.picture_path, painting.image_file),
                    painting.x * conf.display.scale,
                    painting.y * conf.display.scale,
                    painting.w * conf.display.scale,
                    painting.h * conf.display.scale            
                ))

        if conf.display.show_areas:
            areas_obj = AreasObj(self, conf.display.scale, self._state)
            self.add_object(areas_obj)

        if conf.display.show_points:
            points_obj = PointsObj(self, conf.display.scale, self._state) 
            self.add_object(points_obj)
       

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
            done,pending = await asyncio.wait([draw_task, event_task], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
        except asyncio.exceptions.CancelledError as e:
            print(f"display canceled") 

        stop.set()
        event_loop_thread.join()
        draw_task.cancel()
        event_task.cancel()
        print(f"display closed") 


    def close(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))


    def event_loop(
            self,
            loop,
            event_queue: asyncio.Queue,
            ready: threading.Event,
            stop: threading.Event
        ):
        pygame.init() 
        try:
            pygame.display.set_caption("Tactile")
            self._screen = pygame.display.set_mode((int(self.width), int(self.height))) # screen have to be created in the thread where events are collected
            ready.set()
            while not stop.is_set():          
                event = pygame.event.wait(100) # check stop once a 0.1s
                if event.type != pygame.NOEVENT:
                    asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)
                # event = pygame.event.wait() # check stop once a 0.1s
                # asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)
                if event.type == pygame.QUIT:
                    break
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
            raise


    async def event_coroutine(self):
        try:
            while True:
                event: pygame.event.Event = await self._event_queue.get()
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.dict['pos']                    
                    self._state.add_point((pos[0]/self._scale, pos[1]/self._scale))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.dict['pos']                    
                    print(f"{pos[0]/self._scale}, {pos[1]/self._scale}")


                for obj in self._objects:
                    await obj.handle_event(event)

        except asyncio.exceptions.CancelledError as e:
            print(f"event_coroutine cancelled")
        except Exception as e:
            print(f"event_coroutine exception {str(e)}")
            raise


    def add_object(self, obj: DisplayObject):
        self._objects.append(obj)


app_display = Display()