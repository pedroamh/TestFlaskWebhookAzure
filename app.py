from flask import Flask
from handlers.webhook_handler import webhook_router


app = Flask(__name__)
app.register_blueprint(webhook_router)

@app.route("/test")
def index():
    return "<h1>Esto es una prueba</h1>"


if __name__ == '__main__':
    app.run()