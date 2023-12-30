
import sqlite3
import json
import re
import csv
from collections import Counter

# Creating Connection & Cursor
conn = sqlite3.connect("chatbot.db")
curs = conn.cursor()

# Checking if Tables are existed
curs.execute(""" DROP TABLE IF EXISTS Patients""")
curs.execute(""" DROP TABLE IF EXISTS Diseases""")
curs.execute(""" DROP TABLE IF EXISTS Prognosis_Reports""")

# Creating Tables
# Creating [Patients] Table
curs.execute('''
    CREATE TABLE Patients (
        p_id INTEGER NOT NULL UNIQUE,
        p_name TEXT NOT NULL,
        age INTEGER,
        phone INTEGER UNIQUE,
        email TEXT UNIQUE,
        sex TEXT,
        PRIMARY KEY(p_id)
    );
''')

# Inserting in [Patients] Table
json_file_path = r"C:\Users\Hp\Downloads\aibot\aibot\data.json"

# Read data from the JSON file
with open(json_file_path, 'r') as file:
    diseases_data = json.load(file)

# Creating [Diseases] Table
curs.execute('''
    CREATE TABLE Diseases (
        d_id INTEGER NOT NULL UNIQUE,
        d_name TEXT NOT NULL,
        description TEXT,
        symptoms TEXT,
        precautions TEXT,
        PRIMARY KEY(d_id)
    );
''')

for disease in diseases_data[0]:
    curs.execute('''
        INSERT INTO Diseases(d_id, d_name, description, symptoms, precautions)
        VALUES(?, ?, ?, ?, ?);
    ''', (disease['d_id'], disease['d_name'], disease['description'], disease['symptoms'], disease['precautions']))

# Creating [Prognosis_Report] Table

# Interactive Chat
print("Welcome to the Health Chatbot!")
patient_name = input("Enter your name: ")

# Get valid age input using regular expression
while True:
    try:
        patient_age = int(input("Enter your age: "))
        if not 0 < patient_age <= 150:
            raise ValueError("Age out of range.")
        break
    except ValueError as e:
        print(f"Error: {e}")

# Get valid sex input using regular expression
while True:
    patient_sex = input("Enter your sex (Male/M or Female/F): ").lower()
    if re.match(r'^(male|m|female|f)$', patient_sex):
        break
    else:
        print("Error: Invalid sex. Please enter Male/M or Female/F.")

# Get valid phone number input using regular expression
while True:
    try:
        patient_phone = int(input("Enter your phone number: "))
        if not re.match(r'^\d{10}$', str(patient_phone)):
            raise ValueError("Phone number must be a 10-digit integer.")
        break
    except ValueError as e:
        print(f"Error: {e}")

# Get valid email input using regular expression
while True:
    patient_email = input("Enter your email address: ")
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', patient_email):
        break
    else:
        print("Error: Invalid email format.")

# Continue with the rest of the interactive chat...

# Inserting patient information into [Patients] Table
curs.execute('''
    INSERT INTO Patients(p_name, age, sex, phone, email)
    VALUES(?, ?, ?, ?, ?);
''', (patient_name, patient_age, patient_sex, patient_phone, patient_email))
patient_id = curs.lastrowid

# Getting user symptoms
user_symptoms = input("Enter your symptoms (comma-separated): ")

# Use a set for symptoms
symptoms_list = {symptom.strip() for symptom in user_symptoms.split(',')}

# Get the list of available symptoms from the dataset
csv_file_path = "unique_symptoms.csv"
with open(csv_file_path, newline="") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    available_symptoms = [row[0] for row in reader]

# Counting occurrences of each user input symptom
symptom_counter = Counter(symptoms_list)

# Building the SQL query for symptom matching
sql_query = "SELECT d_id, d_name, description, precautions FROM Diseases WHERE "
for symptom, count in symptom_counter.items():
    sql_query += f"symptoms LIKE '%{symptom}%' AND " * count

# Removing the trailing "AND" from the query
sql_query = sql_query.rstrip(" AND ")

# Executing the query
curs.execute(sql_query)
result = curs.fetchall()
import textdistance

def correct_spelling(symptom, available_symptoms):
    # Get the best match and its score
    best_match, score = max((s, textdistance.jaccard(symptom, s)) for s in available_symptoms)
    
    # If the score is above a certain threshold, consider it a match
    if score >= 0.8:  # You can adjust the threshold as needed
        return best_match
    else:
        return None

# ...

if not result:
    print("No matching diseases found for the given symptoms.")
    print("Available Symptoms:", ", ".join(available_symptoms))

    # Getting user symptoms again
    user_symptoms = input("Enter your symptoms from the list above (comma-separated): ")

    # Use a set for symptoms
    symptoms_list = {symptom.strip() for symptom in user_symptoms.split(',')}

    # Correct spelling for each user input symptom
    corrected_symptoms = [correct_spelling(symptom, available_symptoms) or symptom for symptom in symptoms_list]

    # Counting occurrences of each corrected symptom
    symptom_counter = Counter(corrected_symptoms)

    # Building the SQL query for symptom matching
    sql_query = "SELECT d_id, d_name, description, precautions FROM Diseases WHERE "
    for symptom, count in symptom_counter.items():
        sql_query += f"symptoms LIKE '%{symptom}%' AND " * count

    # Removing the trailing "AND" from the query
    sql_query = sql_query.rstrip(" AND ")

    # Executing the query
    curs.execute(sql_query)
    result = curs.fetchall()

    if not result:
        print("No matching diseases found for the given symptoms. Ending.")
    else:
        # Displaying matched diseases
        for row in result:
            disease_id, disease_name, description, precautions = row
            print(f"\nDisease ID: {disease_id}")
            print(f"Disease Name: {disease_name}")
            print(f"Description: {description}")
            print(f"Precautions: {precautions}")
else:
    # Displaying matched diseases
    for row in result:
        disease_id, disease_name, description, precautions = row
        print(f"\nDisease ID: {disease_id}")
        print(f"Disease Name: {disease_name}")
        print(f"Description: {description}")
        print(f"Precautions: {precautions}")

# Ask the user to select a disease


# Additional logic to handle the user's choice goes here...

# Closing the Connection
conn.commit()
conn.close()
