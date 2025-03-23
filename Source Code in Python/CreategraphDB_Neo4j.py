from neo4j import GraphDatabase
import pandas as pd
import time
#import networkx as nx

#g = nx.Graph();

#path_data = "Bpi2013_sample_1.csv"
path_data = "bpi2013_1000sample.csv"
df = pd.read_csv(path_data)
#for index,row in df.iterrows():
 #   print(row['case'])
uri= "bolt://localhost:7687"
driver = GraphDatabase.driver(uri,auth=("neo4j","12345"))

#creation of database
def create_database(database):
    createdatabase = "Create Database $dbase"
    with driver.session().begin_transaction() as tx:
        tx.run(createdatabase,dbase=database);
    driver.close()

#drop database
def drop_database(database):
    createdatabase = "Drop Database $dbase"
    with driver.session().begin_transaction() as tx:
        tx.run(createdatabase,dbase=database);
    driver.close()

# Creation of Baseline
def create_baseline(database):

    cqlNodeQuery = "CREATE CONSTRAINT ON (e:Event) ASSERT e.name IS UNIQUE;"
    query2 = "CREATE CONSTRAINT ON (c:Case) ASSERT c.name IS UNIQUE;"
    query3 = "CREATE CONSTRAINT ON (r:Resource) ASSERT r.name IS UNIQUE;"
    createcasenode =  "LOAD CSV WITH HEADERS FROM $tablename as line WITH line.case as case MERGE (c:Case {name: case})";
    createeventnode = """LOAD CSV WITH HEADERS FROM $tablename as line
WITH line.case as case,
    line.EventID as event,
    line.event as activity,
    line.position as position,
    line.sT as sT,
    line.cT as cT,
    line.case_index as cIndex,
    line.sY as sY, line.sD as sD, line.sM as sM, line.sHH as sHH, line.sMM as sMM, line.sSS as sSS, line.sMS as sMS,
    line.cY as cY, line.cD as cD, line.cM as cM, line.cHH as cHH, line.cMM as cMM, line.cSS as cSS, line.cMS as cMS
MATCH (c:Case {name: case})
CREATE (e:Event {name: event,
    starttime: localdatetime({year:toInteger(sY), month:toInteger(sM), day:toInteger(sD), hour:toInteger(sHH), minute:toInteger(sMM), second:toInteger(sSS), microsecond:toInteger(sMS)}),
    completetime: localdatetime({year:toInteger(cY), month:toInteger(cM), day:toInteger(cD), hour:toInteger(cHH), minute:toInteger(cMM), second:toInteger(cSS), microsecond:toInteger(cMS)}),
    activity: activity, position: toInteger(position), caseindex: toInteger(cIndex), sT: toFloat(sT),cT:toFloat(cT)})
CREATE (e) -[:EVENT_TO_CASE]-> (c)
""";
    createdirectfollow = "MATCH (e1:Event) --> (c:Case) <-- (e2:Event) WHERE e2.caseindex - e1.caseindex = 1 CREATE (e2) -[:DF {timebetween: duration.between(e1.completetime, e2.starttime) }]-> (e1)";


    with driver.session(database=database) as graphDB_Session:
        starttime = time.time()
        graphDB_Session.run(cqlNodeQuery)
        graphDB_Session.run(query2)
        graphDB_Session.run(createcasenode ,tablename="file:///"+path_data)
        graphDB_Session.run(createeventnode, tablename="file:///" + path_data)
        graphDB_Session.run(createdirectfollow)
        end = time.time()
    driver.close()
    processingtime = end - starttime
    return processingtime


# Creation of Baseline
def create_baseline_data(database):

    cqlNodeQuery = "CREATE CONSTRAINT ON (e:Event) ASSERT e.name IS UNIQUE;"
    query2 = "CREATE CONSTRAINT ON (c:Case) ASSERT c.name IS UNIQUE;"
    query3 = "CREATE CONSTRAINT ON (r:Resource) ASSERT r.name IS UNIQUE;"
    createcasenode =  "LOAD CSV WITH HEADERS FROM $tablename as line WITH line.case as case MERGE (c:Case {name: case})";
    createeventnode = """LOAD CSV WITH HEADERS FROM $tablename as line
WITH line.case as case,
    line.EventID as event,
    line.event as activity,
    line.position as position,
    line.case_index as cIndex
MATCH (c:Case {name: case})
CREATE (e:Event {name: event,
    activity: activity, position: toInteger(position), caseindex: toInteger(cIndex)})
CREATE (e) -[:EVENT_TO_CASE]-> (c)
""";
    createdirectfollow = "MATCH (e1:Event) --> (c:Case) <-- (e2:Event) WHERE e2.caseindex - e1.caseindex = 1 CREATE (e2) -[:DF]-> (e1)";


    with driver.session(database=database) as graphDB_Session:
        starttime = time.time()
        graphDB_Session.run(cqlNodeQuery)
        graphDB_Session.run(query2)
        graphDB_Session.run(createcasenode ,tablename="file:///"+path_data)
        graphDB_Session.run(createeventnode, tablename="file:///" + path_data)
        graphDB_Session.run(createdirectfollow)
        end = time.time()
    driver.close()
    processingtime = end - starttime
    return processingtime

# creation of Event position graph
def create_eventposition(database):
    cqlNodeQuery = "CREATE CONSTRAINT ON (e:Event) ASSERT e.name IS UNIQUE;"
    query2 = "CREATE CONSTRAINT ON (c:Case) ASSERT c.name IS UNIQUE;"
    query3 = "CREATE CONSTRAINT ON (r:Resource) ASSERT r.name IS UNIQUE;"
    createcasenode =  "LOAD CSV WITH HEADERS FROM $tablename as line WITH line.case as case MERGE (c:Case {name: case})";
    createeventnode = """LOAD CSV WITH HEADERS FROM $tablename as line
WITH line.eventpos as eventpos,
   line.event as activity,
   line.position as position
MERGE (e:Event {name: eventpos, event: activity, position:position})
""";
    createdirectfollow = """LOAD CSV WITH HEADERS FROM $tablename as line
MATCH(c:Case), (e:Event)
WHERE c.name = line.case and e.name = line.eventpos
CREATE (c) -[:Case_To_Event{startTime:line.sT}]-> (e)
""";

    starttime = time.time()
    with driver.session(database=database) as graphDB_Session:
        graphDB_Session.run(cqlNodeQuery)
        graphDB_Session.run(query2)
        graphDB_Session.run(createcasenode ,tablename="file:///"+path_data)
        graphDB_Session.run(createeventnode, tablename="file:///" + path_data)
        graphDB_Session.run(createdirectfollow, tablename="file:///" + path_data)
    driver.close()
    end = time.time()
    processingtime = end - starttime
    return processingtime

# creation of UA "Unique Activities"
def create_unique(database):

    cqlNodeQuery = "CREATE CONSTRAINT ON (e:Event) ASSERT e.name IS UNIQUE;"
    query2 = "CREATE CONSTRAINT ON (c:Case) ASSERT c.name IS UNIQUE;"
    createcasenode = "LOAD CSV WITH HEADERS FROM $tablename as line WITH line.case as case MERGE (c:Case {name: case})";
    createeventnode = """LOAD CSV WITH HEADERS FROM $tablename as line
    WITH line.event as activity MERGE (e:Event {name: activity})""";
    createrelation = """LOAD CSV WITH HEADERS FROM $tablename as line MATCH(c:Case), (e:Event)
     WHERE c.name = line.case and e.name = line.event 
     CREATE (c) -[:Case_To_Event{startTime:line.sT,position:line.position}]-> (e)""";

    with driver.session(database=database) as graphDB_Session:
        starttime = time.time()
        graphDB_Session.run(cqlNodeQuery)
        graphDB_Session.run(query2)
        result =graphDB_Session.run(createcasenode,tablename="file:///"+path_data)
        result1 = graphDB_Session.run(createeventnode,tablename="file:///" + path_data)
        result2 = graphDB_Session.run(createrelation,tablename="file:///" + path_data)
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        avail1 = result1.consume().result_available_after
        cons1 = result1.consume().result_consumed_after
        avail2 = result2.consume().result_available_after
        cons2 = result2.consume().result_consumed_after
        #total_time = avail + cons + avail1 +cons1 +avail2 +cons2
        end = time.time()
        processingtime = end - starttime
    driver.close()
    return processingtime


def create_unique_data(database):

    cqlNodeQuery = "CREATE CONSTRAINT ON (e:Event) ASSERT e.name IS UNIQUE;"
    query2 = "CREATE CONSTRAINT ON (c:Case) ASSERT c.name IS UNIQUE;"
    createcasenode =  "LOAD CSV WITH HEADERS FROM $tablename as line WITH line.case as case MERGE (c:Case {name: case})";
    createeventnode = """LOAD CSV WITH HEADERS FROM $tablename as line
    WITH line.event as activity MERGE (e:Event {name: activity})""";
    createrelation = """LOAD CSV WITH HEADERS FROM $tablename as line MATCH(c:Case), (e:Event)
     WHERE c.name = line.case and e.name = line.event 
     CREATE (c) -[:Case_To_Event{position:line.position}]-> (e)""";

    with driver.session(database=database) as graphDB_Session:
        starttime = time.time()
        graphDB_Session.run(cqlNodeQuery)
        graphDB_Session.run(query2)
        result =graphDB_Session.run(createcasenode,tablename="file:///"+path_data)
        result1 = graphDB_Session.run(createeventnode,tablename="file:///" + path_data)
        result2 = graphDB_Session.run(createrelation,tablename="file:///" + path_data)
        avail = result.consume().result_available_after
        cons = result.consume().result_consumed_after
        avail1 = result1.consume().result_available_after
        cons1 = result1.consume().result_consumed_after
        avail2 = result2.consume().result_available_after
        cons2 = result2.consume().result_consumed_after
        #total_time = avail + cons + avail1 +cons1 +avail2 +cons2
        end = time.time()
        processingtime = end - starttime
    driver.close()
    return processingtime
##########################

# Main
total_time=0
event_time=0
unique_time=0
answer = True

while answer:
    CD = input("(1) Create Baseline Database or (2) Create Event position or (3) Create UA ");
    if CD == "1":
        Name = input("Baseline Name: ")
        create_database(Name)
        btime = create_baseline_data(Name)
        total_time += btime
    elif CD == "2":
        #unique event database
        Name1 = input("Event-position Name: ")
        create_database(Name1)
        etime = create_eventposition(Name1)
        print(etime)
        event_time += etime
    elif CD == "3":
        # unique Unique database
        Name2 = input("Unique Datase Name: ")
        create_database(Name2)
        #utime = create_unique(Name2)
        utime = create_unique_data(Name2)
        print(utime)
        #unique_time += utime
    else:
        Base = input("Drop Baseline Datase Name: ")
        drop_database(Base)
        #Event = input("Drop Event Datase Name: ")
        #drop_database(Event)
        Unique = input("Drop Unique Datase Name: ")
        drop_database(Unique)

    chooseone = (input("Would you like to choose another method?: "))
    if str(chooseone) == 'yes':
        answer = True
    else:
        answer = False
        print("baseline" + str(total_time))
        #print("Event" + str(event_time / 4))
        print("Unique" + str(unique_time))
#Unique Datase Name: log50u
#15.481086015701294

#Unique Datase Name: log100u
#33.07393932342529
