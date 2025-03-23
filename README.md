Validating Temporal Compliance Patterns: A Unified Approach with MTL over Various Data Models
This repository collects compliance antipatterns over different encoded methods, including relational databases, Neo4j, and SQL graph databases. It provides tools and implementations for detecting and validating temporal compliance patterns using Linear Temporal Logic (LTL) and Metric Temporal Logic (MTL).

Repository Structure

LTL Checker
This folder contains files related to the implementation, testing, and results of compliance antipatterns using Linear Temporal Logic (LTL). Below is a description of the files and their purposes.

Files in the LTL Checker Folder
bpj2013_sample.csv

This file contains sample event log data in CSV format. It is used for testing and validating the LTL checker.

Resulting of Other Methods.docx

This document provides results obtained using alternative methods (e.g., relational databases, Neo4j, SQL graph databases) for detecting compliance antipatterns.

Results of Testing Pattern in LTL Checker.docx

This document contains the results of testing various compliance patterns using the LTL checker.

Source Code
This folder contains Python scripts for creating and querying graph databases (Neo4j and SQL-based) and detecting compliance antipatterns. Below is a description of the files and their purposes.

Files in the Source Code Folder
Create_DB_SQL_Graph.py

This script is used to create a SQL-based graph database. It sets up the necessary tables and relationships for storing event log data and detecting antipatterns.

CreategraphDB_Neo4j.py

This script is used to create a Neo4j graph database. It initializes the database schema and populates it with event log data for further analysis.

Graph_db_sql_antipatterns.py

This script detects compliance antipatterns in a SQL-based graph database. It includes queries and logic for identifying antipatterns such as absence, existence, response, and precedence, as well as other patterns.

Graph_db_sql_antipatterns_No_Window.py

This script detects compliance antipatterns in a SQL-based graph database without considering time windows.

Neo4jAntiPatterns.py

This script detects compliance antipatterns in a Neo4j graph database. It includes Cypher queries and logic for identifying antipatterns such as absence, existence, response, and precedence.

SQL_Antipatterns_No_Window.py

This script detects compliance antipatterns in a SQL-based database without considering time windows.

SQLMiner_Antipatterns_With_Window.py

This script detects compliance antipatterns in a SQL-based database with time windows. It includes queries and logic for identifying antipatterns that occur within or after specific time intervals.