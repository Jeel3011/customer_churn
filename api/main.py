from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io
import os
import boto3
from datetime import datetime

from src.pipeline.predict_pipeline import PredictPipeline
from src.analytics.kpi import ChurnKPI
from api.schemas import CustomerInput

# AWS S3 Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
USE_S3 = S3_BUCKET is not None

if USE_S3:
    s3_client = boto3.client('s3', region_name=AWS_REGION)

app = FastAPI(
    title="Customer Churn Prediction API",
    description="ML-powered churn prediction service",
    version="1.0.0"
)

predict_pipeline = PredictPipeline()


@app.get("/health")
def health_check():
    s3_status = "connected" if USE_S3 else "disabled"
    return {
        "status": "OK",
        "message": "Churn model is ready",
        "s3": s3_status
    }


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

    # Save predictions to S3 if enabled
    s3_file_key = None
    if USE_S3:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_file_key = f"predictions/{timestamp}_{file.filename}"
            
            # Convert predictions to CSV
            csv_buffer = io.StringIO()
            predictions.to_csv(csv_buffer, index=False)
            
            # Upload to S3
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_file_key,
                Body=csv_buffer.getvalue()
            )
            print(f"✅ Predictions saved to S3: {s3_file_key}")
        except Exception as e:
            print(f"⚠️ S3 upload failed: {str(e)}")

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
        ],
        "s3_file": s3_file_key
    }

