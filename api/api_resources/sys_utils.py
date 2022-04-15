

def write_text_file(string_data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(",".join(string_data))
    return 'Done'


