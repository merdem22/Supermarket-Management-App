from flask import Blueprint, render_template, request
from src.db_connection import get_db_connection

employees_bp = Blueprint('employees_bp', __name__)

@employees_bp.route('/employees')
def list_employees():
    """
    Display employees, allowing sorting by last_name, first_name, or salary.
    """
    sort_column = request.args.get('sort', 'last_name')
    allowed_sorts = ['last_name', 'first_name', 'salary']
    if sort_column not in allowed_sorts:
        sort_column = 'last_name'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Join employee to its supervisor
    query = f"""
    SELECT e.employee_id, e.first_name, e.last_name, e.salary, e.supervisor_id,
           s.first_name AS supervisor_first, s.last_name AS supervisor_last, s.employee_id AS supervisor_eid
    FROM Employee e
    LEFT JOIN Employee s ON e.supervisor_id = s.employee_id
    ORDER BY e.{sort_column} ASC
    """
    cursor.execute(query)
    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('employees.html', employees=employees, sort=sort_column)

@employees_bp.route('/employees/<int:employee_id>')
def employee_detail(employee_id):
    """
    Show detail for a single employee, including supervisor info and subordinates.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the main employee
    cursor.execute("""
        SELECT e.*, 
               s.first_name AS supervisor_first, s.last_name AS supervisor_last, s.employee_id AS supervisor_eid
        FROM Employee e
        LEFT JOIN Employee s ON e.supervisor_id = s.employee_id
        WHERE e.employee_id = %s
    """, (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        cursor.close()
        conn.close()
        return "Employee not found", 404

    # Optionally, find subordinates:
    cursor.execute("""
        SELECT e2.employee_id, e2.first_name, e2.last_name
        FROM Employee e2
        WHERE e2.supervisor_id = %s
    """, (employee_id,))
    subordinates = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('employee_detail.html',
                           employee=employee,
                           subordinates=subordinates)
