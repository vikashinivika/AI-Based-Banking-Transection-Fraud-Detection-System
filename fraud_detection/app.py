from flask import Flask, render_template, request
from main import detect_fraud, generate_charts

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    result_text = None
    show_charts = False

    if request.method == "POST":
        # --- Get form input ---
        account = request.form["account"]
        amount = float(request.form["amount"])
        time = int(request.form["time"])
        location = request.form["location"]
        device = request.form["device"]
        txn_type = request.form["txn_type"]
        prev_fraud = int(request.form["prev_fraud"])

        # --- Detect fraud (account number included) ---
        result = detect_fraud(
            account,           # <-- account number passed here
            amount,
            time,
            location,
            device,
            txn_type,
            prev_fraud
        )

        # --- Generate charts ---
        generate_charts(result)

        # --- Result text ---
        result_text = "Fraud Transaction ❌" if result == 1 else "Normal Transaction ✅"
        show_charts = True

    return render_template("index.html", result=result_text, show_charts=show_charts)

if __name__ == "__main__":
    app.run(debug=True)

