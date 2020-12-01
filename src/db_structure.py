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
        
    #adding entires to nfc_and_employee_id table
    def add_entries(self):
        try:
            with open("./stub_text/nfc_id_address.txt", "r") as idfile:
                badge_id1 = bytes.fromhex(idfile.readline())
                badge_id2 = bytes.fromhex(idfile.readline())
                badge_id3 = bytes.fromhex(idfile.readline())
                badge_id4 = bytes.fromhex(idfile.readline())
                badge_id5 = bytes.fromhex(idfile.readline())
        except FileNotFoundError as e:
            print("RC522: Could not open testcase files.")
            exit(1)
        
        #badge_id1 = bytes.fromhex("68091a96e619ad7997099f16c64b5e17")
        #badge_id2 = bytes.fromhex("63d584ccd569b75faf69d1a8e230efc7")
        #badge_id3 = bytes.fromhex("86878fa2296fdfc32fe278dfd45e6400")
        #badge_id4 = bytes.fromhex("4a5ca17b0fe64b9c8b9859577f9f7960")
        #badge_id5 = bytes.fromhex("3f8319465ef0e3927cd36f29a7f424a1")
        data_tuple =(badge_id1,1)
        self.cursor.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        data_tuple =(badge_id2,2)
        self.cursor.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        data_tuple =(badge_id3,3)
        self.cursor.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        data_tuple =(badge_id4,4)
        self.cursor.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        data_tuple =(badge_id5,5)
        self.cursor.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        i = 1
        for i in range (6):
            if i ==1:
                data_tuple1 =(1,i,"exit",3,0,"authorized",0)
                self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,temp_reading,status,validity) VALUES (?,?,?,?,?,?,?)",data_tuple1)
                self.database.commit()
            elif i == 2:
                data_tuple2 =(2,i,"entry",1,36,"authorized",0)
                self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,temp_reading,status,validity) VALUES (?,?,?,?,?,?,?)",data_tuple2)
                self.database.commit()
            elif i == 3:
                data_tuple3 =(3,i,"entry",2,36.5,"authorized",0)
                self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,temp_reading,status,validity) VALUES (?,?,?,?,?,?,?)",data_tuple3)
                self.database.commit()
            elif i == 4:
                data_tuple4 =(4,i,"exit",4,0,"authorized",0)
                self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,temp_reading,status,validity) VALUES (?,?,?,?,?,?,?)",data_tuple4)
                self.database.commit()
            elif i == 5:
                data_tuple5 =(5,i ,"entry",1,38,"unauthorized",3)
                self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,temp_reading,status,validity) VALUES (?,?,?,?,?,?,?)",data_tuple5)
                self.database.commit()
                
    #adding node info
    def add_nodes(self):
        data_tuple = (1,'entry','Main Entrance','North side')
        self.cursor.execute("INSERT INTO node_info VALUES (?,?,?,?)",data_tuple)
        self.database.commit()
        data_tuple = (2,'entry','South Entrance','South side')
        self.cursor.execute("INSERT INTO node_info VALUES (?,?,?,?)",data_tuple)
        self.database.commit()
        data_tuple = (3,'exit','Main Exit','North side')
        self.cursor.execute("INSERT INTO node_info VALUES (?,?,?,?)",data_tuple)
        self.database.commit()
        data_tuple = (4,'exit','South Exit','South side')
        self.cursor.execute("INSERT INTO node_info VALUES (?,?,?,?)",data_tuple)
        self.database.commit()
        
    def close_db(self):
        if (self.database):
            self.database.close()
            print("\n\nSQLite connection is closed")
