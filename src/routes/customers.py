from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

customers_bp = Blueprint('customers_bp', __name__)

@customers_bp.route('/customers/')
def list_customers():
    """
    Display all customers with sorting by last_name, first_name, or reward_points.
    """
    sort_column = request.args.get('sort', 'last_name')
    allowed_sorts = ['last_name', 'first_name', 'reward_points']
    if sort_column not in allowed_sorts:
        sort_column = 'last_name'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM Customer ORDER BY {sort_column} ASC"
    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('customers.html', 
                           customers=customers, 
                           sort=sort_column)

@customers_bp.route('/customers/<int:customer_id>')
def customer_detail(customer_id):
    """
    Shows detailed info for a single customer, including total spent and their past sales.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Basic customer info
    cursor.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        cursor.close()
        conn.close()
        return "Customer not found", 404

    # 2) Fetch the customer's sales
    cursor.execute("""
        SELECT sale_id, sale_date, payment_method, rewards_points_used, discount_id 
        FROM Sale
        WHERE customer_id = %s
        ORDER BY sale_date DESC
    """, (customer_id,))
    sales = cursor.fetchall()

    total_spent = 0.0
    # If you have discount logic, you'd replicate that logic (similar to sales) 
    # to find the final total for each sale. 
    for sale in sales:
        sale_id = sale['sale_id']
        # compute that sale's total (basic version, no discount for now)
        cursor.execute("""
            SELECT sp.quantity, p.unit_price
            FROM Sale_Product sp
            JOIN Product p ON sp.product_id = p.product_id
            WHERE sp.sale_id = %s
        """, (sale_id,))
        items = cursor.fetchall()

        subtotal = sum(item['quantity'] * float(item['unit_price']) 
                       for item in items)
        # If you want to apply discount logic, do so here
        sale_total = subtotal
        total_spent += sale_total

    cursor.close()
    conn.close()

    return render_template('customer_detail.html',
                           customer=customer,
                           sales=sales,
                           total_spent=round(total_spent, 2))
