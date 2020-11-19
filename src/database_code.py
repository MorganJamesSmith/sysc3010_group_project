#! /usr/bin/env python3

#
# file name: database_code
# Description: Database function code for second test demo 
# Author(s): Sunjeevani Pujari
#

import sqlite3
import time
from datetime import date

class DataBase:
    def __init__(self):
        try:
            # Connecting to project database
            self.database = sqlite3.connect('project.db')
            print('Connection to database successful!')
        except sqlite3.Error as error:
                print("Error while working with SQLite", error)
                
    def accessrequest(self,accessType,badge_id):
        try:
            self.badge_id = badge_id
            #Variables needed from database
            self.database.execute("SELECT employee_id FROM nfc_and_employee_id WHERE nfc_id =?", self.badge_id)
            employeeId = self.database.fetchone()[0]
            
            if employeeId == NULL:
                employeeId = 0
                return employeeId
            elif accessType == "exit":
                #if AccessRequestMessage is from exit node, all we need is to get employee ID
                return employeeId
            #if AccessRequestMessage is from entry node, we need information about employees most recent entry attempt
            self.database.execute("SELECT access_date FROM access_entry WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", employeeId)
            accessDate = self.database.fetchone()[0]
            selfdatabase.execute("SELECT status FROM access_entry WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", employeeId)
            statusType = self.database.fetchone()[0]
            self.database.execute("SELECT validity FROM access_entry WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", employeeId)
            validity = self.database.fetchone()[0]
            return employeeID, accessDate,statusType, validity
            
        finally:
            if (self.database):
                self.database.close()
                print("sqlite connection is closed")
    def exit_log(self,employeeId,exitnode):
        self.employeeID = employeeId #INT value of employee ID acquired from the nfc ID in the AccessRequestMessage 
        self.exitnode = exitnode #TEXT value of the entry node requesting entry
        #fields saved to log exit access of employee
        self.database.execute("INSERT INTO access_exit (employee_id, exit_time,exit_date,exit_node) VALUES (?,?,?,?)",self.employeeId,time('now'),date('now'),self.exitnode)
        self.database.commit()
        self.database.execute("SELECT * FROM access_exit WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", employeeId)
        print ("data added to the database is:",database.fetchone())
        
        if (self.database):
            self.database.close()
            print("sqlite connection is closed")
   
    #entry
    def entry_log(self,employeeId,entrynode,tempReading,status):
        self.employeeId = employeeId #INT value of employee ID acquired from the nfc ID in the AccessRequestMessage 
        self.entrynode = entrynode #TEXT value of the entry node requesting entry
        self.tempReading= tempReading #NUMERIC value of the employees recorded Temp 
        self.status = status #TEXT value of the status of employee 
        #fields saved to log exit access of employee
        self.database.execute("INSERT INTO access_entry (employee_id,access_time,access_date,access_node,in_range,temp_reading,status,validity) VALUES(?,?,?,?,?,?,?,?)",
                         self.employeeId,time('now'),date('now'),self.entrynode,'Y',self.tempReading,self.status,0)
        self.database.commit()
        self.database.execute("SELECT * FROM access_entry WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", employeeId)
        print ("data added to the database is:",database.fetchone())
        if (self.database):
            self.database.close()
            print("sqlite connection is closed")
    
    #adding entires to nfc_and_employee_id table
    def add_entries(self,badge_id,employee_id):
        data_tuple =(badge_id,employee_id)
        self.database.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",data_tuple)
        self.database.commit()
        
    #adding tables to the database     
    def creating_db(self):
        #creating access_entry table
        entry = '''CREATE TABLE access_entry(employee_id INTEGER NOT NULL, access_time TIME, access_date DATE,
        access_node TEXT NOT NULL, in_range TEXT NOT NULL, temp_reading NUMERIC NOT NULL, status TEXT NOT NULL,validity INTEGER NOT NULL);'''
        self.database.execute(entry)
        self.database.commit()
        
        #creating employee_info table
        info = '''CREATE TABLE employee_info(employee_id INTEGER NOT NULL, first_name TEXT NOT NULL, middle_name TEXT, last_name TEXT NOT NULL,
        admin TEXT NOT NULL, FOREIGN KEY(employee_id) REFERENCES nfc_and_employee_id (employee_id));'''
        self.database.execute(info)
        self.database.commit()
        
        #creating unauthorized_employee table
        unauthorized = '''CREATE TABLE unauthorized_employee(employee_id INT, temp_reading NUM, start_of_quarantine_date DATE);'''
        self.database.execute(unauthorized)
        self.database.commit()
        
        #creating access_exit table
        exit = '''CREATE TABLE access_exit(employee_id INTEGER NOT NULL, exit_time TIME, exit_date DATE, exit_node TEXT NOT NULL);'''
        self.database.execute(exit)
        self.database.commit()
        
        #creating nfc_and_employee_id table
        nfc = 'CREATE TABLE nfc_and_employee_id(nfc_id BLOB NOT NULL, employee_id INTEGER NOT NULL);'
        self.database.execute(nfc)
        self.database.commit()
