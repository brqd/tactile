from typing import Iterator
import asyncio
import pydantic
import models
import numpy as np

picture_path = ""

class State:


    def __init__(self):

        self._points_count = 1000 # fix by now
        self._points_index = 0        
        self._current_area: models.Area | None = None
        self._current_area_valid: bool = True
        self._areas_limits: np.ndarray = np.zeros((0,4))
        self._areas_sizes: np.ndarray = np.zeros((0,1))
        self._areas: list[models.Area] = [] 

        # filling up points
        self._points: list[models.Point] = []
        self._points_array: np.array = np.zeros((0,2))
        for i in range(self._points_count):
            self._points.append(models.Point(pos=(0,0), color=(0,0,0)))
            self._points_array = np.vstack([
                self._points_array,
                [0,0]
            ])
        self._points_areas = None


    def configure(self, painting_conf: models.PaintingFile):

        # filling up areas                    
        for param in painting_conf.music.bank_params: 
            for value in param.values:
                area = models.Area(
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
        self._points_areas = np.ones((len(self._points), len(self._areas)), dtype=bool)


    def get_current_area(self) -> models.Area | None:
        if not self._current_area_valid:                
            # calculate current area if neede
            areas_count = np.sum(self._points_areas,0)
            area_index = np.argmax(areas_count.T / self._areas_sizes.T) 
            self._current_area = self._areas[area_index]
            self._current_area_valid = True

        return self._current_area


    def get_points(self) -> list[models.Point] :
        return self._points
    

    def get_areas_states(self) -> list[models.AreaState]:
        current = self.get_current_area()
        return [
            models.AreaState.model_validate(a.model_dump() | {"state": a is current})
            for a in self._areas
        ]


    def add_point(self, pos: tuple[float, float], color: tuple[int, int, int] = (255,255,255)):

        if self._points_areas is not None:
            self._points_index += 1
            if self._points_index == self._points_count:
                self._points_index = 0

            # points for display        
            self._points[self._points_index] = models.Point(pos=pos, color=color) 

            # find areas the point belong to
            p = pos
            a = self._areas_limits
            self._points_areas[self._points_index] = (a[:,0] < p[0]) & (p[0] < a[:,2]) & (a[:,1] < p[1]) & (p[1] < a[:,3])

            # invalidate current area for lazy calculation
            self._current_area_valid = False


app_state = State()