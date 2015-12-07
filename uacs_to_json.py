import csv
import sys
import json

final_json = {}

f = open(sys.argv[1], 'rt')
try:

    department = ""
    agency = ""
    region = ""
    operating_unit =""

    reader = csv.reader(f)

    for row in reader:
        department = row[0].upper().strip()
        agency = row[1].upper().strip() if row[1] else department
        region = row[2].upper().strip() if row[2] else agency
        operating_unit = row[3].upper().strip() if row[3] else region
        uacs = str(row[4])

        if department not in final_json:
            final_json[department] = {}

        if agency not in final_json[department]:
            final_json[department][agency] = {}

        if region not in final_json[department][agency]:
            final_json[department][agency][region] = {}

        final_json[department][agency][region][operating_unit] = uacs
        print row


finally:
    f.close()

f = open('uacs.json','w')
f.write(json.dumps(final_json))
f.close()


"""
Department
Agency
Region
Lower-Level-Operating Unit
UACS


"""
