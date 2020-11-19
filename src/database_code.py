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
            self.database = sqlite3.connect('projectdatabase.db')
            print('Connection to database successful!')
        except sqlite3.Error as error:
                print("Error while working with SQLite", error)
                
    def accessrequest(self,accessType,badge_id):
        try:
            self.badge_id = badge_id
            #Variables needed from database
            self.database.execute("SELECT employee_id FROM employee_info WHERE nfc_id =?", self.badge_id)
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
    
    def add_entries(self,badge_id,employee_id):
        self.badge_id = badge_id
        self.employee_id = employee_id
        self.database.execute("INSERT INTO nfc_and_employee_id(nfc_id,employee_id) VALUES (?,?)",self.badge_id, self.employee_id)
        self.database.commit()
