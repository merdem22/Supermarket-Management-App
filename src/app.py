from flask import Flask
from src.routes.customers import customers_blueprint
from src.routes.products import products_blueprint
from src.routes.sales import sales_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(customers_blueprint, url_prefix='/customers')
    app.register_blueprint(products_blueprint, url_prefix='/products')
    app.register_blueprint(sales_blueprint, url_prefix='/sales')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) #run in debug for development