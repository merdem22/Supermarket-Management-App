from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/sales')
def list_sales():
    sort_column = request.args.get('sort', 'sale_date')
    order = request.args.get('order', 'asc').lower()

    # We will allow sorting by 'sale_id', 'sale_date', 'customer_name', or 'total_amount'
    valid_sorts = ['sale_id', 'sale_date', 'customer_name', 'total_amount']
    if sort_column not in valid_sorts:
        sort_column = 'sale_date'
    if order not in ['asc','desc']:
        order = 'asc'

    # Connect to DB
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Fetch all sales (we do final sorting in Python)
    cursor.execute("""
        SELECT 
            s.sale_id, 
            s.sale_date, 
            s.discount_id,
            c.customer_id,
            c.first_name AS customer_first, 
            c.last_name AS customer_last
        FROM Sale s
        JOIN Customer c ON s.customer_id = c.customer_id
        ORDER BY s.sale_date DESC
    """)
    sales = cursor.fetchall()

    # 2) Fetch discount details into dictionaries
    cursor.execute("SELECT discount_id, threshold, discount_amount FROM OverThresholdDiscount")
    threshold_discounts = {row['discount_id']: row for row in cursor.fetchall()}

    cursor.execute("SELECT discount_id, percentage FROM PercentageDiscount")
    percentage_discounts = {row['discount_id']: row for row in cursor.fetchall()}

    cursor.execute("SELECT discount_id, discount_type FROM Discount")
    discount_types = {}
    for row in cursor.fetchall():
        discount_types[row['discount_id']] = row['discount_type']

    # 3) Compute total_amount for each sale
    for sale in sales:
        sale_id = sale['sale_id']
        discount_id = sale['discount_id']

        # Build a 'customer_name' field for sorting
        sale['customer_name'] = f"{sale['customer_first']} {sale['customer_last']}"

        # 3a) Sum line items (subtotal)
        cursor.execute("""
            SELECT sp.quantity, p.unit_price
            FROM Sale_Product sp
            JOIN Product p ON sp.product_id = p.product_id
            WHERE sp.sale_id = %s
        """, (sale_id,))
        items = cursor.fetchall()

        subtotal = sum(
            float(item['quantity']) * float(item['unit_price'])
            for item in items
        )

        # 3b) Discount logic
        discount_total = 0.0
        if discount_id:
            d_type = discount_types.get(discount_id)
            if d_type == 'over_threshold':
                row = threshold_discounts.get(discount_id)
                if row:
                    threshold_val = float(row['threshold'])
                    discount_amt = float(row['discount_amount'])
                    if subtotal >= threshold_val:
                        discount_total = discount_amt

            elif d_type == 'percentage':
                row = percentage_discounts.get(discount_id)
                if row:
                    pct = float(row['percentage'])
                    discount_total = (pct / 100.0) * subtotal

        total_with_discount = subtotal - discount_total
        sale['total_amount'] = round(total_with_discount, 2)

    cursor.close()
    conn.close()

    # 4) Sort in Python based on sort_column
    reverse_sort = (order == 'desc')

    if sort_column == 'sale_id':
        sales.sort(key=lambda s: s['sale_id'], reverse=reverse_sort)
    elif sort_column == 'sale_date':
        # sale_date is a string like "YYYY-MM-DD HH:MM:SS"; 
        # sorted properly if zero-padded
        sales.sort(key=lambda s: s['sale_date'], reverse=reverse_sort)
    elif sort_column == 'customer_name':
        # Convert to lowercase for case-insensitive sorting
        sales.sort(key=lambda s: s['customer_name'].lower(), reverse=reverse_sort)
    elif sort_column == 'total_amount':
        sales.sort(key=lambda s: s['total_amount'], reverse=reverse_sort)

    next_order = 'asc' if order == 'desc' else 'desc'

    return render_template(
        'sales.html',
        sales=sales,
        sort_column=sort_column,
        order=order,
        next_order=next_order
    )


# =========================================
# =           SALE DETAIL ROUTE          =
# =========================================

@sales_bp.route('/sales/<int:sale_id>')
def sale_detail(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Get the main sale info
    cursor.execute("""
        SELECT s.*, 
               c.customer_id,
               c.first_name AS customer_first, 
               c.last_name AS customer_last,
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

    discount_id = sale['discount_id']
    discount_type = sale['discount_type']

    # 2) Get the line items
    cursor.execute("""
        SELECT sp.quantity, p.product_id, p.product_name, p.unit_price
        FROM Sale_Product sp
        JOIN Product p ON sp.product_id = p.product_id
        WHERE sp.sale_id = %s
    """, (sale_id,))
    line_items = cursor.fetchall()

    # 3) If discount, fetch subtable data
    threshold_data = None
    percentage_data = None

    if discount_id and discount_type == 'over_threshold':
        cursor.execute("""
            SELECT threshold, discount_amount
            FROM OverThresholdDiscount
            WHERE discount_id = %s
        """, (discount_id,))
        threshold_data = cursor.fetchone()

    elif discount_id and discount_type == 'percentage':
        cursor.execute("""
            SELECT percentage
            FROM PercentageDiscount
            WHERE discount_id = %s
        """, (discount_id,))
        percentage_data = cursor.fetchone()

    cursor.close()
    conn.close()

    # 4) Calculate subtotal + discount
    subtotal = sum(
        float(item['quantity']) * float(item['unit_price'])
        for item in line_items
    )

    discount_amount = 0.0
    if discount_id and discount_type == 'over_threshold' and threshold_data:
        if subtotal >= float(threshold_data['threshold']):
            discount_amount = float(threshold_data['discount_amount'])
    elif discount_id and discount_type == 'percentage' and percentage_data:
        pct = float(percentage_data['percentage'])
        discount_amount = (pct / 100.0) * subtotal

    total_with_discount = subtotal - discount_amount

    return render_template(
        'sale_detail.html',
        sale=sale,
        line_items=line_items,
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_amount, 2),
        total_with_discount=round(total_with_discount, 2)
    )
