import numpy as np
import asyncio
import config
import os
import pyfmodex
import pyfmodex.studio

import state

class Sound:

    def __init__(self, config: config.Config, st: state.State):

        self._state = st
        bank_file = os.path.join(os.path.dirname(__file__), config.bank_file)
        bank_strings_file = os.path.join(os.path.dirname(__file__), config.bank_string_file)
        self._fmod_system = pyfmodex.studio.StudioSystem()
        self._fmod_system.initialize()
        self._fmod_system.load_bank_file(bank_file)
        self._fmod_system.load_bank_file(bank_strings_file)
        self._fmod_event = self._fmod_system.get_event(f"event:{config.fmod_event}")
        self._fmod_instance = self._fmod_event.create_instance()
        self._fmod_instance.start()
        self._fmod_system.update()                

    async def run(self):
        try:
            while True:
                param_id = self._state.current_area.param_id
                param_value = self._state.current_area.param_value
                self._fmod_instance.set_parameter_by_name(param_id, param_value)
                self._fmod_system.update()
                await asyncio.sleep(1)
        finally:
            self._fmod_system.release() 