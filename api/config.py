import fastapi
import fastapi.responses

router = fastapi.APIRouter(prefix="/config")


@router.get("/")
async def list_paintings():
    return {"message": "Hello World"}


@router.get("/{id}")
async def get_painting():
    return {"message": "Hello World"}


@router.get(
    "/{id}/img",
    responses = {
        200: {
            "content": {"image/png": {}}
        }
    },    
)
async def get_painting_image(id: str):
    return fastapi.responses.FileResponse(content=f"images/{id}", media_type="image/png")


@router.post(
    "/{id}/img"
)
def upload(file: fastapi.UploadFile):
    try:
        with open(file.filename, 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}