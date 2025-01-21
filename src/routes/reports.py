# src/routes/reports.py

from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

reports_bp = Blueprint('reports_bp', __name__)

@reports_bp.route('/reports/top_selling')
def top_selling_by_category():
    """
    1) Top-selling product per category.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Subquery approach: find total_sold for each product, then join with max_table
    query = """
    SELECT t.category,
           t.product_name,
           t.total_sold
    FROM (
       SELECT p.category,
              p.product_name,
              SUM(sp.quantity) AS total_sold
       FROM Product p
       JOIN Sale_Product sp ON p.product_id = sp.product_id
       GROUP BY p.category, p.product_name
    ) AS t
    JOIN (
       SELECT sub.category,
              MAX(sub.total_sold) AS max_sold
       FROM (
         SELECT p.category,
                SUM(sp.quantity) AS total_sold
         FROM Product p
         JOIN Sale_Product sp ON p.product_id = sp.product_id
         GROUP BY p.category, p.product_name
       ) AS sub
       GROUP BY sub.category
    ) AS max_table
       ON t.category    = max_table.category
      AND t.total_sold = max_table.max_sold
    ORDER BY t.category;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('top_selling.html', results=results)


@reports_bp.route('/reports/monthly_sales', methods=['GET'])
def monthly_sales():
    """
    Displays monthly sales totals, with optional date filters (start_date, end_date).
    """
    start_date = request.args.get('start_date', '')  # e.g. '2025-01-01'
    end_date   = request.args.get('end_date', '')    # e.g. '2025-02-01'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # We'll build the base query
    base_query = """
        SELECT DATE_FORMAT(s.sale_date, '%%Y-%%m') AS sale_month,
               SUM(sp.quantity * p.unit_price) AS monthly_total
        FROM Sale s
        JOIN Sale_Product sp ON s.sale_id = sp.sale_id
        JOIN Product p ON sp.product_id = p.product_id
    """

    # We'll store conditions in a list and join them
    conditions = []
    params = []

    # If user provided start_date and end_date, add the WHERE
    if start_date and end_date:
        conditions.append("s.sale_date BETWEEN %s AND %s")
        params.append(start_date)
        params.append(end_date)
    elif start_date:
        conditions.append("s.sale_date >= %s")
        params.append(start_date)
    elif end_date:
        conditions.append("s.sale_date <= %s")
        params.append(end_date)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += """
        GROUP BY DATE_FORMAT(s.sale_date, '%%Y-%%m')
        ORDER BY sale_month
    """

    cursor.execute(base_query, tuple(params))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'monthly_sales.html',
        results=results,
        start_date=start_date,
        end_date=end_date
    )


@reports_bp.route('/reports/top_employees')
def top_employees():
    """
    3) Employees whose total sales exceed the average of all employees.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT e.employee_id,
           e.first_name,
           e.last_name,
           emp_sales.total_amount
    FROM Employee e
    JOIN (
      -- Subquery: sum per employee
      SELECT s.employee_id,
             SUM(sp.quantity * p.unit_price) AS total_amount
      FROM Sale s
      JOIN Sale_Product sp ON s.sale_id = sp.sale_id
      JOIN Product p ON sp.product_id = p.product_id
      GROUP BY s.employee_id
    ) AS emp_sales
      ON e.employee_id = emp_sales.employee_id
    WHERE emp_sales.total_amount >
    (
       SELECT AVG(all_emp.sum_total)
       FROM (
         SELECT s2.employee_id,
                SUM(sp2.quantity * p2.unit_price) AS sum_total
         FROM Sale s2
         JOIN Sale_Product sp2 ON s2.sale_id = sp2.sale_id
         JOIN Product p2 ON sp2.product_id = p2.product_id
         GROUP BY s2.employee_id
       ) AS all_emp
    )
    ORDER BY emp_sales.total_amount DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('top_employees.html', results=results)
