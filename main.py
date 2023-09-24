import asyncio
import traceback
import yaml
import numpy as np

import config
from state import State

  
async def main():

    with open("config.yaml") as f:
        config_dict = yaml.load(f, yaml.Loader)
    conf = config.Config.model_validate(config_dict)

    state = State(conf)

    tasks: list[asyncio.Task] = []

    if conf.enable_lidar:
        from lidar import Lidar
        lidar = Lidar(conf, state)
        tasks.append(asyncio.create_task(lidar.run()))
    if conf.enable_display:
        from display import Display
        display = Display(conf, state)
        tasks.append(asyncio.create_task(display.run()))
    if conf.enable_sound:
        from sound import Sound
        sound = Sound(conf, state)
        tasks.append(asyncio.create_task(sound.run()))

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