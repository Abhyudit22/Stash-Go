from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import eng , Base
import models
from routes import product_routes, sale_routes, analytics_routes, return_routes, bill_routes, auth_routes ,report_routes
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.drop_all(bind=eng)
    # print("Database wiped clean automatically!")

    Base.metadata.create_all(bind=eng)
    print("Database tables verified and successfully created in Docker!")
    
    yield
    print("Application shutting down cleanly")

app = FastAPI(
    title="Stash GO",
    version="1.0.0",
    lifespan=lifespan,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(product_routes.router)
app.include_router(sale_routes.router)
app.include_router(analytics_routes.router)
app.include_router(return_routes.router)
app.include_router(bill_routes.router)
app.include_router(auth_routes.router)
app.include_router(report_routes.router)
@app.get("/")
def read_root():
    """ 
    testing the backend 
    """
    return {
        "status" : "online"
    }     