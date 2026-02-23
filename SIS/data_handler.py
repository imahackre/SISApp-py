import csv
import os
import re

class DataHandler:
    """Handles CSV file operations for database entities.
    
    Provides methods to load and save data to CSV files with automatic
    file creation and header management.
    """
    def __init__(self, filename, fieldnames):
        self.filename = filename
        self.fieldnames = fieldnames

        if not os.path.exists(self.filename):
            with open(self.filename, mode = 'w', newline = '') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def load_data(self):
        with open(self.filename, mode = 'r', newline='') as f:
            return list(csv.DictReader(f))
        
    def save_data(self, data_list):
        with open(self.filename, mode = 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(data_list)

def validate_student_id(student_id):
    pattern = r"^\d{4}-\d{4}$"
    return bool(re.match(pattern, student_id))
    

COLLEGE_FIELDS = ['code', 'name']
PROGRAM_FIELDS = ['code', 'name', 'college_code']
STUDENT_FIELDS = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']

college_db = DataHandler('colleges.csv', COLLEGE_FIELDS)
program_db = DataHandler('programs.csv', PROGRAM_FIELDS)
student_db = DataHandler('students.csv', STUDENT_FIELDS)