import fastapi
import uvicorn
import models
from . import config
from . import visualize

class AppApi(fastapi.FastAPI):
    
    def configure(self, conf: models.ConfigFile, painting: models.PaintingFile):
        ...


    async def run(self):
        # uvicorn.run(self)
        config = uvicorn.Config(self, port=18000)
        server = uvicorn.Server(config=config)
        await server.serve()


app_api = AppApi()
app_api.include_router(config.router)
app_api.include_router(visualize.router)
