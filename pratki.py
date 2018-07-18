#!/usr/bin/env python

import argparse
import requests
import xmltodict
from prettytable import PrettyTable
from dateutil.parser import parse
from datetime import datetime, time

# Data in pratki.txt should be
# <Tracking ID> - <Date of shipment> - <Content/Package name>
# ...
# <Tracking ID> - <Date of shipment> - <Content/Package name>


# Define arguments
parser = argparse.ArgumentParser(description='Path of pratki.txt')
parser.add_argument(
    "--pratki",
    dest="pratki_file",
    default="pratki.txt",
    help="Path of pratki.txt.")


args = parser.parse_args()

try:

    # Read packages data from file
    with open(args.pratki_file, "r") as f:
        content = f.readlines()
except FileNotFoundError:
    print()
    print('Missing %s file' % args.pratki_file)
    print()
    exit()

now = datetime.now()

# Initialize table and set titles
table = PrettyTable()
table.field_names = [
    "Tracking #", "Shipped ago", "Info/Date", "Notice", "Item name"]

# Set alignments for few columns
table.align['Shipped ago'] = 'r'
table.align['Item name'] = "l"

# Put data from file into list
pkgs = []
for item in content:
    track_no, pkg_date, pkg_name = item.split(' - ')
    pkgs.append((track_no, pkg_date, pkg_name.rstrip()))


diff_track_no = False

# Initialize table for different tracking codes and set titles
diff_tbl = PrettyTable()
diff_tbl.field_names = [
    "Tracking #", "Shipped ago", "Item name"]

# Set alignments for one column
diff_tbl.align['Shipped ago'] = 'r'

# Make requests to check package status
for track_no, pkg_date, pkg_name in pkgs:
    send_date = parse(pkg_date, dayfirst=True)
    shipped_ago = (now - send_date).days

    if len(track_no) != 13:
        diff_tbl.add_row([track_no, shipped_ago, pkg_name])
        diff_track_no = True
        continue

    r = requests.get(
        'http://www.posta.com.mk/tnt/api/query?id=%s' % track_no)

    # Convert xml data to dict
    req_data = xmltodict.parse(r.text)

    # Get required data
    array_of_tracking_data = req_data['ArrayOfTrackingData']

    # Check if there is no package data
    # and add in table without Info/Data & Notice
    if not array_of_tracking_data:
        table.add_row(
            [track_no, shipped_ago, "", "", pkg_name])
        continue

    # Get tracking data per package
    tracking_data = array_of_tracking_data['TrackingData']

    # Get latest tracking data pre package
    try:
        # Tracking data it's a list when there is multiple items
        # Get only the latest item/status
        package = list(tracking_data[-1].items())
    except KeyError:
        # Tracking data it's not a list when there is only one item
        package = list(tracking_data.items())

    # Get datetime format, if there is midnight get only date
    dt_format = '%d.%m.%Y'
    pkg_date = parse(package[3][1])
    if pkg_date.time() != time(0, 0):
        dt_format = '%d.%m.%Y %H:%M:%S'

    # Get data from post office
    pkg_date = parse(package[3][1]).strftime(dt_format)
    pkg_notice = package[4][1]

    # Add package data into table
    table.add_row([track_no, shipped_ago, pkg_date, pkg_notice, pkg_name])

# Sort by shipped dates ago
table.sortby = "Shipped ago"
diff_tbl.sortby = "Shipped ago"

# Show table in console
print()
print(table)
print()
if diff_track_no:
    print(diff_tbl)
    print()
