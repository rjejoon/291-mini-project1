import sqlite3

conn = sqlite3.connect('./test.db')
curr = conn.cursor()

def searchPosts(conn, curr, uid):

    prompt = "Enter keywords to search, each separated by a comma: "
    keywords = input(prompt).lower().split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))

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
    
    matchTitleBodyTable = '''
                            SELECT 
                                pid,
                                (length(title)-length(replace(title, :kw, ''))) / length(:kw)
                                  + (length(body)-length(replace(body, :kw, ''))) / length(:kw) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE '%'||:kw||'%'
                                OR p.body LIKE '%'||:kw||'%'
                            ''' 
    matchTagTable = '''
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        from 
                            tags t
                        where
                            tag like '%'||:kw||'%'
                    '''

    numMatchQuery = '''
                        SELECT 
                            pid, 
                            numTitleBodyMatches + ifnull(numTagMatches, 0)
                                as numMatches
                        FROM
                            ({}) left outer join ({}) using (pid)
                     '''.format(matchTitleBodyTable, matchTagTable)

    for kw in keywords:
        curr.execute(numMatchQuery,{'kw':kw})
        for row in curr.fetchall():
            print(row)




         
    #numAns = curr.execute("SELECT count(pid) FROM answers WHERE pid = :")


def isMatch(title, body):

    for kw in keywords:
        if (kw in title) or (kw in body):
            return 1

    return 0
    


if __name__ == '__main__':
    searchPosts(conn, curr, 'rjej')


    

    
    
