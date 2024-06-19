from typing import Iterator
import asyncio
import pydantic
import config
import numpy as np


class Area(pydantic.BaseModel):

    param_id: str
    param_value: float
    rect: config.Rect

    
class Point(pydantic.BaseModel):

    pos: tuple[float,float] = (0,0)
    color: tuple[int,int,int] = (0,0,0)
        

class State:

    _points_count = 1000 # fixed by now
    _points_index = 0
    _points_areas = None
    _current_area: Area = None
    _current_area_valid: bool = False

    def __init__(self, conf: config.Config):

        self._areas_limits: np.array = np.zeros((0,4))
        self._areas_sizes:  np.array = np.zeros((0,1))
        


        # filling up areas
        self._areas: list[Area] = []             
        for param in conf.bank_params: 
            for value in param.values:
                area = Area(
                    param_id = param.id,
                    param_value = value.value,
                    rect = value.rect
                )
                self._areas.append(area)

                self._areas_limits = np.vstack([
                    self._areas_limits,
                    [
                        value.rect.x,
                        value.rect.y,
                        value.rect.x + value.rect.w,
                        value.rect.y + value.rect.h,
                    ]
                ])

                self._areas_sizes = np.vstack([
                    self._areas_sizes,
                    [value.rect.w * value.rect.h]
                ])                

        # filling up points
        self._points: list[Point] = []
        self._points_array: np.array = np.zeros((0,2))
        for i in range(self._points_count):
            self._points.append(Point(pos=(0,0), color=(0,0,0)))
            self._points_array = np.vstack([
                self._points_array,
                [0,0]
            ])


        self._points_areas = np.ones((len(self._points), len(self._areas)), dtype=bool)


    def get_current_area(self):
        if not self._current_area_valid:                
            # calculate current area if neede
            areas_count = np.sum(self._points_areas,0)
            area_index = np.argmax(areas_count.T / self._areas_sizes.T) 
            self._current_area = self._areas[area_index]
            self._current_area_valid = True

        return self._current_area


    def get_points(self) -> list[Point] :
        return self._points


    def add_point(self, pos: tuple[float, float], color: tuple[int, int, int] = (255,255,255)):

        self._points_index += 1
        if self._points_index == self._points_count:
            self._points_index = 0

        # points for display        
        self._points[self._points_index] = Point(pos=pos, color=color) 

        # find areas the point belong to
        p = pos
        a = self._areas_limits
        self._points_areas[self._points_index] = (a[:,0] < p[0]) & (p[0] < a[:,2]) & (a[:,1] < p[1]) & (p[1] < a[:,3])

        # invalidate current area for lazy calculation
        self._current_area_valid = False