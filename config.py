from pydantic import BaseModel, Field


class Rect(BaseModel):
    x: int
    y: int
    w: int
    h: int
    

class Value(BaseModel):
    value: float
    rect: Rect


class Param(BaseModel):
    id: str
    values: list[Value]


class Painting(BaseModel):
    image_file: str
    x: float
    y: float
    w: float
    h: float

class Lidar(BaseModel):
    port: str
    x: int
    y: int

class Area(BaseModel):
    w: float
    h: float


class Config(BaseModel):
    bank_file: str
    bank_string_file: str
    fmod_event: str
    bank_params: list[Param]
    display_scale: float
    area: Area
    lidar: Lidar      
    paintings: list[Painting]

    display: bool = True
    display_paintings: bool = False
    display_points: bool = True    
    display_areas: bool = True 
    
    




