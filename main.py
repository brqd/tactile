import asyncio
import traceback
import yaml
import numpy as np
import os

import models
import state
from state import app_state

  
async def main():

    path = "configs/2024"

    with open("config.yaml") as f:
        config_dict = yaml.load(f, yaml.Loader)
    conf = models.ConfigFile.model_validate(config_dict)

    state.picture_path = os.path.abspath(conf.picture_path)

    with open(os.path.join(state.picture_path, "painting.yaml")) as f:
        painting_dict = yaml.load(f, yaml.Loader)
    painting = models.PaintingFile.model_validate(painting_dict)    

    # state = State(conf)

    tasks: list[asyncio.Task] = []

    state.app_state.configure(painting)

    if conf.enable_lidar:   
        from lidar import app_lidar
        app_lidar.configure(conf, painting)
        tasks.append(asyncio.create_task(app_lidar.run()))
    if conf.enable_display:
        from display import app_display
        app_display.configure(painting)
        tasks.append(asyncio.create_task(app_display.run()))
    if conf.enable_sound:
        from sound import app_sound
        app_sound.configure(painting)
        tasks.append(asyncio.create_task(app_sound.run()))
    if conf.enable_api:
        from api import app_api
        app_api.configure(conf, painting)
        tasks.append(asyncio.create_task(app_api.run()))        

    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        for task in done:
            task.result()        
    except asyncio.exceptions.CancelledError as e:
        print(f"quit!") 
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BaseException as e:
        traceback.print_exception(type(e), e, e.__traceback__)