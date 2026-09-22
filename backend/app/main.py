from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, family, categories, transactions, budget, analytics
from app.db.session import engine, Base
from app.models.user import User
from app.models.family import Family
from app.models.category import Category
from app.models.transaction import Transaction

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Family Budget API",
    description="API для автоматизированной системы управления семейным бюджетом",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(family.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(budget.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
