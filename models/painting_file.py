from pydantic import BaseModel
from . import common


class LidarConfig(BaseModel):
    x: int
    y: int


class AreaConfig(BaseModel):
    w: float
    h: float


class PaintingFile(BaseModel):
    
    music: common.MusicConfig    
    lidar: LidarConfig
    area: AreaConfig
    paintings: list[common.Painting]