from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Expense Splitter</title>

    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body {
            background: linear-gradient(to right, #667eea, #764ba2);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card {
            border-radius: 20px;
            padding: 20px;
            width: 500px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .result-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }
    </style>
</head>

<body>

<div class="card">
    <h3 class="text-center mb-3">💰 Expense Splitter</h3>

    <div class="mb-3">
        <label class="form-label">People</label>
        <input id="people" class="form-control" placeholder="Alice, Bob, Charlie">
    </div>

    <div>
        <label class="form-label">Expenses</label>
        <div id="expenses"></div>

        <button class="btn btn-sm btn-secondary mt-2" onclick="addExpense()">+ Add Expense</button>
    </div>

    <button class="btn btn-primary w-100 mt-3" onclick="calculate()">Split</button>

    <div class="result-box mt-3" id="result"></div>
</div>

<script>
function addExpense() {
    const div = document.createElement("div");
    div.className = "d-flex gap-2 mt-2";

    div.innerHTML = `
        <input class="form-control name" placeholder="Name">
        <input class="form-control amount" type="number" placeholder="Amount">
        <button class="btn btn-danger" onclick="this.parentElement.remove()">X</button>
    `;

    document.getElementById("expenses").appendChild(div);
}

// Add one default row
addExpense();

function calculate() {
    const people = document.getElementById("people").value
        .split(",")
        .map(p => p.trim())
        .filter(p => p);

    const expenseDivs = document.querySelectorAll("#expenses > div");
    let expenses = [];

    expenseDivs.forEach(div => {
        const name = div.querySelector(".name").value.trim();
        const amount = parseFloat(div.querySelector(".amount").value);

        if (name && !isNaN(amount)) {
            expenses.push({ paid_by: name, amount: amount });
        }
    });

    fetch("/split", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ people, expenses })
    })
    .then(res => res.json())
    .then(data => displayResult(data))
    .catch(() => {
        document.getElementById("result").innerHTML =
            "<div class='text-danger'>Something went wrong</div>";
    });
}

function displayResult(data) {
    let html = "<h5>Balances</h5>";

    const balances = data.balances || data;

    for (let person in balances) {
        let value = balances[person];

        if (value > 0) {
            html += `<div class="text-success">🟢 ${person} gets ${value.toFixed(2)}</div>`;
        } else if (value < 0) {
            html += `<div class="text-danger">🔴 ${person} owes ${Math.abs(value).toFixed(2)}</div>`;
        } else {
            html += `<div>⚪ ${person} is settled</div>`;
        }
    }

    if (data.transactions && data.transactions.length > 0) {
        html += "<hr><h5>Transactions</h5>";
        data.transactions.forEach(t => {
            html += `<div>💸 ${t.from} → ${t.to}: ${t.amount}</div>`;
        });
    }

    document.getElementById("result").innerHTML = html;
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api")
def api_status():
    return "API is working!"


@app.route("/split", methods=["POST"])
def split():
    data = request.json

    people = data.get("people", [])
    expenses = data.get("expenses", [])

    if not people:
        return jsonify({"error": "No people provided"}), 400

    total = sum(exp.get("amount", 0) for exp in expenses)
    share = total / len(people)

    balances = {person: 0 for person in people}

    for exp in expenses:
        balances[exp.get("paid_by")] += exp.get("amount", 0)

    for person in balances:
        balances[person] -= share

    # Transactions logic
    debtors = []
    creditors = []

    for person, balance in balances.items():
        if balance < 0:
            debtors.append([person, -balance])
        elif balance > 0:
            creditors.append([person, balance])

    transactions = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        amount = min(debt, credit)

        transactions.append({
            "from": debtor,
            "to": creditor,
            "amount": round(amount, 2)
        })

        debtors[i][1] -= amount
        creditors[j][1] -= amount

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return jsonify({
        "balances": balances,
        "transactions": transactions
    })


if __name__ == "__main__":
    app.run(debug=True)