from flask import Flask
from map import map_endpoints
app = Flask(__name__)

app.register_blueprint(map_endpoints, url_prefix="/map")
@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
