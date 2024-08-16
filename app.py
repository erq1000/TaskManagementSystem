from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

port = int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)