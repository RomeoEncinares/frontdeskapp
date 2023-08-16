import sqlite3
from datetime import datetime

def main():
    
    # Connect to the SQLite database
    db_connection = sqlite3.connect('FrontDeskApp.db')

    # Create a cursor object to interact with the database
    cursor = db_connection.cursor()

    while True:
        print("###################################")
        print("### Welcome to the FrontDeskApp ###")
        print("###################################")
        print("Actions: ")
        print("1: Select Storage")
        print("2: View Storage Capacity")
        print("3: Create Storage Capacity")
        print("4: View Storage History")
        initial_input = int(input("Select Action: "))
        if initial_input == 1:
            table = printStorage(cursor)
            print("Actions: ")
            print("1: Insert Box")
            print("2: Remove Box")
            size_mapping = {1: "small", 2: "medium", 3: "large"}
            try:
                initial_input = int(input("Select Action: "))
            except:
                print("Invalid Input. Try Again.")
                continue
            if initial_input == 1:
                displayBoxChoices() ### 1 - small, 2 - medium, 3- large
                try: 
                    size = int(input("Select box size: "))
                except:
                    print("Invalid Input. Try Again.")
                    continue
                size_label = size_mapping.get(size, "unknown") # Default to "unknown" if size is not 1, 2, or 3
                if getStorageSize(cursor, table, size_label):
                    first_name, last_name, phone_number, input_date, retrieve_date = getPersonalInfo()
                    insert_query = f"INSERT INTO {table} (box_size, first_name, last_name, phone_number, input_date, retrieve_date) VALUES (?, ?, ?, ?, ?, ?)"
                    data = (size_label, first_name, last_name, phone_number, input_date, retrieve_date)
                    cursor.execute(insert_query, data)
                    db_connection.commit()
                    print("#### Box Successfully Added ###")
                    showStorage(cursor, table)
                else:
                    print(f"!!!!!! The storage for {size_label} is full !!!!!!")
            
            ### Retrieving boxes
            elif initial_input == 2:
                displayBoxChoices()
                try: 
                    size = int(input("Select box size: "))
                except:
                    print("Invalid Input. Try Again.")
                    continue
                size_label = size_mapping.get(size, "unknown") # Default to "unknown" if size is not 1, 2, or 3
                showSpecificStorage(cursor, table, size_label)
                index = int(input("Select the index of the box that will retreived: "))

                select_query = f"SELECT * FROM {table} WHERE box_id = {index}"
                cursor.execute(select_query)
                row_to_move = cursor.fetchone()
                print(row_to_move)

                if row_to_move:
                    now = datetime.now()
                    retrieve_date = now.strftime("%Y-%m-%d")
                    modified_row = list(row_to_move)
                    modified_row[6] = retrieve_date
                    insert_query = "INSERT INTO storage_1_history (box_size, first_name, last_name, phone_number, input_date, retrieve_date) VALUES (?, ?, ?, ?, ?, ?)"
                    print((modified_row[1:]))
                    cursor.execute(insert_query, (modified_row[1:]))
                    db_connection.commit()
                    
                    delete_query = f"DELETE FROM storage_1 WHERE box_id = {index}"
                    cursor.execute(delete_query)
                    db_connection.commit()

        elif initial_input == 2:
            getStorageAvailability(cursor)

        elif initial_input == 3:
            tableName = str(input("Enter new storage facility name (i.e storage_2): "))
            createStorageFacility(db_connection, cursor, tableName)

        elif initial_input == 4:
            table = printHistory(cursor)
            print("Select Storage History: ")
            getStorageHistory(cursor, table)

### Function to create a storage facility
def createStorageFacility(db_connection, cursor, tableName):
    query = f"""
    CREATE TABLE "{tableName}" (
        "box_id"	INTEGER,
        "box_size"	TEXT NOT NULL CHECK("box_size" IN ('small', 'medium', 'large')),
        "first_name"	TEXT NOT NULL,
        "last_name"	TEXT NOT NULL,
        "phone_number"	TEXT NOT NULL,
        "input_date"	TEXT NOT NULL,
        "retrieve_date"	TEXT,
        PRIMARY KEY("box_id")
    );
    """
    query_history = f"""
    CREATE TABLE "{tableName}_history" (
        "box_id"	INTEGER,
        "box_size"	TEXT NOT NULL CHECK("box_size" IN ('small', 'medium', 'large')),
        "first_name"	TEXT NOT NULL,
        "last_name"	TEXT NOT NULL,
        "phone_number"	TEXT NOT NULL,
        "input_date"	TEXT NOT NULL,
        "retrieve_date"	TEXT NOT NULL,
        PRIMARY KEY("box_id")
    );
    """
    cursor.execute(query)
    cursor.execute(query_history)
    db_connection.commit()

### Function to print and select a storage facility
def printStorage(cursor):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%\_history' ESCAPE '\\';"
    cursor.execute(query)
    tables = cursor.fetchall()

    print("Available tables:")
    for idx, table in enumerate(tables, start=1):
        print(f"{idx}. {table[0]}")

    selection = int(input("Select a table by entering its number: ")) - 1

    if 0 <= selection < len(tables):
        selected_table = tables[selection][0]
        print(f"{selected_table} selected")
    else:
        print("Invalid selection.")
    
    return selected_table

### Function to print all storage facility history (removed boxes)
def printHistory(cursor):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%\_history' ESCAPE '\\';"
    cursor.execute(query)
    tables = cursor.fetchall()

    print("Available tables:")
    for idx, table in enumerate(tables, start=1):
        print(f"{idx}. {table[0]}")

    selection = int(input("Select a table by entering its number: ")) - 1

    if 0 <= selection < len(tables):
        selected_table = tables[selection][0]
        print(f"{selected_table} selected")
    else:
        print("Invalid selection.")
    
    return selected_table

### Function to get removed boxes in storage facility history
def getStorageHistory(cursor, table):
    query = f"SELECT * FROM {table};"
    cursor.execute(query)

    # Fetch and print the results
    results = cursor.fetchall()
    for row in results:
        print(row)

### Function to get storage facilities
def getStorageAvailability(cursor):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%\_history' ESCAPE '\\';"
    cursor.execute(query)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        sizes_count = getBoxesCount(cursor, table_name)
        availability = calculateAvailability(sizes_count)
        print(f"Table: {table_name}")
        for size, count in availability.items():
            print(f"{size.capitalize()} Availability: {count}")

### Function to count number of boxes in a storage facility
def getBoxesCount(cursor, table_name):
    sizes = ['small', 'medium', 'large']
    sizes_count = {size: 0 for size in sizes}

    for size in sizes:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE box_size = ?", (size,))
        size_count = cursor.fetchone()[0]
        sizes_count[size] = size_count

    return sizes_count

### Function to count number of availability in a storage facility
def calculateAvailability(sizes_count):
    max_storage = {'small': 46, 'medium': 14, 'large': 12}
    availability = {size: max_storage[size] - count for size, count in sizes_count.items()}
    return availability

### Function to print choices
def displayBoxChoices():
    print("### Insert Box Selected ###")
    print("Box Sizes:")
    print("1: Small Box")
    print("2: Medium Box")
    print("3: Large Box")

### Function to get personalInfo
def getPersonalInfo():
    print("Enter the details:")
    first_name = str(input("First Name: "))
    last_name = str(input("Last Name: "))
    phone_number = str(input("Phone Number: "))
    now = datetime.now()
    input_date = now.strftime("%Y-%m-%d")
    retrieve_date = None

    return first_name, last_name, phone_number, input_date, retrieve_date

### Function to get the last 5 box records
def showStorage(cursor, table):
    select_query = f"SELECT * FROM {table} ORDER BY box_id desc LIMIT 5"
    cursor.execute(select_query)

    # Fetch and print the results
    results = cursor.fetchall()
    for row in results:
        print(row)

### Function to get specific box size ecords
def showSpecificStorage(cursor, table, area):
    select_query = f"SELECT * FROM {table} WHERE box_size = '{area}'"
    cursor.execute(select_query)

    # Fetch and print the results
    results = cursor.fetchall()
    for row in results:
        print(row)

### Function to check if box size storage is full
def getStorageSize(cursor, table, size):
    query = f"SELECT COUNT(*) FROM {table} WHERE box_size = '{size}';"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    
    if count < 10:
        return True
    else:
        return False
    
if __name__ == "__main__":
    main()
