from flask import Flask
from flask_cors import CORS
from app.routes import setup_routes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up routes
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)