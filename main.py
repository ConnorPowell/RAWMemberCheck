import configparser, psycopg2
import xml.etree.ElementTree as ET
import urllib.request as request
from prettytable import PrettyTable

config = configparser.ConfigParser()
config.read("check.config")

db_host = config["database"]["host"]
db_port = config["database"]["port"]
db_name = config["database"]["name"]
db_user = config["database"]["user"]
db_password = config["database"]["password"]

api_url = "https://www.warwicksu.com/membershipapi/listmembers/" + config["su"]["key"] + "/"
members_xml = request.urlopen(api_url).read()
root = ET.fromstring(members_xml);

members = {}
for member in root:
	info = {}
	for part in member:
		info[part.tag] = part.text
	members[info["UniqueID"]] = info

print("Fetched", len(members), "current RAW members according to the SU...")

connection = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
cursor = connection.cursor()

date = input("Show start date (in form YYYY-MM-DD) to search from: ")

cursor.execute("""SELECT web_shows.name as showname, web_members.name as name, web_members.id as id
	FROM web_shows, web_show_presenters, web_members
	WHERE web_shows.showid = web_show_presenters.showid
		AND web_show_presenters.username = web_members.username
		AND web_shows.date_start >= %s""", (date,))

print("These members have no membership :(")
table = PrettyTable()

table.field_names = ["ID", "Name", "Showname"]

for row in cursor.fetchall():
	if not row[2] in members:
		table.add_row([row[2], row[1], row[0]])

print(table)