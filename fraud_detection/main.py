import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Path to dataset
DATASET_FILE = "fraud_dataset_upload.xlsx"

# Load dataset if exists
columns = ['Account Number','Amount','Time','Location','Device','Transaction Type','Previous Fraud','Is Fraud']

if os.path.exists(DATASET_FILE):
    df = pd.read_excel(DATASET_FILE)
else:
    df = pd.DataFrame(columns=columns)

# Train ML model if dataset has data
if not df.empty:
    le_location = LabelEncoder()
    le_device = LabelEncoder()
    le_txn_type = LabelEncoder()

    df['Location_code'] = le_location.fit_transform(df['Location'])
    df['Device_code'] = le_device.fit_transform(df['Device'])
    df['TxnType_code'] = le_txn_type.fit_transform(df['Transaction Type'])

    X = df[['Amount','Time','Location_code','Device_code','TxnType_code','Previous Fraud']]
    y = df['Is Fraud']

    model = RandomForestClassifier()
    model.fit(X, y)
else:
    le_location = le_device = le_txn_type = None
    model = None

# ----------------- Save user input automatically -----------------
def save_user_input(account, amount, time, location, device, txn_type, prev_fraud, result):
    # Load existing dataset
    if os.path.exists(DATASET_FILE):
        df_existing = pd.read_excel(DATASET_FILE)
    else:
        df_existing = pd.DataFrame(columns=columns)
    
    # Create new row as DataFrame
    new_row = pd.DataFrame([{
        'Account Number': account,   # <-- exact match
        'Amount': amount,
        'Time': time,
        'Location': location,
        'Device': device,
        'Transaction Type': txn_type,
        'Previous Fraud': prev_fraud,
        'Is Fraud': result
    }])

    # Concatenate
    df_existing = pd.concat([df_existing, new_row], ignore_index=True)

    # Save back to Excel
    df_existing.to_excel(DATASET_FILE, index=False)

# ----------------- Detect Fraud -----------------
def detect_fraud(account, amount, time, location, device, txn_type, prev_fraud):
    # Rule-based detection
    rules_fraud = 0
    if amount > 10000 and (time < 6 or time > 22) and location.lower() != "chennai":
        rules_fraud = 1

    # ML prediction
    ml_pred = 0
    if model is not None:
        loc_code = le_location.transform([location])[0] if location in le_location.classes_ else 0
        device_code = le_device.transform([device])[0] if device in le_device.classes_ else 0
        txn_code = le_txn_type.transform([txn_type])[0] if txn_type in le_txn_type.classes_ else 0
        ml_pred = model.predict([[amount, time, loc_code, device_code, txn_code, prev_fraud]])[0]

    final_result = 1 if rules_fraud == 1 or ml_pred == 1 else 0

    # Save user input including account number
    save_user_input(account, amount, time, location, device, txn_type, prev_fraud, final_result)

    return final_result

# ----------------- Generate Charts -----------------
def generate_charts(result):
    os.makedirs("static", exist_ok=True)

    labels = ['Normal','Fraud']
    values = [0,0]
    values[result] = 1
    colors = ['green','red']

    # Bar chart
    plt.figure()
    plt.bar(labels, values, color=colors)
    plt.title("Transaction Result (Bar Chart)")
    plt.savefig("static/bar_chart.png")
    plt.close()

    # Line chart
    plt.figure()
    plt.plot(['Transaction'], [result], marker='o')
    plt.yticks([0,1], ['Normal','Fraud'])
    plt.title("Transaction Status (Line Chart)")
    plt.savefig("static/line_chart.png")
    plt.close()

    # Pie chart
    plt.figure()
    plt.pie([1-result, result], labels=['Normal','Fraud'], colors=['green','red'], autopct='%1.1f%%')
    plt.title("Fraud Percentage")
    plt.savefig("static/pie_chart.png")
    plt.close()

