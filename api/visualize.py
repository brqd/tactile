import fastapi
from models import common
from state import app_state

router = fastapi.routing.APIRouter(prefix="/visualize")


@router.get("/point")
async def list_points() -> list[common.Point]:
    return app_state.get_points()


@router.get("/area_states")
async def list_area_states() -> list[common.AreaState]:
    return app_state.get_areas_states()