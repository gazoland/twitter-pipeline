from flask import Flask
from flask_restx import Api
import os

from api.controllers.users import Users

app = Flask(__name__)
app.config["DEBUG"] = os.getenv("API_DEBUG", False) in ("true", "True", "t", "T", 1)  # Local: True / Docker: False
api = Api(
    app,
    version="1.0",
    title="Twitter Pipeline API",
    description="A simple API for the Twitter Data Pipeline project.",
    doc="/v1/docs"
)

api.add_resource(Users, "/v1/users")


@app.errorhandler(404)
def abort_notfound(e):
    return {"message": "Error 404. Resource not found."}, 404


if __name__ == "__main__":
    app.run(port=os.environ.get("API_PORT"), host="0.0.0.0")
