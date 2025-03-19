import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import importlib.util
import sys

conn = pyodbc.connect('Driver={SQL Server};Server=NESMA\SQLEXPRESS;Database=BPI2013;Trusted_Connection=yes;')
cursor = conn.cursor()
def response_antipattern(log, event_a, event_b):
    query = (f"""
        SELECT count(distinct a.caseid) as total_cases 
        FROM {log} a 
        JOIN ( 
            SELECT a.[event] AS TaskA, b.[event] AS TaskB 
            FROM {log} a 
            JOIN {log} b ON a.[event] != b.[event] 
            WHERE a.[event] = '{event_a}' AND b.[event] = '{event_b}' 
            GROUP BY a.[event], b.[event] 
        ) x
        ON a.[event] = '{event_a}' 
        WHERE ( 
            EXISTS ( 
                SELECT 1 
                FROM {log} b 
                WHERE b.[event] = '{event_b}' 
                AND b.caseid = a.caseid 
                AND b.startTime < a.startTime 
            ) 
            OR NOT EXISTS ( 
                SELECT 1 
                 FROM {log} b 
                 WHERE b.[event] = '{event_b}' 
                AND b.caseid = a.caseid 
           ) 
        ) """
    )

    # Execute the query
    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def precedence_pattern(log, event_a, event_b):
    # Define the SQL query
    query = f"""
    SELECT 
        COUNT(DISTINCT a.caseid) AS total_cases
    FROM 
        {log} a
    INNER JOIN 
        (SELECT 
             a.[event] AS TaskA, 
             b.[event] AS TaskB 
         FROM 
             {log} a
         INNER JOIN 
             {log} b ON a.[event] != b.[event]
         WHERE 
             a.[event] = '{event_a}' 
             AND b.[event] = '{event_b}'
         GROUP BY 
             a.[event], b.[event]) x
    ON 
        a.[event] = '{event_b}'
    WHERE 
        EXISTS (SELECT 1 
                FROM {log} b 
                WHERE b.[event] = '{event_a}' 
                  AND b.caseid = a.caseid 
                  AND a.position > b.position)
    UNION 
    SELECT COUNT(DISTINCT e.caseid) AS total_cases
    FROM {log} AS e
    WHERE 
        (e.event = '{event_a}'
         AND NOT EXISTS (
            SELECT 1 FROM {log} c
            WHERE e.caseid = c.caseid 
            AND c.event = '{event_b}'
        ))
    """

    # Execute the query
    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def chain_response_pattern(log, event_a, event_b):
    query = f"""
    SELECT Count(DISTINCT a.caseid) as total_cases
    FROM {log} AS a
    LEFT JOIN {log} AS b 
    ON a.caseid = b.caseid 
    AND a.position + 1 = b.position  -- Must be immediately after event_a
    AND b.event = '{event_b}'
    WHERE a.event = '{event_a}'
    AND b.caseid IS NULL;  -- Violation: event_b does not exist immediately after
    """
    # Execute the query
    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def chain_precede_pattern(log, event_a, event_b):
    query = f"""
    SELECT Count(DISTINCT b.caseid) as total_cases
    FROM {log} AS b
    LEFT JOIN {log} AS a 
    ON b.caseid = a.caseid 
    AND a.position = b.position - 1  -- event_a must be immediately before event_b
    AND a.event = '{event_a}'
    WHERE b.event = '{event_b}'
    AND a.caseid IS NULL;  -- No immediate event_a before event_b
    """

    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def alternate_response_pattern(log, event_a, event_b):
    query = f"""
    SELECT count(DISTINCT a.caseid) as total_cases 
    FROM {log} AS a
    WHERE a.event = '{event_a}' -- Event A
    AND NOT EXISTS (
        SELECT 1 FROM {log} AS b 
        WHERE b.caseid = a.caseid 
        AND b.event = '{event_b}' -- Event B
        AND b.position > a.position -- B must happen after A
    );
    """

    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def alternate_precede_pattern(log, event_a, event_b):

    query = f"""
    SELECT count(DISTINCT c.caseid) as total_cases
    FROM {log} c
    WHERE c.event = '{event_b}'  -- Event B
    AND NOT EXISTS (
        SELECT 1
        FROM {log} e1
        WHERE e1.caseid = c.caseid  -- Same case
        AND e1.event = '{event_a}' -- Event A
        AND e1.position < c.position  -- Ensuring event A happened before event B
    );
    """

    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def responded_existence_pattern(log,event_a, event_b):
    query = f"""Select count(Distinct a.caseid) as total_cases
                FROM {log} a,
                (SELECT a.[event] AS TaskA, b.[event] AS TaskB FROM {log} a, {log} b
                        WHERE a.[event] != b.[event] and a.event = '{event_a}' and b.event ='{event_b}'
                        GROUP BY a.[event], b.[event]) x
                WHERE a.[event] = '{event_a}'
                AND (Not EXISTS (SELECT * FROM {log} b
                    WHERE b.[event] = '{event_b}' and b.caseid = a.caseid) )"""
    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases

def absence_pattern (log,event_a):
   query=f"""
        SELECT count(Distinct a.caseid) as total_cases
        FROM {log} a 
        WHERE a.[event] = '{event_a}'
    """
   cursor.execute(query)
   # Fetch the results
   results = cursor.fetchall()
   # Sum the counts from both parts of the UNION
   total_cases = sum(row.total_cases for row in results)

   return total_cases

def existence_pattern (log,event_a):
    query =f"""
        SELECT count(DISTINCT a.caseid) AS total_cases
        FROM {log} a
        WHERE NOT EXISTS (
            SELECT 1
            FROM {log} b
            WHERE b.caseid = a.caseid  
              AND b.event = '{event_a}' 
        );
    """
    cursor.execute(query)
    # Fetch the results
    results = cursor.fetchall()
    # Sum the counts from both parts of the UNION
    total_cases = sum(row.total_cases for row in results)

    return total_cases



#Configuration
def get_activities(log):
    query = f"""
    SELECT 
        DISTINCT a.[event]
    FROM 
        {log} a
    """
    cursor.execute(query)
    activities = [row[0] for row in cursor.fetchall()]
    return activities

# # Function to display activities and let the user choose
# def choose_activities(activities):
#     print("\nList of Activities:")
#     for i, activity in enumerate(activities, start=1):
#         print(f"{i}. {activity}")
#
#     # Let the user choose event_a and event_b
#     event_a_index = int(input("Choose the index for event_a: ")) - 1
#     event_b_index = int(input("Choose the index for event_b: ")) - 1
#
#     event_a = activities[event_a_index]
#     event_b = activities[event_b_index]
#     return event_a, event_b
# # Assuming you have a database connection and cursor set up
#
# # # Function to take input from the user
# # def get_user_input():
# #     log_table = input("Enter the log table name: ")
# #     event_a = input("Enter the first event (event_a): ")
# #     event_b = input("Enter the second event (event_b): ")
# #     return log_table, event_a, event_b
# #
# # Function to display the menu
# def display_menu():
#     print("\nChoose a function to run:")
#     print("1. Precedence Pattern")
#     print("2. Chain Response Pattern")
#     print("3. Chain Precede Pattern")
#     print("4. Alternate Response Pattern")
#     print("5. Alternate Precede Pattern")
#     print("6. Response Antipattern")
#     print("7. Exit")
# # Main program
# def main():
#     log_table = input("Enter the log table name: ")
#
#     # Fetch distinct activities from the database
#     activities = get_activities(log_table)
#     if not activities:
#         print("No activities found in the log table.")
#         return
#
#     while True:
#         display_menu()
#         choice = input("Enter your choice (1-7): ")
#
#         if choice == '7':
#             print("Exiting the program.")
#             break
#
#         # Let the user choose event_a and event_b
#         event_a, event_b = choose_activities(activities)
#         print(f"Selected events: event_a = {event_a}, event_b = {event_b}")
#
#         # Run the selected function
#         if choice == '1':
#             results = precedence_pattern(log_table, event_a, event_b)
#             print("Precedence Cases:", results)
#         elif choice == '2':
#             chain_response_cases = chain_response_pattern(log_table, event_a, event_b)
#             print("Chain Response Cases:", chain_response_cases)
#         elif choice == '3':
#             chain_precede_cases = chain_precede_pattern(log_table, event_a, event_b)
#             print("Chain Precede Cases:", chain_precede_cases)
#         elif choice == '4':
#             alternate_response_cases = alternate_response_pattern(log_table, event_a, event_b)
#             print("Alternate Response Cases:", alternate_response_cases)
#         elif choice == '5':
#             alternate_precede_cases = alternate_precede_pattern(log_table, event_a, event_b)
#             print("Alternate Precede Cases:", alternate_precede_cases)
#         elif choice == '6':
#             response_cases = response_antipattern(log_table, event_a, event_b)
#             print("Response Cases:", response_cases)
#         else:
#             print("Invalid choice. Please try again.")
#
# # Run the program
# if __name__ == "__main__":
#     main()
# # Assuming you have a database connection and cursor set up
# results = precedence_pattern('bpi2013_1000', 'W_Afhandelen leads', 'W_Completeren aanvraag')
# print("Precedence Cases:",results)
#
# # Example usage
# log_table = 'bpi2013_1000'
#
# # Chain Response Pattern
# event_a = 'A_ACCEPTED'
# event_b = 'W_Completeren aanvraag'
# chain_response_cases = chain_response_pattern(log_table, event_a, event_b)
# print("Chain Response Cases:", chain_response_cases)
#
#
# # Chain Precede Pattern
# event_a = 'A_ACCEPTED'
# event_b = 'W_Nabellen offertes'
# chain_precede_cases = chain_precede_pattern(log_table, event_a, event_b)
# print("Chain Precede Cases:", chain_precede_cases)
#
# # Alternate Response Pattern
# event_a = 'A_SUBMITTED'
# event_b = 'A_PREACCEPTED'
# alternate_response_cases = alternate_response_pattern(log_table, event_a, event_b)
# print("Alternate Response Cases:", alternate_response_cases)
#
#
# event_a = 'A_SUBMITTED'
# event_b = 'A_PREACCEPTED'
#
# alternate_precede_cases = alternate_precede_pattern(log_table, event_a, event_b)
# print("Alternate Precede Cases:", alternate_precede_cases)
#
#
# event_a = 'A_SUBMITTED'
# event_b = 'W_Completeren aanvraag'
#
# response_cases = response_antipattern(log_table, event_a, event_b)
# print("Response Cases:", response_cases)
#
#
#
#

#Configuration

def import_events():
    # Open a file dialog to select the text file
    file_path = filedialog.askopenfilename(
        title="Select Events File",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if not file_path:
        return  # User canceled the file dialog

    try:
        with open(file_path, 'r') as file:
            events = file.readlines()

        # Process each line in the file
        for event_line in events:
            # Split the line into event_a and event_b
            components = event_line.strip().split(',')
            if len(components) != 2:
                messagebox.showwarning("Format Error", f"Invalid event format: {event_line}")
                continue

            event_a, event_b = components

            # Populate the event fields
            event_a_combobox.set(event_a if event_a else "")
            event_b_combobox.set(event_b if event_b else "")

            # Debug: Print the imported events
            print(f"Imported Events: Event A={event_a}, Event B={event_b}")

            # Optionally, automatically run the scenario
            run_pattern()
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file: {e}")

def update_activities(event=None):
    log_table = log_table_entry.get()
    if not log_table:
        messagebox.showwarning("Input Error", "Please enter a log table name.")
        return

    activities = get_activities(log_table)
    if activities:
        event_a_combobox['values'] = activities
        event_b_combobox['values'] = activities
        event_a_combobox.current(0)  # Set the first activity as default
        event_b_combobox.current(0)  # Set the first activity as default
        print(f"Activities fetched: {activities}")  # Debug: Print fetched activities
    else:
        messagebox.showwarning("Data Error", "No activities found for the given log table.")

# Function to run the selected pattern
def run_pattern():
    # Get inputs from the GUI
    log_table = log_table_entry.get()
    event_a = event_a_combobox.get()

    # Debug: Print the state and value of event_b_combobox
    print(f"Event B Combobox State: {event_b_combobox['state']}")
    print(f"Event B Value: {event_b_combobox.get()}")

    # Get event_b only if the combobox is enabled
    event_b = event_b_combobox.get() if event_b_combobox['state'] == 'normal' else None
    selected_function = function_combobox.get()

    # Debug: Print all inputs
    print(f"Log Table: {log_table}")
    print(f"Event A: {event_a}")
    print(f"Event B: {event_b}")
    print(f"Selected Function: {selected_function}")

    # Map the selected function to the corresponding function
    function_mapping = {
        "Select Pattern": None,  # Placeholder for the default option
        "Precedence": precedence_pattern,
        "Chain Response": chain_response_pattern,
        "Chain Precede": chain_precede_pattern,
        "Alternate Response": alternate_response_pattern,
        "Alternate Precede": alternate_precede_pattern,
        "Response": response_antipattern,
        "Responded-Existence":responded_existence_pattern,
        "Absence": absence_pattern,
        "Existence": existence_pattern
    }

    # Validate inputs
    if not log_table:
        messagebox.showwarning("Input Error", "Please enter a log table name.")
        return

    if not event_a:
        messagebox.showwarning("Input Error", "Please select event_a.")
        return

    if selected_function not in ["Existence", "Absence"] and not event_b:
        messagebox.showwarning("Input Error", "Please select event_b for this function.")
        return

    # Run the selected function
    if selected_function in function_mapping:
        try:
            if selected_function in ["Existence", "Absence"]:
                # Single-event functions
                result = function_mapping[selected_function](log_table, event_a)
            else:
                # Two-event functions
                result = function_mapping[selected_function](log_table, event_a, event_b)
            result_text.delete(1.0, tk.END)  # Clear previous result
            result_text.insert(tk.END, f"Unsatisfied Cases for {selected_function}:\n{result}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Function Error", "Invalid function selected.")
# Function to toggle event fields based on the selected function
def toggle_event_fields(event):
    selected_function = function_combobox.get()
    if selected_function in ["Existence", "Absence"]:
        # Single-event functions
        event_a_label.grid(row=2, column=0, padx=10, pady=10)
        event_a_combobox.grid(row=2, column=1, padx=10, pady=10)
        event_a_combobox.config(state='normal')
        event_b_label.grid_remove()
        event_b_combobox.grid_remove()
    else:
        # Two-event functions
        event_a_label.grid(row=2, column=0, padx=10, pady=10)
        event_a_combobox.grid(row=2, column=1, padx=10, pady=10)
        event_a_combobox.config(state='normal')
        event_b_label.grid(row=3, column=0, padx=10, pady=10)
        event_b_combobox.grid(row=3, column=1, padx=10, pady=10)
        event_b_combobox.config(state='normal')

# GUI Setup
root = tk.Tk()
root.title("Compliance Pattern Analyzer")

# Log Table Input
tk.Label(root, text="Log Table:").grid(row=0, column=0, padx=10, pady=10)
log_table_entry = tk.Entry(root, width=30)
log_table_entry.grid(row=0, column=1, padx=10, pady=10)

# Bind the FocusOut and Return events to update_activities
log_table_entry.bind("<FocusOut>", update_activities)
log_table_entry.bind("<Return>", update_activities)

# Event A Selection
event_a_label = tk.Label(root, text="Event A:")
event_a_combobox = ttk.Combobox(root, width=30)

# Event B Selection
event_b_label = tk.Label(root, text="Event B:")
event_b_combobox = ttk.Combobox(root, width=30)

# Function Selection
tk.Label(root, text="Function:").grid(row=1, column=0, padx=10, pady=10)
function_combobox = ttk.Combobox(root, width=30)
function_combobox['values'] = [
    "Select Pattern",
    "Precedence",
    "Chain Response",
    "Chain Precede",
    "Alternate Response",
    "Alternate Precede",
    "Response",
    "Responded-Existence",
    "Existence",
    "Absence",
]
function_combobox.current(0)
function_combobox.grid(row=1, column=1, padx=10, pady=10)
function_combobox.bind("<<ComboboxSelected>>", toggle_event_fields)

# Run Button
run_button = tk.Button(root, text="Run Function", command=run_pattern)
run_button.grid(row=4, column=1, padx=10, pady=10)

# Result Display
result_text = tk.Text(root, height=10, width=50)
result_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# Start the GUI
root.mainloop()