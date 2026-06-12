from flask import Flask
from DL.history_repo import load_stacks_from_db
from Routes.auth_routes import auth_bp
from Routes.manager_routes import manager_bp
from Routes.passenger_routes import passenger_bp

# Tell Flask where templates are
app = Flask(__name__, template_folder="UI/templates")
app.secret_key = "supersecretkey"

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(passenger_bp)

if __name__ == "__main__":
    load_stacks_from_db()
    app.run(debug=True)