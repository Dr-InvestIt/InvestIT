import json

# a_dictionary = {"model": "stocks.SP500", "pk": }

# with open('data.json', 'r+') as f:
#     data = json.load(f)
#     data.update(a_dictionary)
#     file.seek(0)
#     json.dump(data, file)

# for
file1 = open('SP500.txt', 'r')
Lines = file1.readlines()


def write_json(new_data, filename='stocks_data.json'):
    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


count = 0
for line in Lines:
    entry = {"model": "stocks.SP500",
             "pk": count,
             "fields": {"stock_id": line.strip()}
             }

    write_json(entry)
    count += 1
