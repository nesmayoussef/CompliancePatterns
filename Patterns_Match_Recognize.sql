select distinct case_ID
from My_log MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'A',
              S AS S.Activity_ID <> 'A' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'C' AND S.Activity_ID <> 'D',
              B AS ((B.Activity_ID = 'B' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'A',
              S AS S.Activity_ID <> 'A' AND S.Activity_ID <> 'B',
              E AS E.Activity_ID = 'END'
     );
--Q11     
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'send confirmation receipt' AND S.Activity_ID <> 'request complete',
              B AS ((B.Activity_ID = 'send confirmation receipt' AND  (B.Time_stamp - A.time_stamp) > interval '20' minute)) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'send confirmation receipt',
              E AS E.Activity_ID = 'END'
     );
     
--Q20
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'send confirmation receipt' AND S.Activity_ID <> 'request complete',
              B AS ((B.Activity_ID = 'send confirmation receipt' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'send confirmation receipt',
              E AS E.Activity_ID = 'END'
     );
--Q21     
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'send confirmation receipt' AND S.Activity_ID <> 'request complete',
              B AS ((B.Activity_ID = 'send confirmation receipt' AND  (B.Time_stamp - A.time_stamp) < interval '20' minute)) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'send confirmation receipt',
              E AS E.Activity_ID = 'END'
     );     
     
--Q30
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'registration date publication',
              S AS S.Activity_ID <> 'registration date publication' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'receive additional information' AND S.Activity_ID <> 'request complete',
              B AS ((B.Activity_ID = 'receive additional information' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'registration date publication',
              S AS S.Activity_ID <> 'registration date publication' AND S.Activity_ID <> 'receive additional information',
              E AS E.Activity_ID = 'END'
     );
--Q31     
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'registration date publication',
              S AS S.Activity_ID <> 'registration date publication' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'receive additional information' AND S.Activity_ID <> 'request complete',
              B AS ((B.Activity_ID = 'receive additional information' AND  (B.Time_stamp - A.time_stamp) > interval '200' minute)) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'registration date publication',
              S AS S.Activity_ID <> 'registration date publication' AND S.Activity_ID <> 'receive additional information',
              E AS E.Activity_ID = 'END'
     );

--Q40
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'register submission date request',
              S AS S.Activity_ID <> 'register submission date request' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'forward to the competent authority' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'forward to the competent authority' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'register submission date request',
              S AS S.Activity_ID <> 'register submission date request' AND S.Activity_ID <> 'forward to the competent authority',
              E AS E.Activity_ID = 'END'
     );
--Q41     
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'register submission date request',
              S AS S.Activity_ID <> 'register submission date request' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'forward to the competent authority' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'forward to the competent authority' AND  (B.Time_stamp - A.time_stamp) > interval '10' minute)) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'register submission date request',
              S AS S.Activity_ID <> 'register submission date request' AND S.Activity_ID <> 'forward to the competent authority',
              E AS E.Activity_ID = 'END'
     );
     
--Q50
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'treat subcases completeness' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'treat subcases completeness' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'treat subcases completeness',
              E AS E.Activity_ID = 'END'
     );
     
--Q51
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'treat subcases completeness' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'treat subcases completeness' AND  (B.Time_stamp - A.time_stamp) > interval '4' minute )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'treat subcases completeness',
              E AS E.Activity_ID = 'END'
     );
--Q60
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'treat subcases completeness' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'treat subcases completeness' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'treat subcases completeness',
              E AS E.Activity_ID = 'END'
     );
     
--Q61
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'treat subcases completeness' AND S.Activity_ID <> 'procedure change',
              B AS ((B.Activity_ID = 'treat subcases completeness' AND  (B.Time_stamp - A.time_stamp) < interval '4' minute )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'inform BAG administrator',
              S AS S.Activity_ID <> 'inform BAG administrator' AND S.Activity_ID <> 'treat subcases completeness',
              E AS E.Activity_ID = 'END'
     );
     
--Q70
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'phase application received' AND S.Activity_ID <> 'terminate on request',
              B AS ((B.Activity_ID = 'phase application received' )) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'phase application received',
              E AS E.Activity_ID = 'END'
     );

--Q71
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* B)
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'END' AND S.Activity_ID <> 'phase application received' AND S.Activity_ID <> 'terminate on request',
              B AS ((B.Activity_ID = 'phase application received' AND  (B.Time_stamp - A.time_stamp) < interval '4' minute)) 
     )
union
select distinct case_ID
from My_log_2015_2 MATCH_RECOGNIZE(
     PARTITION BY Case_ID
     ORDER BY Time_stamp
     ONE ROW PER MATCH
     AFTER MATCH SKIP TO NEXT ROW
     PATTERN (A S* E )
     DEFINE
              A AS Activity_ID = 'OLO messaging active',
              S AS S.Activity_ID <> 'OLO messaging active' AND S.Activity_ID <> 'phase application received',
              E AS E.Activity_ID = 'END'
     );
