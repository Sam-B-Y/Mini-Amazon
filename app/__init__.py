from flask import Flask, session
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.secret_key = '!@#($rcheriq34c1!@$fasjdc)'  # should be hidden but for the sake of this project, it's here
    app.config['SESSION_TYPE'] = 'filesystem' 

    app.db = DB(app)
    login.init_app(app)
    

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .search import bp as search_bp
    app.register_blueprint(search_bp)

    from .reviews import bp as review_bp
    app.register_blueprint(review_bp)
    
    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)
    
    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .products import bp as products_bp
    app.register_blueprint(products_bp)

    from .orders import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders') 

    from .chatbot import bp as chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app
