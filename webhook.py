import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Stripe API keys from environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

@app.route('/')
def home():
    return "Stripe Webhook is running!", 200

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle Stripe event
    if event['type'] == 'payment_intent.succeeded':
        print("✅ Payment succeeded!")
    elif event['type'] == 'payment_intent.payment_failed':
        print("❌ Payment failed.")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)

cristofani@cristofani-HP-EliteBook-840-G1:~/my
