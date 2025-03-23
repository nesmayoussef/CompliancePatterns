import pyodbc
import pandas as pd
import time
import datetime
import os.path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

conn = pyodbc.connect('Driver={SQL Server};Server=NESMA\SQLEXPRESS;Database=BPI2013;Trusted_Connection=yes;')
cursor = conn.cursor()

#Response
def response_pattern(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id, e.event
    FROM graph.Cases_base_{log} c, 
         graph.Events_base_{log} e, 
         graph.casetoevent_base_{log} r
    WHERE MATCH(c-(r)->e)
    AND (
        (e.event = ? 
         AND NOT EXISTS (
            SELECT 1 FROM graph.Cases_base_{log} c2, 
                         graph.Events_base_{log} e2, 
                         graph.casetoevent_base_{log} r2
            WHERE MATCH(c2-(r2)->e2) 
            AND c.case_id = c2.case_id 
            AND e2.event = ? 
        ))
    )
    ORDER BY c.case_id;
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Precedence
def precede_pattern(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c, 
         graph.Events_base_{log} e, 
         graph.casetoevent_base_{log} r
    WHERE MATCH(c-(r)->e) 
    AND e.event = ?
    AND c.case_id NOT IN (
        SELECT a.case_id 
        FROM graph.Cases_base_{log} a, 
             graph.Events_base_{log} e2, 
             graph.casetoevent_base_{log} r3 
        WHERE MATCH(a-(r3)->e2) 
        AND e2.event = ?
    )
    UNION
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c
    JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id
    JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
    JOIN graph.casetoevent_base_{log} r2 ON c.$node_id = r2.$from_id 
    JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
    LEFT JOIN graph.df_base_{log} df ON df.$from_id = e.$node_id AND df.$to_id = e1.$node_id
    WHERE e.event = ?
    AND e1.event = ?
    AND df.$from_id IS NULL;
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb, actb, acta))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Chain Precedence
def chain_precede(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c
    JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id 
    JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
    JOIN graph.casetoevent_base_{log} r2 ON c.$node_id = r2.$from_id
    JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
    WHERE e.event = ?
    AND e1.event = ?
    AND (e1.caseindex - e.caseindex > 1)
    UNION
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c, 
         graph.Events_base_{log} e, 
         graph.casetoevent_base_{log} r
    WHERE MATCH(c-(r)->e) 
    AND e.event = ?
    AND c.case_id NOT IN (
        SELECT a.case_id 
        FROM graph.Cases_base_{log} a, 
             graph.Events_base_{log} e2, 
             graph.casetoevent_base_{log} r3 
        WHERE MATCH(a-(r3)->e2) 
        AND e2.event = ?
    );
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb, actb, acta))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Chain Response
def chain_response(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c
    JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id 
    JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
    JOIN graph.casetoevent_base_{log} r2 ON c.$node_id = r2.$from_id
    JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
    JOIN graph.df_base_{log} df ON df.$from_id = e1.$node_id AND df.$to_id = e.$node_id
    WHERE e.event = ?
    AND e1.event = ?
    UNION
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c, 
         graph.Events_base_{log} e, 
         graph.casetoevent_base_{log} r
    WHERE MATCH(c-(r)->e) 
    AND e.event = ?
    AND c.case_id NOT IN (
        SELECT a.case_id 
        FROM graph.Cases_base_{log} a, 
             graph.Events_base_{log} e2, 
             graph.casetoevent_base_{log} r3 
        WHERE MATCH(a-(r3)->e2) 
        AND e2.event = ?
    );
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb, acta, actb))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Alternate Response
def alternate_response(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c
    JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id 
    JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
    WHERE e.event = ?
    AND NOT EXISTS (
        SELECT 1
        FROM graph.casetoevent_base_{log} r2
        JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
        WHERE r2.$from_id = c.$node_id  -- Same case
        AND e1.event = ? 
        AND e1.caseindex > e.caseindex  -- Ensuring event B happens after event A
    );
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Alternate Precede
def alternate_precede(acta, actb, log):
    query = f"""
    SELECT DISTINCT c.case_id
    FROM graph.Cases_base_{log} c
    JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id 
    JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
    WHERE e.event = ?
    AND NOT EXISTS (
        SELECT 1
        FROM graph.casetoevent_base_{log} r2
        JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
        WHERE r2.$from_id = c.$node_id  -- Same case
        AND e1.event = ? 
        AND e1.caseindex < e.caseindex  -- Ensuring event A happened before event B
    );
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Responded Existence
def responded_existence(acta, actb, log):
    query = f"""
            SELECT DISTINCT c.case_id
            FROM graph.Cases_base_{log} c
            JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id
            JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
            WHERE e.event = {acta}  -- Event A (e.g., 'A_DECLINED')
            AND NOT EXISTS (
                SELECT 1
                FROM graph.casetoevent_base_{log} r2
                JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
                WHERE r2.$from_id = c.$node_id  -- Same case
                AND e1.event = {actb}  -- Event B (e.g., 'A_FINALIZED')
            )"""
    # Execute the query with acta and actb as parameters
    cursor.execute(query, (acta, actb))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Absence
def absence(act,log):
    query = f"""
                SELECT DISTINCT c.case_id
                FROM graph.Cases_base_{log} c
                JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id
                JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
                WHERE e.event = {act} """
    # Execute the query with acta and actb as parameters
    cursor.execute(query, (act))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases

#Existence
def existence(act,log):
    query= f"""
        SELECT DISTINCT c.case_id
        FROM graph.Cases_base_{log} c
        JOIN graph.casetoevent_base_{log} r ON c.$node_id = r.$from_id 
        JOIN graph.Events_base_{log} e ON r.$to_id = e.$node_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM graph.casetoevent_base_{log} r2
            JOIN graph.Events_base_{log} e1 ON r2.$to_id = e1.$node_id
            WHERE r2.$from_id = c.$node_id  
            AND e1.event = {act}  
        )
    """

    # Execute the query with acta and actb as parameters
    cursor.execute(query, (act))

    # Fetch all results
    results = cursor.fetchall()

    # Extract case IDs from the results
    cases = [row[0] for row in results]  # row[0] is the case_id

    # Get the total number of cases
    total_cases = len(cases)

    # Return the total number of cases and the list of case IDs
    return total_cases



acta = 'A_Submitted'
actb = 'W_Completeren aanvraag'
log = 'bpi2013_1000'

# Call the function
total_cases = response_pattern(acta, actb, log)

# Print the results
print(f"Total number of cases: {total_cases}")

