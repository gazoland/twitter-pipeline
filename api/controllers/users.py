import os
from flask_restx import Resource, reqparse, abort
from api import api_resources
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth()
API_TOKEN = os.environ.get("API_TOKEN")


@auth.verify_token
def verify_token(token):
    return token == API_TOKEN


class Users(Resource):
    @auth.login_required
    def get(self):
        usernames = get_usernames(filename="../src/usernames.txt")
        return {"data": {"usernames": usernames}}

    @auth.login_required
    def post(self):
        users_post_args = reqparse.RequestParser()
        users_post_args.add_argument("usernames", type=str, help="Twitter usernames required", location="form", required=True)
        args = users_post_args.parse_args()

        # ERRORS:
        # ''; whitespace
        passed_users = args["usernames"].split(",")
        all_new, existing_users = check_usernames(*passed_users, filename="../src/usernames.txt")

        if all(all_new):
            add_usernames(*passed_users, current_filename="../src/usernames.txt", new_filename="../src/usernames.txt")
            return f"Added usernames: {', '.join(passed_users)}", 201

        else:
            abort_post_existing_users(*existing_users)

        # Add tasks with AWS Lambda functions

    @auth.login_required
    def delete(self):
        users_delete_args = reqparse.RequestParser()
        users_delete_args.add_argument("usernames", type=str, help="Twitter usernames required", location="form", required=True)
        args = users_delete_args.parse_args()

        passed_users = args["usernames"].split(",")
        updated, deleted, not_found = remove_usernames(*passed_users, current_filename="../src/usernames.txt", new_filename="../src/usernames.txt")
        deleted_message = f"Users deleted from list: {', '.join(deleted)}" if len(deleted) > 0 else ""
        not_found_message = f"Users not found in list: {', '.join(not_found)}" if len(not_found) > 0 else ""
        return f"{deleted_message}\n{not_found_message}"


def get_usernames(filename):
    with open(filename) as file:
        all_usernames = file.read().rstrip("\n").split(",")
    return all_usernames


def check_usernames(*args, filename):
    usernames = get_usernames(filename=filename)
    new_users = [u not in usernames for u in args]
    duplicated_users = [u for u in args if u in usernames]
    return new_users, duplicated_users


def add_usernames(*args, current_filename, new_filename):
    users_list = get_usernames(filename=current_filename)
    users_list.extend(args)
    api_resources.write_text_file(users_list, filename=new_filename)


def remove_usernames(*args, current_filename, new_filename):
    usernames = get_usernames(filename=current_filename)
    updated_users = [u for u in usernames if u not in args]
    deleted_users = [u for u in usernames if u in args]
    not_found_users = [u for u in args if u not in usernames]
    api_resources.write_text_file(updated_users, filename=new_filename)
    return updated_users, deleted_users, not_found_users


def abort_post_existing_users(*args):
    return abort(409, message=f"Error. These users are already listed: {', '.join(args)}")
