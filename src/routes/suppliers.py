from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

suppliers_bp = Blueprint('suppliers_bp', __name__)

@suppliers_bp.route('/suppliers')
def list_suppliers():
    """
    Displays a list of suppliers with sorting by name or address.
    Also toggles ascending/descending order each time the user clicks.
    """

    # Get sort column & order from query params
    sort_col = request.args.get('sort', 'supplier_name')
    order = request.args.get('order', 'asc').lower()  # 'asc' or 'desc'

    # Allowed columns to prevent SQL injection
    allowed_cols = ['supplier_name', 'supplier_address']
    if sort_col not in allowed_cols:
        sort_col = 'supplier_name'

    # Ensure order is only 'asc' or 'desc'
    if order not in ['asc', 'desc']:
        order = 'asc'

    # Build the query
    query = f"SELECT * FROM Supplier ORDER BY {sort_col} {order}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()

    # Determine next order for toggle
    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('suppliers.html',
                           suppliers=suppliers,
                           sort_col=sort_col,
                           current_order=order,
                           next_order=next_order)

@suppliers_bp.route('/suppliers/<int:supplier_id>')
def supplier_detail(supplier_id):
    """
    Shows a single supplier and the products they supply.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Fetch supplier info
    cursor.execute("SELECT * FROM Supplier WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    if not supplier:
        cursor.close()
        conn.close()
        return "Supplier not found", 404

    # 2) Fetch all products from Supplier_Product
    #    that this supplier provides
    cursor.execute("""
        SELECT p.product_id, p.product_name, p.category, p.unit_price, p.quantity_in_stock
        FROM Supplier_Product sp
        JOIN Product p ON sp.product_id = p.product_id
        WHERE sp.supplier_id = %s
    """, (supplier_id,))
    supplied_products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('supplier_detail.html',
                           supplier=supplier,
                           supplied_products=supplied_products)
