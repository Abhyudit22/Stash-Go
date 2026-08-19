from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from utils.auth import get_current_user
from models import User_Auth, Product
from schemas import (
    ChatRequest, ChatResponse, SearchResult, ForecastResponse,
    RecommendationItem, InsightsResponse, InsightItem
)
from ai.chat_query import process_chat_query
from ai.search import search_engine
from ai.forecasting import get_sales_forecast, get_product_forecast
from ai.recommendations import get_recommendations
from ai.insights import get_all_insights

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    res = process_chat_query(request.question, db, current_user.id)
    return res

@router.get("/search", response_model=list[SearchResult])
def search_products(q: str, limit: int = 10, db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    results = search_engine.search(q, products, top_k=limit)
    return results

@router.get("/forecast", response_model=ForecastResponse)
def forecast_sales(days: int = 7, db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    forecast, model_type, data_points = get_sales_forecast(db, current_user.id, days)
    return {
        "forecast": forecast,
        "model_type": model_type,
        "data_points_used": data_points
    }

@router.get("/forecast/{product_id}", response_model=ForecastResponse)
def forecast_product(product_id: int, days: int = 30, db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    forecast, model_type, data_points = get_product_forecast(db, current_user.id, product_id, days)
    return {
        "forecast": forecast,
        "model_type": model_type,
        "data_points_used": data_points
    }

@router.get("/recommendations/{product_id}", response_model=list[RecommendationItem])
def get_product_recommendations(product_id: int, limit: int = 5, db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    results = get_recommendations(db, current_user.id, product_id, limit)
    return results

@router.get("/insights", response_model=InsightsResponse)
def get_insights(db: Session = Depends(get_db), current_user: User_Auth = Depends(get_current_user)):
    insights_data = get_all_insights(db, current_user.id)
    return {
        "insights": insights_data,
        "generated_at": datetime.now()
    }
