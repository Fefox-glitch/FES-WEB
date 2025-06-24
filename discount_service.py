from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Example list of valid discount codes
valid_discount_codes = {
    "SAVE5": 5,
    "SAVE10": 10,
    "MEMBER5": 5,
    "MEMBER10": 10
}

MIN_PURCHASE_AMOUNT = 20000

@app.route('/apply-discount', methods=['POST'])
def apply_discount():
    data = request.json
    email = data.get('email')
    purchase_amount = data.get('purchase_amount')
    discount_code = data.get('discount_code', None)

    if not email or purchase_amount is None:
        return jsonify({"error": "Email and purchase_amount are required"}), 400

    discount_percentage = 0

    # Check if purchase amount qualifies for discount
    if purchase_amount >= MIN_PURCHASE_AMOUNT:
        # Randomly assign discount between 5% and 10%
        discount_percentage = random.choice([5, 10])

    # Check if discount code is valid and overrides discount_percentage if higher
    if discount_code:
        code_discount = valid_discount_codes.get(discount_code.upper())
        if code_discount:
            discount_percentage = max(discount_percentage, code_discount)
        else:
            return jsonify({"error": "Invalid discount code"}), 400

    if discount_percentage == 0:
        return jsonify({"message": "No discount applicable", "final_amount": purchase_amount})

    discount_amount = purchase_amount * discount_percentage / 100
    final_amount = purchase_amount - discount_amount

    return jsonify({
        "message": f"Discount of {discount_percentage}% applied",
        "discount_percentage": discount_percentage,
        "discount_amount": discount_amount,
        "final_amount": final_amount
    })

if __name__ == '__main__':
    app.run(debug=True)
