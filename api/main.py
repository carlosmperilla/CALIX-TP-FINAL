from fastapi import FastAPI

from .country.models import Base
from .province.models import Base
from .procedure.models import Base

from .database import engine

from .country.views import router as country_router
from .province.views import router as province_router
from .procedure.views import router as procedure_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API Transferencia de Autos",
    description="Una API con tramites de autos, sus provincias y países.",
    version="1.0"
)

app.include_router(country_router)
app.include_router(province_router)
app.include_router(procedure_router)