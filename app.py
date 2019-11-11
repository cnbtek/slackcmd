from flask import Flask
from flask import jsonify

from routes.smartgate import smartgate_api

app = Flask(__name__)

# register routes
app.register_blueprint(smartgate_api, url_prefix='/smartgate')

if __name__ == '__main__':
    app.run()