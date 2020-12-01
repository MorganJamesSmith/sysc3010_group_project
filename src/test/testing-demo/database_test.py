#! /usr/bin/env python3

#
# file name: database_test
# Description: Database integrity test code second demo 
# Author(s): Sunjeevani Pujari
#

import sys
sys.path.append("../../")

from database_code import DataBase

db = DataBase()


db.creating_db()

badge_id1 = bytes.fromhex("68091a96e619ad7997099f16c64b5e17")

badge_id2 = bytes.fromhex("63d584ccd569b75faf69d1a8e230efc7")

#adding info to database
print()
print("Test1: adding entries to database")
db.add_entries(badge_id1,1)
db.add_entries(badge_id2,2)

#exit loop
print()
print()
print("Test2: Exit loop retrieving and uploading data")
print("Starting Exit Loop")
print (f"Sample Badge ID being used is:", badge_id1)
exitnode = "North exit"
employee_id1 = db.accessrequest("exit",badge_id1)
print(f"Employee ID retrieved is:", employee_id1)
print(f"Employee ID of employee requesting exit is",employee_id1,"at node",exitnode)
#logging information for exit process
db.exit_log(employee_id1,exitnode)

#entry loop
print()
print()
print("Test3: Entry loop retrieving and uploading data")
print("Starting Entry Loop")
print (f"Sample Badge ID being used is:", badge_id2)
entrynode = "South entry"
employee_id2,accessDate,status= db.accessrequest("entry",badge_id2)
print(f"Employee ID retrieved is:", employee_id2)
print(f"Employee ID of employee requesting entry is:",employee_id2)
#logging information for entry process
temp_reading = 37.0
status = "authorized"
db.entry_log(employee_id2,entrynode,temp_reading,status)

db.close_db()
