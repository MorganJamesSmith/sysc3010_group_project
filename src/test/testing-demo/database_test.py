#! /usr/bin/env python3

#
# file name: database_test
# Description: Database integrity test code second demo 
# Author(s): Sunjeevani Pujari
#

from database_code import *

badge_id = bytes.fromhex("68091a96e619ad7997099f16c64b5e17")

#exit loop
exitnode = "North exit"
employee_id = database_test.accessrequest('exit',badge_id)
print(f"employee ID of employee requesting exit is:",employee_id)
#logging information for exit process
database_test.exit_log(employee_id,exitnode)

#entry loop
entrynode = "Sounth entry"
employee_id ,access_date,status,validity= database_test.accessrequest('entry',badge_id)
print(f"employee ID of employee requesting entry is:",employee_id)
#logging information for entry process
temp_reading = 37
status = "authorized"
database_test.entry_log(employee_id,entrynode,temp_reading,status)
