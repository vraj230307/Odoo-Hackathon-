from flask import Blueprint, jsonify, request
import sqlite3
import os

budget_bp = Blueprint('budget', __name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@budget_bp.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        trip_id = request.args.get('trip_id')
        conn = get_db()
        cursor = conn.cursor()

        if trip_id:
            cursor.execute("SELECT * FROM expenses WHERE trip_id = ?", [trip_id])
        else:
            cursor.execute("SELECT * FROM expenses")

        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()

        total = sum(e['amount'] for e in expenses)

        return jsonify({"success": True, "message": "Expenses fetched.", "data": {"expenses": expenses, "total": total}}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500


@budget_bp.route('/expenses', methods=['POST'])
def add_expense():
    try:
        data        = request.get_json()
        trip_id     = data.get('trip_id')
        category    = data.get('category')
        description = data.get('description')
        amount      = data.get('amount')
        date        = data.get('expense_date')

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (trip_id, category, description, amount, expense_date) VALUES (?,?,?,?,?)",
            [trip_id, category, description, amount, date]
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Expense added.", "data": []}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500


@budget_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM expenses WHERE id = ?", [expense_id])
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Expense deleted.", "data": []}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500