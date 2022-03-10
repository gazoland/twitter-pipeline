from datetime import datetime, timezone
import resources


def users_url(filename):
    with open(filename, "r") as username_file:
        users = username_file.read().rstrip('\n')

    user_fields = ["description", "created_at", "public_metrics", "verified", "entities"]

    u_fields = f"user.fields={','.join(user_fields)}"
    usernames = f"usernames={users}"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, u_fields)
    return url


def user_file_creation(datafile):
    user_data_filename = f"users_{datetime.strftime(datetime.today(), '%Y%m%d')}.txt"
    resources.write_json_file(datafile, user_data_filename)

    user_ids = dict()
    for user in datafile["data"]:
        user_ids[user["username"]] = user["id"]
    resources.write_json_file(user_ids, "user_ids.txt")

    return user_data_filename


def ingest_users():
    url = users_url("usernames.txt")
    user_data = resources.connect_to_endpoint(url)
    user_data["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    user_data_filename = user_file_creation(user_data)
    resources.upload_to_s3(user_data_filename, path="data/users/")
    resources.delete_file(user_data_filename)


if __name__ == "__main__":
    ingest_users()
