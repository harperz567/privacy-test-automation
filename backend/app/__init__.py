from flask import Flask
from flask_cors import CORS
from config import Config
from app.database import db, init_db
from app.middleware import setup_request_logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    
    db.init_app(app)
    
    setup_request_logging(app)
    
    from app.api import auth, employees, dsr, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(dsr.bp)
    app.register_blueprint(admin.bp)
    
    with app.app_context():
        db.create_all()
    
    return app