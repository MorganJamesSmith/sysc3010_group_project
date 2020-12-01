#! /usr/bin/env python3

#
# file name: create_database
# Description: Creates Database for final demo
# Author(s): Sunjeevani Pujari
#

from db_structure import DataBase

db = DataBase()

#creating database 
db.creating_db()

#adding node info
db.add_nodes()

#adding info to database
db.add_entries()

#closing connection
db.close_db()
