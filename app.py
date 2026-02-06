from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "fca_live_iZokyqUoJbsY74k6fzJ2QodNX4EgzGHXQWknFclT"


@app.route("/", methods=["GET"])
def health():
    print("✅ GET health check hit", flush=True)
    return "OK", 200


@app.route("/", methods=["POST"])
def index():
    data = request.get_json()
    query_result = data.get("queryResult", {})

    action = query_result.get("action", "")
    parameters = query_result.get("parameters", {})
    fulfillment_text = query_result.get("fulfillmentText", "")

    # CASE 1: Currency conversion
    if (
        action == "currency.convert"
        and parameters.get("currency-from")
        and parameters.get("currency-to")
        and parameters.get("amount") is not None
    ):
        source_currency = parameters["currency-from"]
        target_currency = parameters["currency-to"]
        amount = float(parameters["amount"])

        try:
            rate = fetch_conversion_factor(source_currency, target_currency)
            final_amount = round(amount * rate, 2)
            print(f"({amount} {source_currency} is {final_amount} {target_currency})", flush=True)

            return jsonify({
                "fulfillmentText": f"{amount} {source_currency} is {final_amount} {target_currency}"
            })
        except Exception:
            return jsonify({
                "fulfillmentText": "Sorry, I couldn’t fetch the exchange rate right now."
            })

    # CASE 2: Small talk / fallback
    print(fulfillment_text, flush=True)
    return jsonify({"fulfillmentText": fulfillment_text})


def fetch_conversion_factor(source, target):
    url = "https://api.freecurrencyapi.com/v1/latest"
    params = {
        "apikey": API_KEY,
        "base_currency": source,
        "currencies": target
    }

    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return float(r.json()["data"][target])


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)