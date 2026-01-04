import json, sys
def handler(op, data, fp):
    with open(fp, op) as file:
        match(op):
            case "r":
                return json.load(file)
            case "w":
                json.dump(data, file)
