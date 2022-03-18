import os
import json


def write_json_file(data_object, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_object, f, ensure_ascii=False, indent=4)
    return 'Done'


def delete_file(filename):
    os.remove(os.path.join(os.getcwd(), filename))
    return 'File removed'
