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


