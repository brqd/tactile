import numpy as np
import asyncio
from  models import painting_file
import os
import pyfmodex
import pyfmodex.studio

import state
from state import app_state

class Sound:

    def __init__(self):
        self._fmod_system = pyfmodex.studio.StudioSystem()
        self._fmod_instance = None

    def configure(self, config: painting_file.PaintingFile):

        self._state = app_state
        bank_file = os.path.join(state.picture_path, config.music.bank_file)
        bank_strings_file = os.path.join(state.picture_path, config.music.bank_string_file)        
        self._fmod_system.initialize()
        self._fmod_system.load_bank_file(bank_file)
        self._fmod_system.load_bank_file(bank_strings_file)
        self._fmod_event = self._fmod_system.get_event(f"event:{config.music.fmod_event}")
        self._fmod_instance = self._fmod_event.create_instance()
        self._fmod_instance.start()
        self._fmod_system.update()     
           
        
    def __del__(self):
        if self._fmod_instance is not None:
            self._fmod_instance.stop()
        self._fmod_system.release() 


    async def run(self):
        while True:
            current_area = self._state.get_current_area()
            if current_area is not None:
                param_id = current_area.param_id
                param_value = current_area.param_value
                self._fmod_instance.set_parameter_by_name(param_id, param_value)
                self._fmod_system.update()
            await asyncio.sleep(1)
        


app_sound = Sound()            