from backend import models  # noqa: F401
from backend.database import Base, engine

Base.metadata.create_all(engine)
