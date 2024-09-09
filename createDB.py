# Import required modules
import csv
import sqlite3

# Connecting to the geeks database
connection = sqlite3.connect("data.db")

# Creating a cursor object to execute
# SQL queries on a database table
cursor = connection.cursor()

# SQL query to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS cards (
    name TEXT PRIMARY KEY,
    quantity INTEGER NOT NULL
);
"""

# Creating the table into our
# database
cursor.execute(create_table_query)

# Path to the CSV file
csv_file_path = "data.csv"

# Initialize an empty list to store the rows
data_array = []

count = 0

# Open and read the CSV file
with open(csv_file_path, newline="", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file)

    # Iterate over each row in the CSV file
    for row in reader:
        # Append the row to the data_array
        data_array.append(row)

# Print the resulting array
# print(data_array)


for row in data_array[1:]:  # Skip the header row
    name = row[0].lower()
    quantity = int(row[1])

    # Insert the data, incrementing the quantity if the name already exists
    insert_or_update_query = """
    INSERT INTO cards (name, quantity)
    VALUES (?, ?)
    ON CONFLICT(name) DO UPDATE SET quantity = quantity + excluded.quantity;
    """
    cursor.execute(insert_or_update_query, (name, quantity))

    count += 1


# Committing the changes
connection.commit()

# closing the database connection
connection.close()

print("Database populated with {} entries.".format(count))
