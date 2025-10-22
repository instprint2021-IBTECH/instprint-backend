# server.py
from flask import Flask, request, jsonify
import os
import razorpay
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env in local dev
load_dotenv()

app = Flask(__name__)
CORS(app)  # allow cross-origin requests from your app during development

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")


if not (RAZORPAY_KEY_ID and RAZORPAY_SECRET):
    raise Exception("Set RAZORPAY_KEY_ID and RAZORPAY_SECRET environment variables")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "InstPrint backend running"}), 200

@app.route("/create_order", methods=["POST"])
def create_order():
    try:
        data = request.get_json() or {}
        # Expect amount in INR as integer (e.g., 100 for ₹100)
        amount_in_inr = int(data.get("amount", 0))
        if amount_in_inr <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        amount_paise = amount_in_inr * 100
        currency = "INR"
        receipt = data.get("receipt") or f"receipt_{data.get('userId','guest')}"
        # create order
        order = client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1
        })
        return jsonify({"order_id": order["id"], "key": RAZORPAY_KEY_ID}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: simple webhook endpoint (verify signature recommended)
@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify using razorpay webhook signature if you set one in dashboard (recommended)
    payload = request.get_data(as_text=True)
    signature = request.headers.get("X-Razorpay-Signature")
    # For full verification you need your webhook secret.
    # Keep it secure and verify here.
    print("Webhook received:", payload[:200])
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    # Local dev server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
