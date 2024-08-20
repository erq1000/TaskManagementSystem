from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=500, text="Internal server error, we're working to fix it!"), 500

def get_port():
    return int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    port = get_port()
    app.run(host='0.0.0.0', port=port)