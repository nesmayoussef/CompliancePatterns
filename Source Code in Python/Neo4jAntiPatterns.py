from py2neo import Graph, Node, Relationship
from neo4j import GraphDatabase
import pandas as pd
import time
import datetime
import os.path

#connect to specific database
uri= "bolt://localhost:7687"
driver = GraphDatabase.driver(uri,auth=("neo4j","12345"))
file_exists = os.path.isfile('data.csv')

#Unique Methods:
#Response antipattern:
def response_anti_pattern(a, b, database):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[:Case_To_Event]->(:Event {name: $actb})
    }
    RETURN DISTINCT c.name AS casename
    UNION
    MATCH (a:Event {name: $acta})<-[r2:Case_To_Event]-(c:Case)-[r1:Case_To_Event]->(b:Event {name: $actb})
    WHERE toInteger(r1.position) < toInteger(r2.position)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def response_anti_pattern_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def response_anti_pattern_after_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

#Precedence antipattern:
def precede_anti_pattern(a, b, database):
    query = """
    MATCH (c:Case)-[:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[:Case_To_Event]->(:Event {name: $actb})
    }
    RETURN DISTINCT c.name AS casename
    UNION
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
    WHERE toInteger(r1.position) < toInteger(r2.position)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def precede_anti_pattern_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(b:Event {name: $actb})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(a:Event {name: $acta})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def precede_anti_pattern_after_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(b:Event {name: $actb})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(a:Event {name: $acta})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Chain Precedence antipattern
def chain_precede(a, b, database):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(e1:Event {name: $acta})
    WITH c, e1, toInteger(r1.position) AS pos
    OPTIONAL MATCH (c)-[r2:Case_To_Event]->(e2:Event {name: $actb})
    WHERE toInteger(r2.position) = pos - 1
    WITH c, e1, e2
    WHERE e2 IS NULL
    RETURN DISTINCT c.name AS caseName
    UNION
    MATCH (c:Case)-[:Case_To_Event]->(e1:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[:Case_To_Event]->(e2:Event {name: $actb})
    }
    RETURN DISTINCT c.name AS caseName
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def chain_precede_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WITH c, a, toInteger(r1.position) AS pos
    OPTIONAL MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
    WHERE toInteger(r2.position) = pos + 1 AND toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    WITH c, a, b
    WHERE b IS NULL
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time


#Chain Response antipattern
def chain_response(a, b, database):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(e1:Event {name: $acta})
    WITH c, e1, toInteger(r1.position) AS pos
    OPTIONAL MATCH (c)-[r2:Case_To_Event]->(e2:Event)
    WHERE toInteger(r2.position) = pos + 1
    WITH c, e1, e2
    WHERE e2 IS NULL OR e2.name <> $actb
    RETURN DISTINCT c.name AS caseName
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def chain_response_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WITH c, a, toInteger(r1.position) AS pos
    OPTIONAL MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
    WHERE toInteger(r2.position) = pos + 1 AND toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    WITH c, a, b
    WHERE b IS NULL
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Alternate Response antipattern
def alternate_response(a, b, database):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(e1:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(e2:Event {name: $actb})
        WHERE toInteger(r2.position) > toInteger(r1.position)
    }
    RETURN DISTINCT c.name AS caseName
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def alternate_response_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toInteger(r2.position) > toInteger(r1.position)
        AND toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def alternate_response_after_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toInteger(r2.position) > toInteger(r1.position)
        AND toFloat(b.startTime) - toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Alternate Precedence antipattern
def alternate_precede(a, b, database):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(e1:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(e2:Event {name: $actb})
        WHERE toInteger(r2.position) < toInteger(r1.position)
    }
    RETURN DISTINCT c.name AS caseName
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def alternate_precede_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toInteger(r2.position) < toInteger(r1.position)
        AND toFloat(a.startTime) - toFloat(b.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def alternate_precede_after_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toInteger(r2.position) < toInteger(r1.position)
        AND toFloat(a.startTime) - toFloat(b.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Responded Existence antipattern
def responded_existence(a, b, database):
    query="""
        MATCH (c:Case)-[r1:Case_To_Event]->(e1:Event {name: $acta})
        WHERE NOT EXISTS {
                MATCH (c)-[r2:Case_To_Event]->(e2:Event {name: $actb})
            }RETURN DISTINCT c.name AS casename
        """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def responded_existence_within_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def responded_existence_after_time_window(a, b, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $acta})
    WHERE NOT EXISTS {
        MATCH (c)-[r2:Case_To_Event]->(b:Event {name: $actb})
        WHERE toFloat(b.startTime) - toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Absence antipattern
def absence(a, database):
    query="""
    MATCH (c)-[r1:Case_To_Event]->(e1:Event {name: $act})
            RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def absence_within_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $act})
    WHERE toFloat(a.startTime) <= $maxTime
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def absence_after_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)-[r1:Case_To_Event]->(a:Event {name: $act})
    WHERE toFloat(a.startTime) > $maxTime
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time
#Existence antipattern
def existence(a, database):
    query="""
    MATCH (c:Case)
    WHERE NOT EXISTS {
        MATCH (c)-[:Case_To_Event]->(e:Event {name: $act})
    }
    RETURN DISTINCT c.name AS casename"""

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def existence_within_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)
    WHERE NOT EXISTS {
        MATCH (c)-[r1:Case_To_Event]->(a:Event {name: $act})
        WHERE toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

def existence_after_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)
    WHERE NOT EXISTS {
        MATCH (c)-[r1:Case_To_Event]->(a:Event {name: $act})
        WHERE toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

#Baseline Methods:

#Response antipattern:
def baseline_response(a, b, database):
    base_response = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta}),
          (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
    WHERE (a)-[:DF*..]-> (b)
    RETURN DISTINCT c.name AS casename
    UNION
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    WHERE NOT EXISTS {
        MATCH (c)<-[:EVENT_TO_CASE]-(:Event {activity: $actb})
    }
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(base_response, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time
#Precede antipattern:
def baseline_precedence(a, b, database):
    base_precede =  """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    WHERE NOT EXISTS {
        MATCH (c)<-[:EVENT_TO_CASE]-(:Event {activity: $actb})
    }
    RETURN DISTINCT c.name AS casename
    UNION
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $actb}),
          (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $acta})
    WHERE (a)-[:DF*..]-> (b)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(base_precede, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time
#Chain Precede antipattern
def baseline_chain_precede(a, b, database):
    query = """
    // Chain Precede: Cases where 'acta' is not directly preceded by 'actb'
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $acta})
    WHERE NOT EXISTS {
        MATCH (b)<-[:DF]-(a:Event {activity: $actb})
    }
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

# Chain Precede antipattern within time window

def baseline_chain_precede_within_window(a, b, database, min_hours=2, max_hours=10):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $acta})
    OPTIONAL MATCH (b)<-[:DF]-(a:Event {activity: $actb})
    WITH c, a, b
    WHERE a IS NULL OR NOT (
        (toFloat(b.startTime) - toFloat(a.startTime)) / 3600 >= $minHours
        AND (toFloat(b.startTime) - toFloat(a.startTime)) / 3600 <= $maxHours
    )
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, minHours=min_hours, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time

#chain Precede max time window

def baseline_chain_precede_max_time(a, b, database, max_hours=10):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $acta})
    OPTIONAL MATCH (b)<-[:DF]-(a:Event {activity: $actb})
    WITH c, a, b
    WHERE a IS NULL OR NOT (
        (toFloat(b.startTime) - toFloat(a.startTime)) / 3600 > $maxHours
    )
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases,cases, total_time


#Chain Response antipattern
def baseline_chain_response(a, b, database):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $actb})
    WHERE NOT EXISTS {
        MATCH (a)-[:DF]->(b:Event {activity: $acta})
    }
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time


def baseline_chain_response_max_time(a, b, database, max_hours=10):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $actb})
    OPTIONAL MATCH (a)-[:DF]->(b:Event {activity: $acta})
    WITH c, a, b
    WHERE b IS NULL OR (
        (toFloat(b.startTime) - toFloat(a.startTime)) / 3600 > $maxHours
    )
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases,cases, total_time

def chain_response_antipatterns_within_window(a, b, database, min_hours=2, max_hours=10):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $actb})
    OPTIONAL MATCH (a)-[:DF]->(b:Event {activity: $acta})
    WITH c, a, b
    WHERE b IS NULL OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 < $minHours) OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 > $maxHours)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, minHours=min_hours, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases,total_time


#Alternate Precede antipattern
def baseline_alternate_precede(a, b, database):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
    WHERE NOT EXISTS {
        MATCH (a:Event {activity: $acta})-[:DF*]->(b)
    }
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time


def alternate_precede_antipatterns_within_window(a, b, database, min_hours=2, max_hours=10):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
    OPTIONAL MATCH (a:Event {activity: $acta})-[:DF*]->(b)
    WITH c, a, b
    WHERE a IS NULL OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 < $minHours) OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 > $maxHours)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, minHours=min_hours, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases,cases,total_time

#Alternate Response antipattern
def baseline_alternate_response(a, b, database):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    WHERE NOT EXISTS {
        MATCH (a)-[:DF*]->(b:Event {activity: $actb})
    }
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def alternate_response_antipatterns_within_window(a, b, database, min_hours=2, max_hours=24):

    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    OPTIONAL MATCH (a)-[:DF*]->(b:Event {activity: $actb})
    WITH c, a, b
    WHERE b IS NULL OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 < $minHours) OR 
          ((toFloat(b.startTime) - toFloat(a.startTime)) / 3600 > $maxHours)
    RETURN DISTINCT c.name AS casename
    """

    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, minHours=min_hours, maxHours=max_hours)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases,cases,total_time

#Responded Existence antipattern
def baseline_responded_existence(a, b, database):
    query="""
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    WHERE NOT EXISTS {
        MATCH (c)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time


def baseline_responded_existence_max_time(a, b, max_time):
        query = """
        MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
        OPTIONAL MATCH (c)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
        WITH c, a, b
        WHERE b IS NULL OR (toFloat(b.startTime) - toFloat(a.startTime) > $maxTime)
        RETURN DISTINCT c.name AS casename
        """
        total_time = 0
        with driver.session(database=database) as graphDB_Session:
            result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)
            cases = [record["casename"] for record in result]
            total_cases = len(cases)

            avail = result.consume().result_available_after
            cons = result.consume().result_consumed_after
            total_time += (avail + cons)

        driver.close()

        return total_cases, cases, total_time

def baseline_responded_existence_antipattern_within(a, b, max_time):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $acta})
    OPTIONAL MATCH (c)<-[:EVENT_TO_CASE]-(b:Event {activity: $actb})
    WITH c, a, b
    WHERE b IS NULL OR (toFloat(b.startTime) - toFloat(a.startTime) > $maxTime OR toFloat(b.startTime) - toFloat(a.startTime) < 0)
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, acta=a, actb=b, maxTime=max_time)
        cases = [record["casename"] for record in result]
        total_cases = len(cases)

        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    return total_cases, cases, total_time


#Absence Anti-pattern
def baseline_absence(a, database):
    query= """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def absence_antipattern_within_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})
    WHERE toFloat(a.startTime) <= $maxTime
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def absence_antipattern_after_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})
    WHERE toFloat(a.startTime) > $maxTime
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

#Existence Antipattern
def baseline_existence(a, database):
    query="""
    Match (c:Case) where not exists {MATCH (c:Case)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})}
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def existence_antipattern_within_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)
    WHERE NOT EXISTS {
        MATCH (c)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})
        WHERE toFloat(a.startTime) <= $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time

def existence_antipattern_after_time_window(a, database, max_time):
    query = """
    MATCH (c:Case)
    WHERE NOT EXISTS {
        MATCH (c)<-[:EVENT_TO_CASE]-(a:Event {activity: $act})
        WHERE toFloat(a.startTime) > $maxTime
    }
    RETURN DISTINCT c.name AS casename
    """
    total_time = 0
    with driver.session(database=database) as graphDB_Session:
        result = graphDB_Session.run(query, act=a, maxTime=max_time)

        # Collect case names
        cases = [record["casename"] for record in result]

        # Get total number of cases
        total_cases = len(cases)

        # Calculate query execution time
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        total_time += (avail + cons)

    driver.close()

    # Return total number of cases, the cases themselves, and total time
    return total_cases, cases, total_time



a = 'A_SUBMITTED'
b = 'W_Completeren aanvraag'
a1 = 'W_Afhandelen leads'
b1 = 'W_Completeren aanvraag'
database = 'bpi2013b'

total_cases, cases, total_time = baseline_response(a, b, database)

print(f"Total number of cases: {total_cases}")
print(f"Case names: {sorted(cases)}")
print(f"Total time taken: {total_time} ms")


total_cases, cases, total_time = baseline_precedence(a1, b1, database)

print(f"Total number of cases: {total_cases}")
print(f"Case names: {sorted(cases)}")
print(f"Total time taken: {total_time} ms")

database = 'bpi2013u1000'
total_cases, cases, total_time = response_anti_pattern(a, b, database)

print(f"Total number of cases: {total_cases}")
print(f"Case names: {sorted(cases)}")
print(f"Total time taken: {total_time} ms")

total_cases, cases, total_time = precede_anti_pattern(a1, b1, database)

print(f"Total number of cases: {total_cases}")
print(f"Case names: {sorted(cases)}")
print(f"Total time taken: {total_time} ms")


