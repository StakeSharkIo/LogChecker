import json
import os
import re
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(script_dir)

ignore = ["main.py", "result.json"]

files = [f for f in files if f not in ignore]

print(files)


def parse_logs():
    data = {}
    data_errors = {}
    dates = []
    for file in files:
        with open(file, "r") as f:
            for line in f:
                match = re.search(r'\[(.*?)\].*?Status=(\d+)', line)
                if match:
                    timestamp = match.group(1)
                    status = match.group(2)
                    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = dt.strftime("%m-%d")
                    dates.append(formatted_date) if formatted_date not in data else None
                    if formatted_date not in data:
                        data[formatted_date] = 0
                    if status == "200":
                        data[formatted_date] += 1
                    else:
                        if formatted_date not in data_errors:
                            data_errors[formatted_date] = {}
                        data_errors[formatted_date][status] = data_errors[formatted_date].get(status, 0) + 1
                else:
                    print("No match found")
    return data, data_errors, dates


good, bad, dates = parse_logs()

for date in dates:
    total_not_200 = 0
    print(f"[{date}]")
    print(f"  [200]: {good[date]}") if date in good else None
    if date not in bad:
        continue
    for code in bad[date]:
        total_not_200 += bad[date][code]
        print(f"  [{code}]: {bad[date][code]}")
    print(f"  Total not 200: {total_not_200}")
with open("result.json", "w") as f:
    f.write(json.dumps({
        "good": good,
        "bad": bad,
        "files": files
    }))
