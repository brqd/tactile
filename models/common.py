from pydantic import BaseModel


class Rect(BaseModel):
    x: int
    y: int
    w: int
    h: int


class Area(BaseModel):

    param_id: str
    param_value: float
    rect: Rect

class AreaState(Area):
    state: bool

    
class Point(BaseModel):

    pos: tuple[float,float] = (0,0)
    color: tuple[int,int,int] = (0,0,0)


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


class MusicConfig(BaseModel):
    bank_file: str
    bank_string_file: str
    fmod_event: str
    bank_params: list[Param]
