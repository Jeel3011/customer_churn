from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io

from src.pipeline.predict_pipeline import PredictPipeline
from src.analytics.kpi import ChurnKPI
from api.schemas import CustomerInput

app = FastAPI(
    title="Customer Churn Prediction API",
    description="ML-powered churn prediction service",
    version="1.0.0"
)

predict_pipeline = PredictPipeline()


@app.get("/health")
def health_check():
    return {"status": "OK", "message": "Churn model is ready"}


@app.post("/predict")
def predict_single_customer(customer: CustomerInput):
    df = pd.DataFrame([customer.dict()])

    predictions = predict_pipeline.predict(df)

    row = predictions.iloc[0]
    return {
        "customer_id": int(row["customer_id"]),
        "churn_probability": float(round(row["churn_probability"], 4)),
        "risk_level": str(row["risk_level"])
    }

@app.post("/predict_csv")
def predict_csv(file: UploadFile = File(...)):
    print("🔥 /predict_csv endpoint was HIT")

    contents = file.file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    predictions = predict_pipeline.predict(df)

    kpi = ChurnKPI(predictions)
    results = kpi.compute_kpis()

    return {
    "kpis": {
        "total_customers": int(results["total_customers"]),
        "high_risk_customers": int(results["high_risk_customers"]),
        "medium_risk_customers": int(results["medium_risk_customers"]),
        "low_risk_customers": int(results["low_risk_customers"]),
        "average_churn_probability": float(results["average_churn_probability"])
    },
    "predictions": [
        {
            "customer_id": int(row["customer_id"]),
            "churn_probability": float(row["churn_probability"]),
            "risk_level": str(row["risk_level"])
        }
        for _, row in predictions.iterrows()
    ]
}

