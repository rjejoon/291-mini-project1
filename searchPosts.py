import sqlite3
import sys
import os 


def searchPosts(curr):

    prompt = "Enter keywords to search, each separated by a comma: "
    # TODO add error checking

    keywords = input(prompt).lower().replace("'", "''").split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))
    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}
        
    fullSearchQuery = genSearchResult(keywords)

    # write full query for checking
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'test'
    testf_path = 'generatedSearchQuery.sql'
    if not os.path.isdir(dir_path):
        testf_path = dir_path + testf_path 

    with open(testf_path, 'w') as f:
        f.write(fullSearchQuery)

    curr.execute(fullSearchQuery, keywords)
    resultTable = curr.fetchall()

    return resultTable


def displaySearchResult(resultTable, limit):

    display(resultTable, limit)

    remainingRows = len(resultTable) - limit
    if remainingRows > 0:
        suffix = 's' if remainingRows > 1 else ''
        n = limit if len(resultTable) > limit else len(resultTable)
        domain = "1-{}".format(n) if n > 1 else '1'
        prompt = "There are {} more row{} to display.\nPress enter to view more, or pick no. ({}) to select: ".format(remainingRows, suffix, domain)

        no = action = None
        valid = False
        while not valid:
            print()
            i = input(prompt)
            if i.isdigit():
                valid = True
                i = int(i)
                no = i - 1      # to match zero-index array
                postType = getPostType(resultTable[no])
                action = getAction(no, postType)
            elif i in ['y', '']:
                #TODO should display 5 more at a time instad of displaying full result
                valid = True
                print()
                display(resultTable, limit=len(resultTable))
                no, action = getActionFromFullSearch(len(resultTable), postType)
            else:
                print("error: invalid command")

    return no, action


def getActionFromFullSearch(n, postType):

    be_verb = 'are' if n > 1 else 'is'
    suffix = 's' if n > 1 else ''
    print("There {} {} matching post{}.".format(be_verb, n, suffix), sep= ' ')

    domain = "1-{}".format(n) if n > 1 else '1'
    prompt = "Pick post no. ({}) to select: ".format(domain)
    valid = False
    while not valid:
        no = input(prompt)
        if no.isdigit(): 
            no = int(no)
            if 1 <= no <= n:
                valid = True
                no -= 1     # to match zero-index array
        else:
            print("error: out of range")

    postType = getPostType(resultTable[no])
    action = getAction(no, postType)

    return no, action


def getPostType(resultRow):

    # resultRow = (pid, pdate, title, body, poster, numVotes, numAns, numMatches)

    # TODO could use row factory to use name of the col instead index.
    return 'a' if not resultRow[6] else 'q'


def getAction(no, postType):

    '''
    actions: 
        1: Vote
        2: Post answer
    '''
    ansOpt = "   2. Write an answer\n" if postType=='q' else '' 

    valid = False
    while not valid:
        print()
        print("Choose an option to:")
        print("   1. Vote on the post")
        print(ansOpt)
        action = input()
        validRange = [1, 2] if postType=='q' else [1]
        if action.isdigit() and int(action) in validRange:
            action = int(action)
            valid = True
        else:
            print("error: invalid command")
    
    return action



def display(results, limit=5):

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

    # lb: line breaker
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
    searchPosts(curr)


    

    
    
