from flask import Blueprint, jsonify, request
from src.db_connection import get_connection

products_blueprint = Blueprint('products', __name__)

@products_blueprint.route('/', methods=['GET'])
def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Product")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()

@products_blueprint.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
        row = cursor.fetchone()
        if row:
            return jsonify(row), 200
        else:
            return jsonify({"message": "Product not found"}), 404
    finally:
        cursor.close()
        conn.close()
