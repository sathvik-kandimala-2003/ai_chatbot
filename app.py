from flask import Flask
from app.routes import main
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)