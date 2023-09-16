import asyncio
import traceback
import config
import yaml
import sound
import display
import lidar

pos_queue = asyncio.Queue()


async def configure():
    with open("config.yaml") as f:
        config_dict = yaml.load(f, yaml.Loader)
    conf = config.Config.model_validate(config_dict)
    await sound.configure(conf)
    await display.configure(conf, pos_queue)
    await lidar.configure(conf, pos_queue, display.points)


async def dispatch_pos():
    try:
        while True:
            pos: tuple[float, float] = await pos_queue.get()
            sound.update(pos)
            display.update(pos)

    except asyncio.exceptions.CancelledError as e:
        print(f"dispatch_pos cancelled")
    except Exception as e:
        print(f"dispatch_pos exception {str(e)}")   


async def main():

    await configure()

    tasks = [
        asyncio.create_task(display.run()),
        asyncio.create_task(sound.run()),
        asyncio.create_task(lidar.run()),
        asyncio.create_task(dispatch_pos())
    ]

    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except asyncio.exceptions.CancelledError as e:
        print(f"quit!") 
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)

    for task in tasks:
        if task.done():
            try:
                task.result()
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BaseException as e:
        traceback.print_exception(type(e), e, e.__traceback__)