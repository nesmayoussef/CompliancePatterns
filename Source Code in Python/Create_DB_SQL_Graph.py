from venv import create
import pyodbc
import pandas as pd
import time
import datetime
import os.path

conn = pyodbc.connect('Driver={SQL Server};Server=LAPTOP-C2QFIL9D;Database=Logs;Trusted_Connection=yes;')
cursor = conn.cursor()

def drop(log):
    cursor.execute('Drop TABLE graph.Cases_base_' + log + ';');

# create of Baseline
# create cases node
def create_case_node_base(log):
    cursor.execute('Create TABLE graph.Cases_base_' + log + ' (case_id NVARCHAR(50) PRIMARY KEY ) AS NODE;');

def insert_data_cases_base(log):
    cursor.execute('INSERT INTO graph.Cases_base_' + log + ' (case_id) SELECT distinct caseid from ' + log + ';');

# create events node
#def create_event_node_base(log):
  #  cursor.execute(
  #      'Create TABLE graph.Events_base_' + log + '(event NVARCHAR(50), starttime Float NOT NULL,position int NOT NULL,caseindex int ) AS NODE;');

# create events node
def create_event_node_base(log):
    cursor.execute(
        'Create TABLE graph.Events_base_' + log + '(event NVARCHAR(50), position int NOT Null,caseindex int) AS NODE;');

#def insert_data_events_base(log):
 #   cursor.execute(
 #       'INSERT INTO graph.Events_base_' + log + ' (event,starttime,position,caseindex) SELECT event,sT, position,case_index from ' + log + ';');

def insert_data_events_base(log):
    cursor.execute(
        'INSERT INTO graph.Events_base_' + log + ' (event,position,caseindex) SELECT event, position,caseindex from ' + log + ';');

# create edges
#def create_edge_node_base(log):
 #   cursor.execute('Create TABLE graph.casetoevent_base_' + log + ' (starttime Float NOT NULL) AS EDGE;');

def create_edge_node_base(log):
    cursor.execute('Create TABLE graph.casetoevent_base_' + log + ' AS EDGE;');


#def insert_data_edge_base(log):
 #   cursor.execute('INSERT INTO graph.casetoevent_base_' + log + ' ($from_id, $to_id, starttime) '
  #                                                              'select c.node1, e.node2, d.sT from ' + log + ' as d '
  #                                                                                                            'inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases_base_' + log + ') c '
       #                                                                                                                                                                                            'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, caseindex, starttime FROM graph.Events_base_' + log + ') e on d.case_index = e.caseindex and d.sT = e.starttime');

def insert_data_edge_base(log):
    cursor.execute('INSERT INTO graph.casetoevent_base_' + log + ' ($from_id, $to_id) '
                   'select c.node1, e.node2 from ' + log + ' as d '
                   'inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases_base_' + log + ') c '
                   'on d.caseid = c.case_id inner join (SELECT $node_id AS node2,caseindex FROM graph.Events_base_' + log +
                   ') e on d.caseindex = e.caseindex');


#def insert_data_edge_base(log):
 #   cursor.execute('INSERT INTO graph.casetoevent_base_' + log + ' ($from_id, $to_id, starttime) '
  #                                                               'select c.node1, e.node2, d.sT from ' + log + ' as d inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases_base_' + log + ') c '
   #                                                                                                                                                                                                'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, event, starttime FROM graph.Events_base_' + log + ') e on d.event = e.event and d.sT = e.starttime');

# create edges
def create_edge_DF_base(log):
    cursor.execute('Create TABLE graph.df_base_' + log + '  AS EDGE;');


def insert_DF_edge_base(log):
    cursor.execute('INSERT INTO graph.df_base_' + log + ' ($from_id, $to_id) '
                                                            'select e.$node_id, e1.$node_id '
                                                        'from graph.Events_base_'+ log +' as e, graph.Events_base_'+ log +' as e1, graph.Cases_base_'+ log +' as c, graph.casetoevent_base_'+ log +' as r, graph.casetoevent_base_'+ log +' as r1 '
                                                        'where Match(c - (r)->e and c - (r1)->e1) and (e1.caseindex - e.caseindex) = 1');


def base_act(log):
    create_case_node_base(log)
    insert_data_cases_base(log)
    create_event_node_base(log)
    insert_data_events_base(log)

def base_casetoevent(log):
    create_edge_node_base(log)
    insert_data_edge_base(log)

def base_df(log):
    create_edge_DF_base(log)
    insert_DF_edge_base(log)

def precede_base(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log +
''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ?
and e.starttime < e1.starttime 
and (((e1.starttime - e.starttime)/3600)*60) > ?
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log +
''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta)
    return cursor.fetchall();

def precede_base_min(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log + ''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ?
and e.starttime < e1.starttime 
and (((e1.starttime - e.starttime)/3600)*60) < ?
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta)
    return cursor.fetchall();


def precede_base_without_time(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log +
''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',actb,acta)
    return cursor.fetchall();

def response_base_without_time(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log +
''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb)
    return cursor.fetchall();



def response_base(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log + ''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ?
and e1.starttime > e.starttime   
and (((e1.starttime - e.starttime)/3600)*60) > ?
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,acta,actb)
    return cursor.fetchall();

def response_base_min(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log + ''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ?
and e1.starttime  > e.starttime  
and (((e1.starttime - e.starttime)/3600)*60) < ?
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,acta,actb)
    return cursor.fetchall();
# create of EP
# create cases node
def create_case_node_ep(log):
    cursor.execute('Create TABLE graph.Cases_ep_' + log + ' (case_id NVARCHAR(50) PRIMARY KEY ) AS NODE;');


def insert_data_cases_ep(log):
    cursor.execute('INSERT INTO graph.Cases_ep_' + log + ' (case_id) SELECT distinct caseid from ' + log + ';');


# create events node
def create_event_node_ep(log):
    cursor.execute(
        'Create TABLE graph.Events_ep_' + log + ' (eventpos NVARCHAR(50) PRIMARY KEY,event NVARCHAR(50) NOT NULL,position int NOT NULL ) AS NODE;');


def insert_data_events_ep(log):
    cursor.execute(
        'INSERT INTO graph.Events_ep_' + log + ' (eventpos,event,position) SELECT distinct eventpos , event, position from ' + log + ';');


# create edges
def create_edge_node_ep(log):
    cursor.execute('Create TABLE graph.casetoevent_ep_' + log + ' ( starttime Float NOT NULL) AS EDGE;');


def insert_data_edge_ep(log):
    cursor.execute('INSERT INTO graph.casetoevent_ep_' + log + ' ($from_id, $to_id, starttime) '
                                                               'select c.node1, e.node2, d.sT from ' + log + ' as d inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases_ep_' + log + ') c '
                                                                                                                                'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, eventpos FROM graph.Events_ep_' + log + ') e on d.eventpos = e.eventpos');


# preced anti-patterns
def precede_ep(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r, graph.Events_ep_''' + log + ''' e1, graph.casetoevent_ep_''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and e.position < e1.position and ((r2.starttime - r.starttime)/3600)*60 > ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases_ep_''' + log + ''' a , graph.Events_ep_''' + log + ''' e2, graph.casetoevent_ep_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta)
    return cursor.fetchall();

def precede_ep_min(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r, graph.Events_ep_''' + log + ''' e1, graph.casetoevent_ep_''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and e.position < e1.position and ((r2.starttime - r.starttime)/3600)*60 < ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases_ep_''' + log + ''' a , graph.Events_ep_''' + log + ''' e2, graph.casetoevent_ep_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta)
    return cursor.fetchall();

def response_ep_max(acta, actb, log,time):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r, graph.Events_ep_''' + log + ''' e1, graph.casetoevent_ep_''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and e1.position > e.position and ((r2.starttime - r.starttime)/3600)*60 > ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases_ep_''' + log + ''' a , graph.Events_ep_''' + log + ''' e2, graph.casetoevent_ep_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,time,acta,actb)
    return cursor.fetchall();

def response_ep_min(acta, actb, log,time):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r, graph.Events_ep_''' + log + ''' e1, graph.casetoevent_ep_''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and e1.position > e.position and ((r2.starttime - r.starttime)/3600)*60 < ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases_ep_''' + log + ''' c, graph.Events_ep_''' + log + ''' e, graph.casetoevent_ep_''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases_ep_''' + log + ''' a , graph.Events_ep_''' + log + ''' e2, graph.casetoevent_ep_''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,time,acta,actb)
    return cursor.fetchall();

def ep_act(log):
    strtime = time.time()
    create_case_node_ep(log)
    insert_data_cases_ep(log)
    create_event_node_ep(log)
    insert_data_events_ep(log)
    create_edge_node_ep(log)
    insert_data_edge_ep(log)
    end = time.time()
    result = str(end-strtime)
    return result


# create of unique activities
# create cases node
def create_case_node(log):
    cursor.execute('Create TABLE graph.Cases' + log + ' (case_id NVARCHAR(50) PRIMARY KEY ) AS NODE;');


def insert_data_cases(log):
    cursor.execute('INSERT INTO graph.Cases' + log + ' (case_id) SELECT distinct caseid from ' + log + ';');


# create events node
def create_event_node(log):
    cursor.execute('Create TABLE graph.Events' + log + ' (event NVARCHAR(50) PRIMARY KEY ) AS NODE;');


def insert_data_events(log):
    cursor.execute('INSERT INTO graph.Events' + log + ' (event) SELECT distinct event from ' + log + ';');


# create edges
#def create_edge_node(log):
#    cursor.execute(
#        'Create TABLE graph.casetoevent' + log + ' ( starttime Float NOT NULL,position int NOT NULL ) AS EDGE;');
def create_edge_node(log):
    cursor.execute(
        'Create TABLE graph.casetoevent' + log + ' (position int NOT NULL ) AS EDGE;');


#def insert_data_edge(log):
#    cursor.execute('INSERT INTO graph.casetoevent' + log + ' ($from_id, $to_id, starttime, position) '
#                                                           'select c.node1, e.node2, d.sT, d.position from ' + log + ' as d inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases' + log + ') c '
#                                                                                                                                                                                                    'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, event FROM graph.Events' + log + ') e on d.event = e.event');

#def insert_data_edge(log):
#    cursor.execute('INSERT INTO graph.casetoevent' + log + ' ($from_id, $to_id, starttime, position) '
#    'select c.node1, e.node2, d.sT, d.position from ' + log + ' as d inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases' + log + ') c '
 #   'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, event FROM graph.Events' + log + ') e on d.event = e.event');
def insert_data_edge(log):
    cursor.execute('INSERT INTO graph.casetoevent' + log + ' ($from_id, $to_id, position) '
    'select c.node1, e.node2, d.position from ' + log + ' as d inner join  (SELECT $node_id AS node1, case_id FROM graph.Cases' + log + ') c '
    'on d.caseid = c.case_id inner join (SELECT $node_id AS node2, event FROM graph.Events' + log + ') e on d.event = e.event');

# preced anti-patterns
def precede_unique_withouttime(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2 
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and r.position < r2.position
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,actb,acta);

    return cursor.fetchall();
# preced anti-patterns
def precede_unique(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2 
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and r.position < r2.position and ((r2.starttime - r.starttime)/3600)*60 > ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta);

    return cursor.fetchall();

def precede_unique_min(acta, actb, log,t):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2 
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and r.position < r2.position and ((r2.starttime - r.starttime)/3600)*60 < ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,t,actb,acta);
    return cursor.fetchall();

def response_unique_max(acta, actb, log,time):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and r2.position > r.position and ((r2.starttime - r.starttime)/3600)*60 > ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,time,acta,actb)
    return cursor.fetchall();

def response_unique_min(acta, actb, log,time):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and r2.position > r.position and ((r2.starttime - r.starttime)/3600)*60 < ?
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,time,acta,actb)
    return cursor.fetchall();

def unique_act(log):
    strtime = time.time()
    create_case_node(log)
    #conn.commit()
    insert_data_cases(log)
    create_event_node(log)
    #conn.commit()
    insert_data_events(log)
    create_edge_node(log)
    #conn.commit()
    insert_data_edge(log)
    end = time.time()
    result = str(end-strtime)
    return result

def execlude (log,a,b,c):
    cursor.execute('select distinct a.caseid from ' + log + ' as a , ' + log + ' as b, ' + log + ' as c '
                                                                                                 'where a.caseid = b.caseid  and c.caseid = b.caseid and a.event = \'' + a + '\' and b.event = \'' + b + '\' and c.event= \'' + c + '\'  and a.position < b.position and b.position < c.position '
                                                                                                                                                                                                                                       'Union select distinct a.caseid from ' + log + ' as a where a.event = \'' + a + '\' and a.caseid not in (select caseid from [dbo].[BPI15] where event = \'' + b + '\') ')
    return cursor.fetchall()


def execludeMax (log,a,b,c,max):
    cursor.execute('select distinct a.caseid from ' + log + ' as a , ' + log + ' as b, ' + log + ' as c '
                                                                                                 'where a.caseid = b.caseid  and c.caseid = b.caseid and a.event = \'' + a + '\' and b.event = \'' + b + '\' and c.event= \'' + c + '\'  and a.position < b.position and b.position < c.position and ((b.sT - a.sT)/3600)*60 > ? '
                                                                                                                                                                                                                                       ' Union select distinct a.caseid from ' + log + ' as a where a.event = \'' + a + '\' and a.caseid not in (select caseid from [dbo].[BPI15] where event = \'' + b + '\')',max)
    return cursor.fetchall()

def execludeMin (log,a,b,c,max):
    cursor.execute('select distinct a.caseid from ' + log + ' as a , ' + log + ' as b, ' + log + ' as c '
                                                                                                 'where a.caseid = b.caseid  and c.caseid = b.caseid and a.event = \'' + a + '\' and b.event = \'' + b + '\' and c.event= \'' + c + '\'  and a.position < b.position and b.position < c.position and ((b.sT - a.sT)/3600)*60 < ? '
                                                                                                                                                                                                                                       ' Union select distinct a.caseid from ' + log + ' as a where a.event = \'' + a + '\' and a.caseid not in (select caseid from [dbo].[BPI15] where event = \'' + b + '\')',max)
    return cursor.fetchall()


#Chain Preced Unique
def chainPreced_UA(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and ((r2.position - r.position) > 1)
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,actb,acta)
    return cursor.fetchall();

#Chain Response Unique
def chainResponcse_UA(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and ((r2.position - r.position) > 1)
	  Union
	  SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,acta,actb)
    return cursor.fetchall();


def chainPreced_base(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log +
''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ? and (e1.caseindex - e.caseindex) > 1
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log +
''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',actb,acta,actb,acta)
    return cursor.fetchall();

def chainResponse_base(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e
, graph.casetoevent_base_''' + log + ''' r, graph.Events_base_''' + log +
''' e1, graph.casetoevent_base_''' + log + ''' r2,[graph].[df_base_''' + log + '''] as df
WHERE MATCH(c-(r)->e AND c-(r2)->e1 and e-(df)->e1)  
and e.event = ? and e1.event = ?
Union
SELECT distinct c.case_id,e.event
FROM graph.Cases_base_''' + log + ''' c, graph.Events_base_''' + log + ''' e, graph.casetoevent_base_''' + log + ''' r
where MATCH(c-(r)->e) and e.event = ? 
and c.case_id not in (select a.case_id from graph.Cases_base_''' + log + ''' a 
, graph.Events_base_''' + log + ''' e2, graph.casetoevent_base_''' + log +
''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb,acta,actb)
    return cursor.fetchall();

#Responded Existence Pattern UA
def RE_UA_Pattern(acta, actb, log):
    cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r, graph.Events''' + log + ''' e1, graph.casetoevent''' + log + ''' r2
	  WHERE MATCH(c-(r)->e AND c-(r2)->e1) and e.event = ? and e1.event = ? and (r2.position > r.position)''',acta,actb)
    return cursor.fetchall();


#Responded Existence Antipattern UA
def RE_UA(acta,actb,log):
      cursor.execute('''SELECT distinct c.case_id,e.event
	  FROM graph.Cases''' + log + ''' c, graph.Events''' + log + ''' e, graph.casetoevent''' + log + ''' r
	  where MATCH(c-(r)->e) and e.event = ? and c.case_id not in (select a.case_id from graph.Cases''' + log + ''' a, graph.Events''' + log + ''' e2, graph.casetoevent''' + log + ''' r3 where MATCH(a-(r3)->e2) and e2.event=?)''',acta,actb)
      return cursor.fetchall();

val = input('Do you want to create a graph, Yes/NO')
if val == 'Yes':
    x=[]
    y=[]
    file_exists = os.path.isfile('loadingtime_sqlgraph.csv')
    logname = input("Enter log name")
    ti = unique_act(logname)
    starttime = time.time()
    #x.append(ti)
    #y.append("Unique"+logname)
    conn.commit()
    endtime = time.time()
    time_base = str(endtime - starttime)
    print(time_base)
    #ti_ep = ep_act(logname)
    #x.append(ti_ep)
    #y.append("EP"+logname)
    #conn.commit()
    #drop(logname)
   # insert_DF_edge_base(logname)
    starttime = time.time()
    #base_act(logname)
    #conn.commit()
    #base_casetoevent(logname)
    #conn.commit()
    #base_df(logname)
    #conn.commit()
    endtime = time.time()
    time_base = str(endtime - starttime)
    x.append(time_base)
    y.append("Base " + logname)
    conn.commit()
    d = {'LT': x, 'Method': y}
    # d = {'Timestamp': x}
    dataframe = pd.DataFrame(d)
    if not file_exists:
        dataframe.to_csv('loadingtime_sqlgraph1.csv', mode='a', index=False,
                         header=['LT', 'Method'])
        file_exists = True
    else:
        dataframe.to_csv('loadingtime_sqlgraph1.csv', mode='a', index=False, header=False)
else:

    file_exists = os.path.isfile('Executiontime_sqlgraph_antipatterns.csv')
    openfile = input('File name.txt: ')
    with open(str(openfile), "r") as file:
        #val = input("Maxp-ep or Maxp or Minp-ep or Minp or Max-ep or Max or Min-ep or Min or Res-without or Prec-without")
        val = input("1-Chain Preced base , 2-ChainResponse base , 3-Chain Preced UA, 4-Chain Response UA,5-RE Unique")

        db = input("dbname : ")
        for line in file:
            x = []
            y = []
            z = []
            m = []
            type = ""
            mylist = []
            # reading each word
            for word in line.split("\""):
                # displaying the words
                mylist.append(word)
            # took every word in specific attribute
            # logname  = 'BPI20151'
            acta = mylist[1]
            actb = mylist[3]
            # actc = mylist[3]
            #max = mylist[4]
            print(acta + ' ' + actb )
            # input from user:
            if val == "Maxp-ep":
                # start
                strtime = time.time()
                data = precede_ep(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type="EP " + db
            elif val == "Maxp":
                strtime = time.time()
                data = precede_unique(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "unique "+db
            elif val == "Maxp-base":
                strtime = time.time()
                data = precede_base(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "base " + db
            elif val == "Minp-ep":
                # start
                strtime = time.time()
                data = precede_ep_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type="EP " + db
            elif val == "Minp":
                strtime = time.time()
                data = precede_unique_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "unique "+db
            elif val == "Minp-base":
                strtime = time.time()
                data = precede_base_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "base " + db
            elif val == "Max-ep":
                # start
                strtime = time.time()
                data = response_ep_max(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "EP " + db
            elif val == "Max":
                # start
                strtime = time.time()
                data = response_unique_max(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "unique " + db
            elif val == "Max-base":
                # start
                strtime = time.time()
                data = response_base(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "base " + db
            elif val == "Min-ep":
                # start
                strtime = time.time()
                data = response_ep_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "EP " + db
            elif val == "Min":
                # start
                strtime = time.time()
                data = response_unique_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "unique " + db
            elif val == "Min-base":
                # start
                strtime = time.time()
                data = response_base_min(acta, actb, db, float(max))
                print(len(data))
                end = time.time()
                type = "base " + db

            elif val == "Res-without":
                # start
                strtime = time.time()
                data = response_base_without_time(acta, actb,db)
                print(len(data))
                end = time.time()
            elif val == "Prec-without":
                # start
                strtime = time.time()
                data = precede_base_without_time(acta, actb,db)
                print(len(data))
                end = time.time()
            elif val == "Resu-without":
                # start
                strtime = time.time()
                data = response_base_without_time(acta, actb,db)
                print(len(data))
                end = time.time()
            elif val == "Precu-without":
                # start
                strtime = time.time()
                data = precede_unique_withouttime(acta, actb,db)
                print(len(data))
                end = time.time()
            elif val == "1":
                strtime = time.time()
                data = chainPreced_base(acta,actb,db)
                print(len(data))
                end = time.time()
                type = "Chain Preced Base " + db
            elif val == "2":
                strtime = time.time()
                data = chainResponse_base(acta, actb, db)
                print(len(data))
                end = time.time()
                type = "Chain Response Base "+ db
            elif val == "3":
                strtime = time.time()
                data = chainPreced_UA(acta, actb, db)
                print(len(data))
                end = time.time()
                type = "Chain Precede UA "+ db
            elif val == "4":
                strtime = time.time()
                data = chainResponcse_UA(acta, actb, db)
                print(len(data))
                end = time.time()
                type = "Chain Response Base "+ db
            elif val == "5":
                strtime = time.time()
                data = RE_UA(acta, actb, db)
                print(len(data))
                end = time.time()
                type = "Responded Existence Unique"+ db

            x.append(str((end - strtime)))
            y.append(len(data))
            z.append(val)
            m.append(type)
            strtime = 0
            end = 0
            # then add it to dataframe
            d = {'Timestamp': x, 'data': y,'Method':z,'type':m}
            # d = {'Timestamp': x}
            dataframe = pd.DataFrame(d)
            if not file_exists:
                dataframe.to_csv('Executiontime_sqlgraph_antipatterns.csv', mode='a', index=False, header=['Timestamp', 'data','Method','type'])
                file_exists = True
            else:
                dataframe.to_csv('Executiontime_sqlgraph_antipatterns.csv', mode='a', index=False, header=False)


