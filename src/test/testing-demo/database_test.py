#! /usr/bin/env python3

#
# file name: database_test
# Description: Database integrity test code second demo 
# Author(s): Sunjeevani Pujari
#

from database_code import DataBase

db = DataBase()

badge_id1 = bytes.fromhex("68091a96e619ad7997099f16c64b5e17")

badge_id2 = bytes.fromhex("63d584ccd569b75faf69d1a8e230efc7")

#adding info to database
db.add_entries(badge_id1,1)
db.add_entries(badge_id2,2)

#exit loop
exitnode = "North exit"
employee_id = db.accessrequest("exit",badge_id)
print(f"employee ID of employee requesting exit is:",employee_id)
#logging information for exit process
db.exit_log(employee_id,exitnode)

#entry loop
entrynode = "Sounth entry"
employee_id ,access_date,status,validity= db.accessrequest("entry",badge_id)
print(f"employee ID of employee requesting entry is:",employee_id)
#logging information for entry process
temp_reading = 37.0
status = "authorized"
db.entry_log(employee_id,entrynode,temp_reading,status)
