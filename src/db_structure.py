#! /usr/bin/env python3

#
# file name: db_structure
# Description: Database structure code for the system 
# Author(s): Sunjeevani Pujari
#

import sqlite3
import time
from datetime import date


class DataBase:
    def __init__(self):
        # Connecting to project database
        self.database = sqlite3.connect('security_system.db')
        self.cursor = self.database.cursor()
        print('SQLite Connection to database successful!\n')

    #adding tables to the database     
    def creating_db(self):
        
        #creating nfc_and_employee_id table
        nfc = 'CREATE TABLE nfc_and_employee_id(nfc_id BLOB NOT NULL, employee_id INTEGER NOT NULL);'
        self.cursor.execute(nfc)
        self.database.commit()
        
        #creating employee_info table
        info = '''CREATE TABLE employee_info(employee_id INTEGER NOT NULL, first_name TEXT NOT NULL,
        middle_name TEXT, last_name TEXT NOT NULL, admin TEXT NOT NULL, FOREIGN KEY(employee_id) REFERENCES nfc_and_employee_id (employee_id));'''
        self.cursor.execute(info)
        self.database.commit()

        #creating node_info table
        node = 'CREATE TABLE node_info(node_id INTEGER NOT NULL, node_type TEXT NOT NULL, address TEXT NOT NULL, location TEXT NOT NULL);'
        self.cursor.execute(node)
        self.database.commit()

        #creating access_summary table
        summary = '''CREATE TABLE access_summary(transaction_id INTEGER NOT NULL, employee_id INTEGER NOT NULL,
        access_type TEXT NOT NULL, access_datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, access_node INTEGER NOT NULL, temp_reading NUMERIC NOT NULL, status TEXT NOT NULL,validity INTEGER NOT NULL)'''
        self.cursor.execute(summary)
        self.database.commit()
        
        #creating unauthorized_employee table
        unauthorized = 'CREATE TABLE unauthorized_employee(employee_id INT, temp_reading NUM, quaratine_start_date NOT NULL DEFAULT CURRENT_TIMESTAMP);'
        self.cursor.execute(unauthorized)
        self.database.commit()
        
        #creating access_exit table
        #exit = 'CREATE TABLE access_exit(employee_id INTEGER NOT NULL, exit_datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, exit_node TEXT NOT NULL);'
        #self.cursor.execute(exit)
        #self.database.commit()
        
    
    def close_db(self):
        if (self.database):
            self.database.close()
            print("\n\nSQLite connection is closed")
