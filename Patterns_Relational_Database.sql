# Response pattern with exclude 
SELECT DISTINCT e1.cid
FROM log e1, log e2 , log e3 
where e1.cid = e2.cid and e1.cid = e3.cid 
AND e2.position > e1.position AND e3.position > e1.position AND e3.position < e2.position 
AND e1.act = 'A'
AND e2.act = 'B'
AND e3.act in('C','D')

# ALternate Response Pattern with exclude
SELECT DISTINCT e1.cid
FROM log e1 , log e2 , log e3, log e4
Where e1.cid = e2.cid and e2.position > e1.position
and e1.cid = e3.cid AND e3.position > e1.position 
and e1.cid = e4.cid AND e4.position > e1.position AND e4.position < e2.position
and e1.act = 'A'
AND e2.act = 'B'
AND (e3.act in ('A')
OR e4.act in ('C','D'))

#Chain Response with exclude
SELECT DISTINCT e1.cid
FROM log e1
JOIN log e2 ON e1.cid = e2.cid and e2.position > e1.position
LEFT JOIN log e3 ON e1.cid = e3.cid AND e3.position > e1.position AND e3.position < e2.position
WHERE e1.act = 'A'
AND e2.act = 'B'
AND e3.act is NULL


# Precedence pattern with exclude
SELECT DISTINCT e1.cid
FROM log e1, log e2 , log e3 
where e1.cid = e2.cid and e1.cid = e3.cid 
AND e2.position < e1.position AND e3.position > e2.position AND e3.position < e1.position 
AND e1.act = 'B'
AND e2.act = 'A'
AND e3.act in('C','D')


# ALternate Precedence with exclude
SELECT DISTINCT e1.cid
FROM log e1 , log e2 , log e3, log e4
Where e1.cid = e2.cid and e2.position < e1.position
and e1.cid = e3.cid AND e1.position > e3.position 
and e1.cid = e4.cid AND e4.position > e2.position AND e4.position < e1.position
and e1.act = 'B'
AND e2.act = 'A'
AND (e3.act in ('B')
OR e4.act in ('C','D'))


# Chain Precedence pattern with exclude
SELECT DISTINCT e1.cid
FROM log e1
JOIN log e2 ON e1.cid = e2.cid and e2.position < e1.position
LEFT JOIN log e3 ON e1.cid = e3.cid AND e3.position > e2.position AND e3.position < e1.position
WHERE e1.act = 'B'
AND e2.act = 'A'
AND e3.act is NULL

#Choice
SELECT DISTINCT e1.cid
FROM log e1
WHERE e1.act in('A','B')

#Last
SELECT DISTINCT e1.cid
FROM log e1
WHERE e1.act = 'D'
and not exists (select 1 from log as e2 where e2.cid = e1.cid and e2.position > e1.position)

#Absence
SELECT DISTINCT e1.cid
FROM log e1
WHERE not exists (select 1 from log e2 
where e2.cid = e1.cid and e2.act in ('A','B'))

#Existence
SELECT DISTINCT e1.cid
FROM log e1
WHERE exists (select 1 from log e2 
where e2.cid = e1.cid and e2.act in ('C'))
