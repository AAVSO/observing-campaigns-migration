import csv
import json

# Read the JSON data from a file
with open('data.json', 'r') as json_file:
    json_data = json.load(json_file)

# Open a new CSV file for writing
with open('../data/observing_campaigns.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter='|')

    # Write the header
    header = ['ID', 'Title', 'Principal Investigator', 'Abstract', 'Justification', 'Target Object', 'Start Date',
              'End Date', 'Status']
    csv_writer.writerow(header)

    # Write the data
    for id, record in json_data.items():
        row = [
            id,
            record.get('Title', ''),
            record.get('Principal Investigator', ''),
            record.get('Abstract', ''),
            record.get('Justification', ''),
            record.get('Target Object', ''),
            record.get('Start Date', ''),
            record.get('End Date', ''),
            record.get('Status', '')
        ]
        csv_writer.writerow(row)
