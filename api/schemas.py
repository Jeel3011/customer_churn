from pydantic import BaseModel
from typing import List


class CustomerInput(BaseModel):
    customer_id: int
    tenure_months: int
    monthly_usage: float
    subscription_plan: str
    monthly_revenue: float
    support_tickets: int
    last_login_days: int
    payment_delay: int


class PredictionResponse(BaseModel):
    customer_id: int
    churn_probability: float
    risk_level: str


class BulkPredictionResponse(BaseModel):
    total_customers: int
    high_risk_customers: int
    medium_risk_customers: int
    low_risk_customers: int
