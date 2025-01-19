from flask import Flask
from src.routes.products import products_bp
from src.routes.sales import sales_bp
from src.routes.customers import customers_bp
from src.routes.employees import employees_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(products_bp, url_prefix='/')
    app.register_blueprint(sales_bp, url_prefix='/')
    app.register_blueprint(customers_bp, url_prefix='/')
    app.register_blueprint(employees_bp, url_prefix='/')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
