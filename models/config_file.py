from typing import Optional
from pydantic import BaseModel

class LidarConfig(BaseModel):
    serial: str


class ApiConfig(BaseModel):
    port: int


class DisplayConfig(BaseModel):
    display_scale: float
    display_paintings: bool = False
    display_points: bool = True    
    display_areas: bool = True 


class ConfigFile(BaseModel):

    enable_display: bool = False
    enable_lidar: bool = True
    enable_sound: bool = True
    enable_api: bool = True    

    picture_path: str

    lidar_config: LidarConfig
    api_config: ApiConfig
    display_config: DisplayConfig



        


    



