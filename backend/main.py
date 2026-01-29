from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status

import models
from auth import get_current_user, router
from database import engine
from dependencies import db_dependency

app = FastAPI()

app.include_router(router)

models.Base.metadata.create_all(bind=engine)

user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/", status_code=status.HTTP_200_OK)
async def root(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return {"user": user}
