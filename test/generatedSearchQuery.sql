 
SELECT
    p.pid,
    pdate,
    title,
    body,
    poster,
    numVotes,
    numAns,
    numMatches
FROM 
    posts p,
    (
    SELECT 
        pid, 
        numMatches,
        ifnull(numVotes, 0) as numVotes,
        numAns
    FROM
        (
            SELECT 
                pid, 
                sum(numTitleBodyMatches) + sum(numTagMatches) as numMatches
            FROM
                (
                    SELECT 
                        pid,
                        ifnull(numTitleBodyMatches, 0) as numTitleBodyMatches,
                        ifnull(numTagMatches, 0) as numTagMatches
                    FROM 
                        (SELECT pid, numTitleBodyMatches, numTagMatches

                        FROM
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw0, ''))) / length(:kw0)
                                  + (length(lower(body))-length(replace(lower(body), :kw0, ''))) / length(:kw0) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw0||'%'
                                OR p.body LIKE '%'||:kw0||'%'
                            ) 
                                left outer join 
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        from 
                            tags t
                        where
                            tag like '%'||:kw0||'%'
                        group by pid
                    ) 
                                using (pid) 

                        union

                        SELECT pid, numTitleBodyMatches, numTagMatches

                        FROM
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        from 
                            tags t
                        where
                            tag like '%'||:kw0||'%'
                        group by pid
                    )
                                left outer join
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw0, ''))) / length(:kw0)
                                  + (length(lower(body))-length(replace(lower(body), :kw0, ''))) / length(:kw0) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw0||'%'
                                OR p.body LIKE '%'||:kw0||'%'
                            )
                                using (pid)
                        )
                    )
            GROUP BY pid
            ) left outer join (
                        SELECT
                            pid,
                            count(vno) as numVotes
                        FROM 
                            votes v
                        GROUP BY pid
                    ) using (pid) 
                                left outer join (
                    SELECT
                        q.pid as qid,
                        ifnull(count(a.pid), 0) as numAns
                    FROM questions q LEFT OUTER JOIN answers a ON q.pid=qid
                    GROUP BY q.pid
                ) on pid = qid

                     ) as search
                    WHERE
                        p.pid = search.pid
                    ORDER BY search.numMatches DESC;
                    
