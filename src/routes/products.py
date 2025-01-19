from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/products/')
def list_products():
    sort_column = request.args.get('sort', 'product_name')  # default sort by product_name
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Simple whitelist of columns to avoid SQL injection
    allowed_sorts = ['product_name', 'category', 'unit_price', 'quantity_in_stock']
    if sort_column not in allowed_sorts:
        sort_column = 'product_name'

    query = f"SELECT * FROM Product ORDER BY {sort_column} ASC"
    cursor.execute(query)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('products.html', products=products, sort=sort_column)

@products_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        return "Product not found", 404

    return render_template('product_detail.html', product=product)
