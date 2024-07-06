import logging
import asyncio
import fastapi
import uvicorn
import models
from . import config
from . import visualize

_logger = logging.getLogger('api')

class AppApi(fastapi.FastAPI):
    
    def configure(self, conf: models.ConfigFile, painting: models.PaintingFile):
        ...

    async def run(self):
        # uvicorn.run(self)

        config = uvicorn.Config(self, host="0.0.0.0", port=18000, lifespan="on")
        server = uvicorn.Server(config=config)
        try:
            await(server.serve())
        except asyncio.CancelledError:
            print(f"api canceled")
            await server.shutdown()              
        finally:
            print(f"api closed")           


app_api = AppApi()
app_api.include_router(config.router)
app_api.include_router(visualize.router)

