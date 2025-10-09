from run_migrations import run_all_migrations
from flask import Flask
from flask_restx import Api
from cors import enable_cors
from utils.config import Config
from utils.mysqlUtils import initialize_database
from api.auth import auth_ns
from api.course import course_ns

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    enable_cors(app)
    api = Api(app)
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(course_ns, path='/course')
    # api.add_namespace(parking_ns, path='/parking')
    # api.add_namespace(floor_ns, path='/floor')
    # api.add_namespace(user_ns, path='/user')
    # api.add_namespace(device_ns, path='/device')
    # api.add_namespace(config_ns, path='/config')
    # api.add_namespace(display_ns, path='/display')
    return app

app = create_app()
initialize_database()
run_all_migrations()

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0", port=5000)



