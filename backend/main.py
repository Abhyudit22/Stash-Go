from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import eng , Base
from routes import product_routes
import models
from routes import sale_routes


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=eng)
    print(" Database tables verified and successfully created in Docker!")
    yield
    print("Application shutting down cleanly")

app = FastAPI(
    title = "Stash GO",
    version = "1.0.0",
    lifespan=lifespan
)

app.include_router(product_routes.router)
app.include_router(sale_routes.router)

@app.get("/")
def read_root():
    """ 
    testing the backend 

    """
    return{
        "status" : "online"
    }
# if __name__=="__main__":
#     main()
