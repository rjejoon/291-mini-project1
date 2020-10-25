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

    displaySearchResult(resultTable, limit=5)

    #TODO integrate moe's input function for option
    remainingRows = len(resultTable) - 5
    if remainingRows > 0:
        if remainingRows == 1:
            prompt = "There are {} more row to display. Enter 'y' to view more: ".format(remainingRows)
        else:
            prompt = "There are {} more rows to display. Enter 'y' to view more: ".format(remainingRows)
        viewMore = input(prompt)
        if viewMore == 'y':
            print()
            displaySearchResult(resultTable, limit=len(resultTable))
        # TODO add input checking 

    return resultTable


def displaySearchResult(results, limit=5):

    rowNameLenDict = {'no.' : 6,
                      'pid' : 7,
                      'pdate': 14,
                      'Title': 19,
                      'Body': 27,
                      'poster': 9,
                      '# of Votes': 13,
                      '# of Answers': 15}

    header = '|'
    for rowName in rowNameLenDict.keys():
        header += rowName.center(rowNameLenDict[rowName], ' ') + '|'

    lb = '|' + '|'.join(list(map(lambda s:'-'*s, rowNameLenDict.values()))) + '|'
    
    print(lb, header, sep='\n')

    for i, row in enumerate(results):
        if i >= limit:
            break
        print(lb, sep='\n')
        r = '|'
        d = rowNameLenDict
        r += str(i+1).center(d['no.'], ' ') + '|'
        r += row[0].center(d['pid'], ' ') + '|'
        r += row[1].center(d['pdate'], ' ') + '|'
        r += row[2][:d['Title']-2].rjust(d['Title'], ' ') + '|'
        r += row[3][:d['Body']-2].rjust(d['Body'], ' ') + '|'
        r += row[4].center(d['poster'], ' ') + '|'
        r += str(row[5]).center(d['# of Votes'], ' ') + '|'
        r += str(row[6]).center(d['# of Answers'], ' ') + '|'

        print(r, sep='\n')

    print(lb)

        

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


    

    
    
