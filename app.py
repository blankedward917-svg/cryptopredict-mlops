from flask import Flask, jsonify
from datetime import datetime, timedelta
from tasks import check_data

app = Flask(__name__)

@app.route("/schedule-check")
def schedule_check():
    result = check_data.apply_async(
        eta=datetime.utcnow() + timedelta(minutes=1)
    )
    return jsonify({"task_id": result.id, "status": "scheduled for 1 min later"})

if __name__ == "__main__":
    app.run(debug=True)