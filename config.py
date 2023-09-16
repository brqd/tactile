from pydantic import BaseModel, Field


class Spot(BaseModel):
    x: int
    y: int
    

class Value(BaseModel):
    value: float
    spots: list[Spot]


class Param(BaseModel):
    id: str
    values: list[Value]


class Painting(BaseModel):
    image_file: str
    x: float
    y: float
    width: float
    height: float

class Lidar(BaseModel):
    x: int
    y: int


class Config(BaseModel):
    bank_file: str
    bank_string_file: str
    fmod_event: str
    bank_params: list[Param]
    display_scale: float
    area_width: float
    area_height: float
    paintings: list[Painting]
    lidar: Lidar      




