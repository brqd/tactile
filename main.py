import asyncio
import traceback
import yaml
import numpy as np

import config
from state import State
from sound import Sound
from display import Display
from lidar import Lidar


  
async def main():

    with open("config.yaml") as f:
        config_dict = yaml.load(f, yaml.Loader)
    conf = config.Config.model_validate(config_dict)

    state = State(conf)
    lidar = Lidar(conf, state)
    display = Display(conf, state)
    sound = Sound(conf, state)

    tasks: list[asyncio.Task] = [
        asyncio.create_task(display.run()),
        asyncio.create_task(sound.run()),
        asyncio.create_task(lidar.run()),
    ]
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