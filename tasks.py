from celery import Celery
from datetime import datetime

celery = Celery(
    "flask_app",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

@celery.task
def check_data():
    print(f"🔍 Checking data at {datetime.utcnow()}")
    data_available = True  

    if data_available:
        print("✅ Data found!")
    else:
        print("❌ No data found yet.")