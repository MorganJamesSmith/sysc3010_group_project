#! /usr/bin/env python3

#
# file name: database_test
# Description: Database integrity test code second demo 
# Author(s): Sunjeevani Pujari
#

from database_code import DataBase

badge_id = bytes.fromhex("68091a96e619ad7997099f16c64b5e17")

#exit loop
exitnode = "North exit"
employee_id = DataBase.accessrequest("exit",badge_id)
print(f"employee ID of employee requesting exit is:",employee_id)
#logging information for exit process
DataBase.exit_log(employee_id,exitnode)

#entry loop
entrynode = "Sounth entry"
employee_id ,access_date,status,validity= DataBase.accessrequest("entry",badge_id)
print(f"employee ID of employee requesting entry is:",employee_id)
#logging information for entry process
temp_reading = 37
status = "authorized"
DataBase.entry_log(employee_id,entrynode,temp_reading,status)
