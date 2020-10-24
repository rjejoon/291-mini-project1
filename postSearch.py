import sqlite3


def searchPosts(conn, curr, uid):

    prompt = "Enter keywords to search, each separated by a comma: "
    keywords = input(prompt).lower().replace("'", "''").split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))
    print(keywords)

    curr.executescript(
            '''drop table if exists searchResult;

               create table searchResult (
                    pid     char(4),
                    numMatches  integer,
                    numVotes integer,
                    numAns integer,
                    primary key (pid),
                    foreign key (pid) references posts
                );

                insert into searchResult 
                select pid, 0, 0, 0
                from posts;
            ''')

    conn.commit()
    

    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}
    print(keywords)
        
    matchingQueries = []
    for i, kw in enumerate(keywords.keys()):
        matchingPostsQuery = getMatchingPosts(i)
        matchingQueries.append(matchingPostsQuery)

    q = '\nUnion all\n'.join(matchingQueries) 
    with open('./testQuery.sql', 'w') as f:
        f.write(q)

    curr.execute(q, keywords)
    for row in curr.fetchall():
        print(row)
                    
def getMatchingPosts(i):

    matchingTitleBodyTable = '''
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw{0}, ''))) / length(:kw{0})
                                  + (length(lower(body))-length(replace(lower(body), :kw{0}, ''))) / length(:kw{0}) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw{0}||'%'
                                OR p.body LIKE '%'||:kw{0}||'%'
                            '''.format(i) 
    matchingTagTable = '''
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        from 
                            tags t
                        where
                            tag like '%'||:kw{0}||'%'
                        group by pid
                    '''.format(i)

    numVotesTable = '''
                        SELECT
                            pid,
                            count(vno) as numVotes
                        FROM 
                            votes v
                        GROUP BY pid
                    '''

    numAnsTable = '''
                    SELECT
                        qid,
                        count(pid) as numAns
                    FROM
                        answers 
                    group by qid
                '''

    matchingPosts = '''
                    SELECT pid, numTitleBodyMatches, numTagMatches

                    FROM
                        ({0}) 
                            left outer join 
                        ({1}) 
                            using (pid) 

                    union

                    SELECT pid, numTitleBodyMatches, numTagMatches

                    FROM
                        ({1})
                            left outer join
                        ({0})
                            using (pid)
                    '''.format(matchingTitleBodyTable, matchingTagTable)

    matchingPostsQuery = '''
                        SELECT 
                            pid, 
                            numTitleBodyMatches + ifnull(numTagMatches, 0)
                                as numMatches,
                            ifnull(numVotes, 0),
                            numAns
                        FROM
                            ({}) left outer join ({}) using (pid) 
                                left outer join ({}) on pid = qid
                     '''.format(matchingPosts, 
                                numVotesTable, 
                                numAnsTable)

    # TODO add semicolon

    # TODO currently working on only matches
    return matchingPosts
        
         

def isMatch(title, body):

    for kw in keywords:
        if (kw in title) or (kw in body):
            return 1

    return 0
    


if __name__ == '__main__':
    conn = sqlite3.connect('./test.db')
    curr = conn.cursor()
    searchPosts(conn, curr, 'rjej')


    

    
    
