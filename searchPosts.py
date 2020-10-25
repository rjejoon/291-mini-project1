import sqlite3
import sys


def searchPosts(conn, curr, uid):

    prompt = "Enter keywords to search, each separated by a comma: "
    # TODO add error checking

    keywords = input(prompt).lower().replace("'", "''").split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))
    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}
        
    fullSearchQuery = genSearchResult(keywords)

    # write full query to check
    with open('./generatedSearchQuery.sql', 'w') as f:
        f.write(fullSearchQuery)

    curr.execute(fullSearchQuery, keywords)
    resultTable = curr.fetchall()
    displaySearchResult(resultTable)

    return resultTable


def displaySearchResult(results):

    for row in results:
        print(row)
    rowLens = [6, 7, 14, 19, 27, 9, 13, 15]
    rowNames = ['no.', 'pid', 'pdate', 'Title', 'Body', 'poster', '# of Votes', '# of Answers']

    lb = '|' + '|'.join(list(map(lambda s:'-'*s, rowLens))) + '|'
    
    # TODO use rowNames to generate header
    header = "|  no. |  pid  |     pdate    |       Title       |            Body           |  poster |  # of Votes |  # of Answers |"
    print(lb, header, sep='\n')

    for i, row in enumerate(results):
        print(lb, sep='\n')
        r = '|   {0}  |  {1} |  {2}  |  {3}|'.format(i+1,
                                                     row[0], 
                                                     row[1], 
                                                     row[2], 
                                                     row[3])
        

def genSearchResult(keywords):

    matchingPostsQuery = '\nUnion all\n'.join([getMatchingPostsQuery(i) for i in range(len(keywords))])
    mergedTableQuery = mergeMatchingTables(matchingPostsQuery)
    numVotesTableQuery = getnumVotesTable()
    numAnsTableQuery = getnumAnsTable()

    searchQuery = '''
                        SELECT 
                            pid, 
                            numMatches,
                            ifnull(numVotes, 0) as numVotes,
                            numAns
                        FROM
                            ({0}) left outer join ({1}) using (pid) 
                                left outer join ({2}) on pid = qid

                     '''.format(mergedTableQuery, 
                                numVotesTableQuery, 
                                numAnsTableQuery)

    fullSearchQuery = ''' 
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
                        ({0}) as search
                    WHERE
                        p.pid = search.pid
                    ORDER BY search.numMatches DESC;
                    '''.format(searchQuery)

    return fullSearchQuery
                    

def mergeMatchingTables(matchingPostsQuery):

    mergedTableQuery = '''
            SELECT 
                pid, 
                sum(numTitleBodyMatches) + sum(numTagMatches) as numMatches
            FROM
                ({})
            GROUP BY pid
            '''.format(matchingPostsQuery)

    return mergedTableQuery

def getMatchingPostsQuery(i):

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

    matchingPostsQuery = '''
                    SELECT 
                        pid,
                        ifnull(numTitleBodyMatches, 0) as numTitleBodyMatches,
                        ifnull(numTagMatches, 0) as numTagMatches
                    FROM 
                        (SELECT pid, numTitleBodyMatches, numTagMatches

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
                        )
                    '''.format(matchingTitleBodyTable, matchingTagTable)



    return matchingPostsQuery


def getnumVotesTable():

    numVotesTable = '''
                        SELECT
                            pid,
                            count(vno) as numVotes
                        FROM 
                            votes v
                        GROUP BY pid
                    '''
    return numVotesTable


def getnumAnsTable():

    numAnsTable = '''
                    SELECT
                        q.pid as qid,
                        ifnull(count(a.pid), 0) as numAns
                    FROM questions q LEFT OUTER JOIN answers a ON q.pid=qid
                    GROUP BY q.pid
                '''

    return numAnsTable


if __name__ == '__main__':
    conn = sqlite3.connect(sys.argv[1])
    curr = conn.cursor()
    searchPosts(conn, curr, 'rjej')


    

    
    
