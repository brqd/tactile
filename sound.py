import numpy as np
import asyncio
import config
import os
import time
import pyfmodex
import pyfmodex.studio

_bank_params: list[config.Param]
_fmod_instance = None
_fmod_event = None
_fmod_system = None

# consistent list o f spots and param values
_param_values: dict[str, int] = {}
_param_spots: dict[str, np.ndarray] = {}


async def configure(config: config.Config):
    global _bank_params, _fmod_instance, _fmod_system, _param_spots

    _bank_params = config.bank_params
    for param in _bank_params:
        _param_values[param.id] = []
        _param_spots[param.id] = np.empty([0,2])
        for value in param.values:
            for spot in value.spots:
                _param_values[param.id].append(value.value)
                _param_spots[param.id] = np.vstack((_param_spots[param.id], [spot.x, spot.y]))

    BANK_FILE = os.path.join(os.path.dirname(__file__), config.bank_file)
    BANK_STRINGS_FILE = os.path.join(os.path.dirname(__file__), config.bank_string_file)
    _fmod_system = pyfmodex.studio.StudioSystem()
    _fmod_system.initialize()
    conf_dir = os.path.dirname(__file__)
    _fmod_system.load_bank_file(BANK_FILE)
    _fmod_system.load_bank_file(BANK_STRINGS_FILE)
    _fmod_event = _fmod_system.get_event(f"event:{config.fmod_event}")
    _fmod_instance = _fmod_event.create_instance()
    _fmod_instance.start()
    _fmod_system.update()                

async def run():
    try:
        while True:
            await asyncio.sleep(100)
    finally:
        _fmod_system.release()

_last = 0

def update(pos: tuple[float,float]):
    global _last
    x,y = pos

    for param in _bank_params:
        spots = _param_spots[param.id]        
        dx = _param_spots[param.id][:,0]-x
        dy = _param_spots[param.id][:,1]-y
        distance = dx*dx + dy*dy
        value = _param_values[param.id][np.argmin(distance)]
        if _last != value:
            print(value)
        _last = value
        _fmod_instance.set_parameter_by_name(param.id, value)
        _fmod_system.update()