import sqlite3



def add_or_update_quantity(db_name: str, table_name: str,query: str) -> str:
  
  """
  Adds a quantity to a record in the database. If the record does not exist, it creates a new one.
  If the record already exists, it updates the quantity.

  :param db_name: The SQLite database file name (e.g., 'data.db').
  :param table_name: The name of the table to query (e.g., 'cards').
  :param name: The name of the item to add to.
  :param query: The card to selectand the quantity to add to the item's current quantity.
  :return: A message indicating the result of the operation.
  """
  # Connect to the SQLite database
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  try:
    # Split the query into name and quantity_to_add
    name, quantity_to_add = query.split(",", 1)
    
    # Check if the name is not null or empty
    if not name.strip():
      raise ValueError("The name part of the query is empty")
    
    # Check if the quantity is a valid integer
    quantity_to_add = int(quantity_to_add.strip())

  except ValueError as e:
        # Handle both cases: empty name and non-integer quantity
        print(e)
        return f"An error occurred. Check your query format: [card,quantity]!"
  
  #Accessing DB
  try:
      # Convert the name to lowercase for consistency
      lower_name = name.lower()
      
      # Check if the record exists and get the current quantity
      select_query = f"SELECT quantity FROM {table_name} WHERE LOWER(name) = LOWER(?)"
      cursor.execute(select_query, (lower_name,))
      result = cursor.fetchone()

      if result:
          # If the record exists, update the quantity
          current_quantity = result[0]
          new_quantity = current_quantity + quantity_to_add

          update_query = f"UPDATE {table_name} SET quantity = ? WHERE LOWER(name) = LOWER(?)"
          cursor.execute(update_query, (new_quantity, lower_name))

          conn.commit()
          
          return f"Updated '{name}': quantity {current_quantity} -> {new_quantity}"
      else:
          # If the record does not exist, insert a new one
          insert_query = f"INSERT INTO {table_name} (name, quantity) VALUES (?, ?)"
          cursor.execute(insert_query, (lower_name, quantity_to_add))

          conn.commit()

          return f"Added '{name}' with quantity {quantity_to_add}"

  except sqlite3.Error as e:
      return f"An error occurred: {e}"

  finally:
      # Ensure the connection is closed
      conn.close()

def subtract_quantity(db_name: str, table_name: str, query: str) -> str:
  """
  Subtracts a quantity from a record in the database and removes the record if the resulting quantity is 0 or less.

  :param db_name: The SQLite database file name (e.g., 'data.db').
  :param table_name: The name of the table to query (e.g., 'cards').
  :param name: The name of the item to subtract from.
  :param quantity_to_subtract: The quantity to subtract from the item's current quantity.
  """
  
  
  
  try:
    # Split the query into name and quantity_to_add
    name, quantity_to_subtract = query.split(",", 1)
    
    # Check if the name is not null or empty
    if not name.strip():
      raise ValueError("The name part of the query is empty")
    
    # Check if the quantity is a valid integer
    quantity_to_subtract = int(quantity_to_subtract.strip())

  except ValueError as e:
    # Handle both cases: empty name and non-integer quantity
    print(e)
    return f"An error occurred. Check your query format: [card,quantity]!"
  
  
  
  
  # Connect to the SQLite database
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  try:
      # Convert the name to lowercase for consistency
      lower_name = name.lower()

      # Check if the record exists and get the current quantity
      select_query = f"SELECT quantity FROM {table_name} WHERE LOWER(name) = LOWER(?)"
      cursor.execute(select_query, (lower_name,))
      result = cursor.fetchone()

      if result:
          current_quantity = result[0]

          # Calculate the new quantity after subtraction
          new_quantity = current_quantity - quantity_to_subtract

          if new_quantity > 0:
            # Update the record with the new quantity
            update_query = f"UPDATE {table_name} SET quantity = ? WHERE LOWER(name) = LOWER(?)"
            cursor.execute(update_query, (new_quantity, lower_name))
            
            conn.commit()
            
            return "Updated {}: quanity {} -> {}".format(name, current_quantity, new_quantity)
          else:
            # Remove the record from the table if the quantity is 0 or less
            delete_query = f"DELETE FROM {table_name} WHERE LOWER(name) = LOWER(?)"
            cursor.execute(delete_query, (lower_name,))
            
            conn.commit()
            
            return "Removed {}".format(name)
              
      else:
          return f"No record found for '{name}' to subtract the quantity."

  except sqlite3.Error as e:
      return f"An error occurred: {e}"

  # Commit the changes and close the connection
  conn.close()

def search_card(db_name, table_name, column_name, substring) -> str:
  """
  Select all rows from the specified table where the column contains a given substring.

  :param db_name: The SQLite database file name (e.g., 'data.db').
  :param table_name: The name of the table to query (e.g., 'cards').
  :param column_name: The name of the column to search (e.g., 'name').
  :param substring: The substring to search for within the column.
  :return: A list of tuples containing the matching rows.
  """
  
  formatted = []

  # Connect to the SQLite database
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  # SQL query to select all rows where the column contains the substring
  query = f"SELECT * FROM {table_name} WHERE {column_name} LIKE ?"

  # The '%' wildcard matches any sequence of characters
  search_pattern = f"%{substring}%"

  # Execute the query with the search pattern as the parameter
  cursor.execute(query, (search_pattern,))

  # Fetch all matching rows
  results = cursor.fetchall()

  # Close the connection
  conn.close()


  if len(results)==0:
    return "No results..."
  
  # Print the matching rows
  for row in results:
    #print(row)
    formatted.append("Found {} -> you have {}".format(row[0],row[1]))
    #print(formatted)
  
  return formatted

  
  
  
def search_card_exact_and_compare(db_name, table_name, column_name, file_path) -> str:
  """
  Compare rows in a text file with entries in the database and return matching rows.

  :param db_name: The SQLite database file name (e.g., 'data.db').
  :param table_name: The name of the table to query (e.g., 'cards').
  :param column_name: The name of the column to search (e.g., 'name').
  :param file_path: The path to the text file containing rows to compare.
  :return: A list of formatted strings containing the matching rows.
  """

  formatted = []
  
  # Connect to the SQLite database
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()

  try:
    file_path =  file_path.replace("\r", "")
    cards = file_path.split("\n")

    for card in cards:
      # Split the card into name and quantity
      name, quantity = card.split(",", 1)

      # Convert the name to lowercase for consistency
      lower_name = name.lower()

      # Check if the record exists and get the current quantity
      select_query = f"SELECT quantity FROM {table_name} WHERE LOWER({column_name}) = LOWER(?)"
      cursor.execute(select_query, (lower_name,))
      result = cursor.fetchone()

      if result:
        current_quantity = result[0]
        current_quantity = current_quantity - int(quantity.strip())
        formatted.append(f"Found \"{name}\": you need {current_quantity}")

  except Exception as e:
      return f"An error occurred: {e}"

  finally:
      # Close the database connection
      conn.close()

  return formatted if formatted else "No matches found."





#Example usage
db_name = 'data.db'
table_name = 'cards'
column_name = 'name'
substring = "island"
query="island, 11"
# file_path= "cards.txt"


#print(search_card(db_name, table_name, column_name, substring))

#print(subtract_quantity(db_name, table_name, query))

#print(add_or_update_quantity(db_name,table_name,query))

#compare_with_file(db_name,table_name, file_path)

#print(read_file_rows(file_path))

#print(search_card_exact_and_compare(db_name,table_name,column_name,file_path))