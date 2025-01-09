from flask import Blueprint, jsonify, request
from src.db_connection import get_connection

customers_blueprint = Blueprint('customers', __name__)

@customers_blueprint.route('/', methods=['GET'])
def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Customer")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()

@customers_blueprint.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
        row = cursor.fetchone()
        if row:
            return jsonify(row), 200
        else:
            return jsonify({'error': 'Customer not found'}), 404
    finally:
        cursor.close()
        conn.close()

@customers_blueprint.route('/', methods=['POST'])
def create_customer():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    reward_points = data.get('reward_points', 0)
    phone_number = data.get('phone_number')
    email = data.get('email')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO Customer (first_name, last_name, reward_points, phone_number, email)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (first_name, last_name, reward_points, phone_number, email))
        conn.commit()
        return jsonify({"message": "Customer created", "customer_id": cursor.lastrowid}), 201
    finally:
        cursor.close()
        conn.close()

@customers_blueprint.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    reward_points = data.get('reward_points')
    phone_number = data.get('phone_number')
    email = data.get('email')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            UPDATE Customer
            SET first_name = %s,
                last_name = %s,
                reward_points = %s,
                phone_number = %s,
                email = %s
            WHERE customer_id = %s
        """
        cursor.execute(sql, (first_name, last_name, reward_points, phone_number, email, customer_id))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({"message": "Customer updated"}), 200
        else:
            return jsonify({"message": "Customer not found"}), 404
    finally:
        cursor.close()
        conn.close()

@customers_blueprint.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({"message": "Customer deleted"}), 200
        else:
            return jsonify({"message": "Customer not found"}), 404
    finally:
        cursor.close()
        conn.close()