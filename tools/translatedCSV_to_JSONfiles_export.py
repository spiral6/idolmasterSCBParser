import csv
import json
with open('N:\\Modding and Homebrew\\im@s translation\\translation tools\\kaitai_script\\dialogue\\hibiki\\translated\\IMAS2 Translation Progress - hib_processing for JSON export.csv', newline='', encoding='utf-8') as csvfile:
    
    # Read exported CSV file with translations provided by BonillaP - spiral6
    # Save it in dictionary variable.
    dialogue_line_reader = csv.reader(csvfile, delimiter=',')
    next(dialogue_line_reader) # skip header row
    dialogue_dict = {}
    for row in dialogue_line_reader:
        if row[0] in dialogue_dict:
            dialogue_dict[row[0]]["strings"].append(row[1])
        else:
            dialogue_dict[row[0]]= {}
            dialogue_dict[row[0]]["filename"] = row[0]
            dialogue_dict[row[0]]["strings"] = []
            dialogue_dict[row[0]]["strings"].append(row[1])

for key in dialogue_dict:
    with open(key + ".dec.culledIV_new.json", 'w', encoding='utf-16') as json_file:
        json.dump(dialogue_dict[key], json_file, indent=4)
    json_file.close()

# exported_file= 'hibiki_exported_csv_to_json.json'
# with open(exported_file, 'w') as json_file:
#     json.dump(dialogue_dict, json_file, indent = 4)
# print(f"Data saved to {exported_file}")