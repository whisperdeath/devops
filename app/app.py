from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API is working!**** "


@app.route("/split", methods=["POST"])
def split():
    data = request.json

    people = data["people"]
    expenses = data["expenses"]

    total = sum(exp["amount"] for exp in expenses)
    share = total / len(people)

    balances = {person: 0 for person in people}

    for exp in expenses:
        balances[exp["paid_by"]] += exp["amount"]

    for person in balances:
        balances[person] -= share

    return jsonify(balances)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

