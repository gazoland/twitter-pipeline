from flask import Flask
from flask_restx import Api

from controllers.users import Users

app = Flask(__name__)
app.config["DEBUG"] = True
api = Api(
    app,
    version="1.0",
    title="Twitter Pipeline API",
    description="A simple API for the Twitter Data Pipeline project.",
    doc="/docs"
)

api.add_resource(Users, "/v1/users")

if __name__ == "__main__":
    app.run()
