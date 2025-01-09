# src/routes/sales.py
from flask import Blueprint, jsonify, request
from src.db_connection import get_connection

sales_blueprint = Blueprint('sales', __name__)

@sales_blueprint.route('/', methods=['POST'])
def create_sale():
    data = request.json
    
    customer_id = data['customer_id']
    employee_id = data['employee_id']
    payment_method = data['payment_method']
    sale_date = data['sale_date']  # in YYYY-MM-DD HH:MM:SS format or handle it in Python
    discount_id = data.get('discount_id')  # might be None
    items = data['items']  # list of { product_id, quantity }

    # Example: items = [
    #   { "product_id": 1, "quantity": 2 },
    #   { "product_id": 3, "quantity": 1 }
    # ]

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1) Insert the sale row (Sale table)
        insert_sale_sql = """
            INSERT INTO Sale (customer_id, employee_id, payment_method, sale_date, rewards_points_used, discount_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        # For now, assume rewards_points_used is 0 (or you can pass it in data)
        cursor.execute(insert_sale_sql, (customer_id, employee_id, payment_method, sale_date, 0, discount_id))
        sale_id = cursor.lastrowid
        
        # 2) Insert line items into Sale_Product
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            cursor.execute("""
                INSERT INTO Sale_Product (sale_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (sale_id, product_id, quantity))
            
            # 3) Deduct quantity from Product table
            cursor.execute("""
                UPDATE Product
                SET quantity_in_stock = quantity_in_stock - %s
                WHERE product_id = %s
            """, (quantity, product_id))

        # 4) Apply discount logic and reward points (optional advanced approach):
        #    - Compute the total from the line items
        #    - Determine if discount threshold is met
        #    - Etc.
        #    For demonstration, we'll keep it simple.
        
        # 5) Optionally update the customer's reward_points
        #    e.g., if you want 1 point per $1, do something like:
        #    cursor.execute("""
        #      UPDATE Customer
        #      SET reward_points = reward_points + %s
        #      WHERE customer_id = %s
        #    """, (points_earned, customer_id))
        
        conn.commit()
        return jsonify({"message": "Sale created successfully", "sale_id": sale_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
