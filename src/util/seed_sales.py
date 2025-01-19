import random
import datetime
import mysql.connector

def get_db_connection():
    """Update with your DB credentials."""
    config = {
        'host': 'localhost',
        'user': 'projectUser',
        'password': '56789abc321.',
        'database': 'project'
    }
    return mysql.connector.connect(**config)

def seed_sales(num_sales=50):
    """
    Generate 'num_sales' random transactions (rows in 'Sale') and line items in 'Sale_Product'.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1) Fetch valid IDs for foreign keys
        cursor.execute("SELECT customer_id FROM Customer")
        customer_ids = [row['customer_id'] for row in cursor.fetchall()]
        print("got customer ids")

        cursor.execute("SELECT employee_id FROM Employee")
        employee_ids = [row['employee_id'] for row in cursor.fetchall()]
        print("got employee ids")

        cursor.execute("SELECT discount_id, discount_type FROM Discount")
        discount_rows = cursor.fetchall()  # e.g., [{'discount_id': 1, 'discount_type': 'percentage'}, ...]
        print("got discount rows")

        cursor.execute("SELECT product_id, quantity_in_stock, unit_price FROM Product")
        product_rows = cursor.fetchall()  # e.g., [{'product_id': 1, 'quantity_in_stock': 100, 'unit_price': 2.5}, ...]
        print("got product rows")

        # Convert product rows to a dictionary for quick lookups
        #product_dict = {p['product_id']: p for p in product_rows}


        # 2) Generate transactions
        for _ in range(num_sales):
            # 2a) Randomly pick customer / employee
            customer_id = random.choice(customer_ids)
            employee_id = random.choice(employee_ids)
            print(f"customer_id: {customer_id}, employee_id: {employee_id}")

            # 2b) Potentially pick a discount ~ 30% chance (adjust as you like)
            use_discount = random.random() < 0.35
            discount_id = random.choice(discount_rows)['discount_id'] if (use_discount and discount_rows) else None
            print(f"discount_id: {discount_id}")

            # 2c) Payment method
            payment_method = random.choice(['Cash', 'Credit Card'])
            print(f"payment_method: {payment_method}")

            # 2d) Choose a random date in the last 200 days
            days_offset = random.randint(0, 200)
            random_date = datetime.datetime.now() - datetime.timedelta(days=days_offset)
            sale_date_str = random_date.strftime('%Y-%m-%d %H:%M:%S')
            print(f"sale_date: {sale_date_str}")

            # 2e) Randomly pick how many reward points to use
            rewards_used = random.randint(0, 5) * 10
            print(f"rewards_used: {rewards_used}")

            # 3) Insert the Sale row
            insert_sale_sql = """
                INSERT INTO Sale (customer_id, employee_id, payment_method, sale_date, rewards_points_used, discount_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sale_sql, (customer_id, employee_id, payment_method, sale_date_str, rewards_used, discount_id))
            print("inserted sale")
            sale_id = cursor.lastrowid
            print(f"sale_id: {sale_id}")

            # 4) Pick line items: random 1-5 items
            num_line_items = random.randint(1, 5)
            chosen_products = random.sample(product_rows, num_line_items)
            print(f"chosen_products: {chosen_products}")

            for prod in chosen_products:
                pid = prod['product_id']
                quantity_in_stock = prod['quantity_in_stock']
                print(f"pid: {pid}, quantity_in_stock: {quantity_in_stock}")
                #unit_price = prod['unit_price']

                if quantity_in_stock <= 0:
                    # If no stock, skip or pick a different product
                    continue

                # pick random quantity up to 5 or up to the stock
                quantity = random.randint(1, min(5, quantity_in_stock))
                print(f"quantity: {quantity}")

                # Insert into Sale_Product
                insert_line_sql = """
                    INSERT INTO Sale_Product (sale_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_line_sql, (sale_id, pid, quantity))
                print("inserted line")

                '''# 4b) Update product stock
                new_stock = quantity_in_stock - quantity
                update_product_sql = """
                    UPDATE Product SET quantity_in_stock = %s WHERE product_id = %s
                """
                cursor.execute(update_product_sql, (new_stock, pid))
                # update local cache
                prod['quantity_in_stock'] = new_stock
                '''

            conn.commit() # commit each sale
            print(f"Inserted sale {sale_id} with {num_line_items} line items")
        # 6) Commit everything
        conn.commit()
        print(f"Successfully inserted {num_sales} random sales.")
    except Exception as e:
        conn.rollback()
        print("Error seeding sales:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_sales(num_sales=250)
