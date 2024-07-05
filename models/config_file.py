from typing import Optional
from pydantic import BaseModel

class LidarConfig(BaseModel):
    serial: str


class ApiConfig(BaseModel):
    port: int


class DisplayConfig(BaseModel):
    scale: float
    show_paintings: bool = False
    show_points: bool = True    
    show_areas: bool = True 


class ConfigFile(BaseModel):

    enable_display: bool = False
    enable_lidar: bool = True
    enable_sound: bool = True
    enable_api: bool = True    

    picture_conf: str

    lidar: LidarConfig
    api: ApiConfig
    display: DisplayConfig



        


    



