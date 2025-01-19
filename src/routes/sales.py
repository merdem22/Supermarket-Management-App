from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/sales')
def list_sales():
    sort_column = request.args.get('sort', 'sale_date')
    allowed_sorts = ['sale_date', 'total_amount']  # or define how you want to sort

    if sort_column not in allowed_sorts:
        sort_column = 'sale_date'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # For demonstration, let's do a subquery or a joined query that
    # calculates total_amount. But if we store total_amount directly, we can just order by that.
    # We'll keep it simple and just get the Sale columns for now.
    query = f"SELECT s.*, c.first_name AS customer_first, c.last_name AS customer_last "
    query += f"FROM Sale s JOIN Customer c ON s.customer_id = c.customer_id "
    query += f"ORDER BY s.{sort_column} DESC"

    cursor.execute(query)
    sales = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('sales.html', sales=sales, sort=sort_column)


@sales_bp.route('/sales/<int:sale_id>')
def sale_detail(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Get the main sale info, including discount, customer, etc.
    cursor.execute("""
        SELECT s.*, c.first_name as customer_first, c.last_name as customer_last,
               d.discount_type
        FROM Sale s
        JOIN Customer c ON s.customer_id = c.customer_id
        LEFT JOIN Discount d ON s.discount_id = d.discount_id
        WHERE s.sale_id = %s
    """, (sale_id,))
    sale = cursor.fetchone()
    if not sale:
        cursor.close()
        conn.close()
        return "Sale not found", 404

    # 2) Get the line items
    cursor.execute("""
        SELECT sp.quantity, p.product_id, p.product_name, p.unit_price
        FROM Sale_Product sp
        JOIN Product p ON sp.product_id = p.product_id
        WHERE sp.sale_id = %s
    """, (sale_id,))
    line_items = cursor.fetchall()

    cursor.close()
    conn.close()

    # 3) Calculate totals on the Python side if you want
    subtotal = 0
    for item in line_items:
        cost = item['unit_price'] * item['quantity']
        subtotal += cost

    discount_amount = 0
    # If discount_type is 'over_threshold', you might check threshold
    # If discount_type is 'percentage', do that. We'll do a simple example:

    if sale['discount_type'] == 'over_threshold':
        # you'd need threshold, discount_amount from OverThresholdDiscount
        # either join them or do a second query
        pass
    elif sale['discount_type'] == 'percentage':
        # you'd need percentage from PercentageDiscount
        pass

    total_with_discount = subtotal  # adjust once you implement discount logic

    return render_template('sale_detail.html',
                           sale=sale,
                           line_items=line_items,
                           subtotal=subtotal,
                           total_with_discount=total_with_discount)
