Validating Temporal Compliance Patterns: A Unified Approach with MTL over various Data Models

This repositry collects compliance anti-patterns over different encoded methods.
-----------------------------------
LTL Checker
-----------
    This folder contains files related to the implementation, testing, and results of compliance antipatterns using Linear Temporal Logic (LTL). Below is a description of the files and their purposes.

Files in the LTL Checker Folder
    1. bpj2013_sample.csv
        This file contains sample event log data in CSV format. It is used for testing and validating the LTL checker.
    2. Resulting of Other Methods.docx
        This document provides results obtained using alternative methods (e.g., relational databases, Neo4j, SQL graph databases) for detecting compliance antipatterns.
    3. Results of Testing Pattern in LTL Checker.docx
        This document contains the results of testing various compliance patterns using the LTL checker.
----------------------------------
Source Code
    This folder contains Python scripts for creating and querying graph databases (Neo4j and SQL-based) and detecting compliance antipatterns. Below is a description of the files and their purposes.

Files in the Source Code Folder
    1. Create_DB_SQL_Graph.py
        This script is used to create a SQL-based graph database.
        It sets up the necessary tables and relationships for storing event log data and detecting antipatterns.
    2. CreategraphDB_Neo4j.py
        This script is used to create a Neo4j graph database.
        It initializes the database schema and populates it with event log data for further analysis.
    3. Graph_db_sql_antipatterns.py
        This script detects compliance antipatterns in a SQL-based graph database.
        It includes queries and logic for identifying anti-patterns such as absence, existence, response, and precedence and rest of patterns.
    4. Graph_db_sql_antipatterns_No_Window.py
        This script detects compliance antipatterns in a SQL-based graph database without considering time windows.
    5. Neo4jAntiPatterns.py
        This script detects compliance antipatterns in a Neo4j graph database.
        It includes Cypher queries and logic for identifying anti-patterns such as absence, existence, response, and precedence.
    6. SQL_Antipatterns_No_Window.py
        This script detects compliance antipatterns in a SQL-based database without considering time windows.
    7. SQLMiner_Antipatterns_With_Window.py
        This script detects compliance antipatterns in a SQL-based database with time windows.
        It includes queries and logic for identifying anti-patterns that occur within or after specific time intervals.
-------------------------------