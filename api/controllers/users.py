from flask_restx import Resource, reqparse


class Users(Resource):
    def get(self):
        with open("../src/usernames.txt") as file:
            usernames = file.read().rstrip("\n").split(",")
        return {"data": {"usernames": usernames}}

    def post(self):
        users_post_args = reqparse.RequestParser()
        users_post_args.add_argument("usernames", type=str, help="Twitter username", location="form", required=True)
        args = users_post_args.parse_args()
        print(args)
        # Write new username
        # All tasks with AWS Lambda functions
        return {"user": args}
