import os
from flask_restx import Resource, reqparse, abort
from flask_httpauth import HTTPTokenAuth
from api import api_resources

auth = HTTPTokenAuth()
API_TOKEN = os.environ.get("API_TOKEN")
usernames_file = "api/usernames.txt"


@auth.verify_token
def verify_token(token):
    return token == API_TOKEN if token == API_TOKEN else abort_unauthorized_access()


class Users(Resource):
    @auth.login_required
    def get(self):
        usernames = get_usernames()
        return {"data": {"usernames": usernames}}

    @auth.login_required
    def post(self):
        users_post_args = reqparse.RequestParser()
        users_post_args.add_argument("usernames", type=str, help="Twitter usernames required", location="form",
                                     required=True)
        args = users_post_args.parse_args()

        # ERRORS:
        # ''; whitespace
        passed_users = args["usernames"].split(",")
        all_new, existing_users = check_usernames(*passed_users)

        if all(all_new):
            add_usernames(*passed_users)
            return f"Added usernames: {', '.join(passed_users)}", 201

        else:
            abort_post_existing_users(*existing_users)

        # Add tasks with AWS Lambda functions

    @auth.login_required
    def delete(self):
        users_delete_args = reqparse.RequestParser()
        users_delete_args.add_argument("usernames", type=str, help="Twitter usernames required", location="form",
                                       required=True)
        args = users_delete_args.parse_args()

        passed_users = args["usernames"].split(",")
        deleted, not_found = remove_usernames(*passed_users)
        deleted_message = f"Users deleted from database: {', '.join(deleted)}" if len(deleted) > 0 else ""
        not_found_message = f"Users not found in database: {', '.join(not_found)}" if len(not_found) > 0 else ""
        return f"{deleted_message}\n{not_found_message}"


def get_usernames():
    db_conn = api_resources.connect_to_database()
    cur = db_conn.cursor()
    cur.execute("SELECT username FROM twitter.usernames")
    all_usernames = [u[0] for u in cur.fetchall()]
    db_conn.close()
    return all_usernames


def check_usernames(*args):
    usernames = get_usernames()
    new_users = [u not in usernames for u in args]
    duplicated_users = [u for u in args if u in usernames]
    return new_users, duplicated_users


def add_usernames(*args):
    print(args)
    db_conn = api_resources.connect_to_database()
    api_resources.insert_batch(
        conn=db_conn,
        multicolumn=False,
        data=args,
        schema="twitter",
        table="usernames",
        conflict=False,
        single_column="username")
    db_conn.close()


def remove_usernames(*args):
    usernames = get_usernames()
    users_to_delete = [u for u in usernames if u in args]
    not_found_users = [u for u in args if u not in usernames]
    db_conn = api_resources.connect_to_database()
    cur = db_conn.cursor()
    cur.execute("DELETE FROM twitter.usernames WHERE username in ('{}')".format("','".join(users_to_delete)))
    db_conn.commit()
    db_conn.close()
    return users_to_delete, not_found_users


def abort_post_existing_users(*args):
    return abort(409, message=f"Error 409. These users are already listed: {', '.join(args)}")


def abort_unauthorized_access():
    return abort(401, message="Unauthorized Access. Authentication token required")
