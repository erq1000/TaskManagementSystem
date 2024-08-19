from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def get_port():
    return int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    port = get_port()
    app.run(host='0.0.0.0', port=port)