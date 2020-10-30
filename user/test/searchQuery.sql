 
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
                        (SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
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
                        LEFT OUTER JOIN 
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw0||'%'
                        GROUP BY 
                            pid
                    ) 
                        USING (pid) 

                        UNION

                        SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw0||'%'
                        GROUP BY 
                            pid
                    )
                        LEFT OUTER JOIN
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
                        USING (pid)
                        )
                    
UNION ALL

                    SELECT 
                        pid,
                        ifnull(numTitleBodyMatches, 0) as numTitleBodyMatches,
                        ifnull(numTagMatches, 0) as numTagMatches
                    FROM 
                        (SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw1, ''))) / length(:kw1)
                                  + (length(lower(body))-length(replace(lower(body), :kw1, ''))) / length(:kw1) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw1||'%'
                                OR p.body LIKE '%'||:kw1||'%'
                            ) 
                        LEFT OUTER JOIN 
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw1||'%'
                        GROUP BY 
                            pid
                    ) 
                        USING (pid) 

                        UNION

                        SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw1||'%'
                        GROUP BY 
                            pid
                    )
                        LEFT OUTER JOIN
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw1, ''))) / length(:kw1)
                                  + (length(lower(body))-length(replace(lower(body), :kw1, ''))) / length(:kw1) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw1||'%'
                                OR p.body LIKE '%'||:kw1||'%'
                            )
                        USING (pid)
                        )
                    
UNION ALL

                    SELECT 
                        pid,
                        ifnull(numTitleBodyMatches, 0) as numTitleBodyMatches,
                        ifnull(numTagMatches, 0) as numTagMatches
                    FROM 
                        (SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw2, ''))) / length(:kw2)
                                  + (length(lower(body))-length(replace(lower(body), :kw2, ''))) / length(:kw2) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw2||'%'
                                OR p.body LIKE '%'||:kw2||'%'
                            ) 
                        LEFT OUTER JOIN 
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw2||'%'
                        GROUP BY 
                            pid
                    ) 
                        USING (pid) 

                        UNION

                        SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            (
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw2||'%'
                        GROUP BY 
                            pid
                    )
                        LEFT OUTER JOIN
                            (
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw2, ''))) / length(:kw2)
                                  + (length(lower(body))-length(replace(lower(body), :kw2, ''))) / length(:kw2) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw2||'%'
                                OR p.body LIKE '%'||:kw2||'%'
                            )
                        USING (pid)
                        )
                    )
            GROUP BY pid
            ) left outer join (
                SELECT
                    pid,
                    count(vno) as numVotes
                FROM 
                    votes v
                GROUP BY 
                    pid
            ) using (pid) 
                                left outer join (
            SELECT
                q.pid as qid,
                ifnull(count(a.pid), 0) as numAns
            FROM 
                questions q 
            LEFT OUTER JOIN 
                answers a 
            ON 
                q.pid=qid
            GROUP BY 
                q.pid
            ) on pid = qid

                     ) as search
                    WHERE
                        p.pid = search.pid
                    ORDER BY search.numMatches DESC;
                    