import sqlite3
import sys
import os 
from datetime import date


def postQ(conn, curr, poster):
    '''
    Prompts the user to post a question

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the current user (str)
    '''
    print('\n< Post Question >')
    infoList = getPInfo(curr)
    if infoList:
        infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

        curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)', infoList)

        curr.execute('INSERT INTO questions VALUES (?, NULL)', [infoList[0]])

        conn.commit()

        print('Posting Completed!')


def searchPosts(curr):

    # TODO interface
    prompt = "Enter keywords to search, each separated by a comma: "
    # TODO add error checking

    keywords = input(prompt).lower().replace("'", "''").split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))
    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}
        
    fullSearchQuery = genSearchResult(keywords)

    # write full query for checking
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'test'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    testf_path = dir_path + os.sep + 'generatedSearchQuery.sql' 

    with open(testf_path, 'w') as f:
        f.write(fullSearchQuery)

    curr.execute(fullSearchQuery, keywords)
    resultTable = curr.fetchall()

    return resultTable


def postAns(conn, curr, poster, qid):
    '''
    Prompts the user to post an answer to the selected question
    Assume the post type is question.
    
    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the current user (str)
        qid -- selected post (str)
    '''
    print('\n< Post Answer >')

    infoList = getPInfo(curr) 
    if infoList:
        infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

        curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)', infoList)

        curr.execute('INSERT INTO answers VALUES (?, ?)', [infoList[0], qid])

        conn.commit()

        print('Posting Complete!')


def castVote(conn, curr, pid, uid):
    '''
    Prompts the user to cast a vote to the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        pid -- selected post (str)
        uid -- uid of the current user (str)
    '''
    print('\n< Cast Vote >')
    valid = False
    while not valid:
        confirm = input('Confirmation: Do you want to vote for this post? y/n ').lower()

        if confirm == 'y':
            # checks if the user has already voted for the selected post
            curr.execute('SELECT * FROM votes WHERE pid = ? and uid = ?',[pid, uid])
            if curr.fetchone():
                print("You've already voted for this post.")

            else:
                curr.execute('SELECT * FROM votes;')
                vdate = str(date.today())

                if not curr.fetchone():
                    vno = 1
                else:
                    # gets the max vno in the database
                    maxVno = curr.execute('SELECT MAX(vno) FROM votes;').fetchone()[0]
                    vno = int(maxVno) + 1 if maxVno else 1
                
                curr.execute('INSERT INTO votes VALUES (?, ?, ?, ?)', [pid, vno, vdate, uid])
                conn.commit()

                print('Voting Completed!')
            
            valid = True

        elif confirm == 'n':
            valid = True


def displaySearchResult(resultTable, isPriv, limit):

    display(resultTable, limit)

    no = action = None
    remainingRows = len(resultTable) - limit
    if remainingRows > 0:
        suffix = 's' if remainingRows > 1 else ''
        n = limit if len(resultTable) > limit else len(resultTable)
        domain = "1-{}".format(n) if n > 1 else '1'
        prompt = "There are {} more row{} to display.\nPress enter to view more, or pick no. ({}) to select: ".format(remainingRows, suffix, domain)

        valid = False
        while not valid:
            print()
            i = input(prompt)
            if i.isdigit():
                valid = True
                i = int(i)
                no = i - 1      # to match zero-index array
                postType = getPostType(resultTable[no])
                action = getAction(postType, isPriv)
            elif i in ['y', '']:
                #TODO should display 5 more at a time instad of displaying full result
                valid = True
                print()
                display(resultTable, limit=len(resultTable))
                # TODO get rid of getActionFromFullSearch
                no, action = getActionFromFullSearch(len(resultTable), resultTable, isPriv)
            else:
                print("error: invalid command")

    # TODO if len(remainingRows) < 0: no, action are None

    return no, action


def getActionFromFullSearch(n, resultTable, isPriv):

    # TODO 
    be_verb = 'are' if n > 1 else 'is'
    suffix = 's' if n > 1 else ''
    print("There {} {} matching post{}.".format(be_verb, n, suffix), sep= ' ')

    domain = "1-{}".format(n) if n > 1 else '1'
    prompt = "Pick post no. ({}) to select: ".format(domain)
    no = None
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
    action = getAction(postType, isPriv)

    return no, action


def getPostType(resultRow):

    # resultRow = (pid, pdate, title, body, poster, numVotes, numAns, numMatches)

    # TODO could use row factory to use name of the col instead index.
    return 'q' if isinstance(resultRow[6], int) else 'a'


def getAction(postType, isPriv):

    '''
    actions: 
        1: Vote
        2: Post answer
    '''
    options = {'vp': "Vote on the post"}
    quesOption = {'wa': "Write an answer"}

    privOptions = {
                    'gb': "Give a badge",
                    't': "Add a tag",
                    'ep': "Edit the post"
                    }

    privAnsOption = {'ma': "Mark as accepted"}

    if postType == 'q':
        options.update(quesOption)
    elif postType == 'a':
        privOptions.update(privAnsOption)
    if isPriv:
        options.update(privOptions)
        
    print("Choose an option to:\n")
    for cmd, option in options.items():
        print("   {0}. {1}".format(cmd, option))
    print()

    valid = False
    while not valid:
        cmd = input("Enter a command... ")
        if cmd in options.keys():
            valid = True
        else:
            print("error: invalid command")
    
    return cmd


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


def getPInfo(curr):
    '''
    Gets an info for making a post and Returns a list of pid, pdate, title, body

    Input: curr -- sqllite3.Connection
    '''
    valid = False
    while not valid:
        pid = getPid(curr)
        pdate = str(date.today())
        title = input("Enter your title: ")
        body = input("Enter your body: ")

        print('\nPlease double check your information: ')
        print('   title: {}'.format(title))
        print('   body: {}'.format(body))

        if checkValid():
            valid = True
            return [pid, pdate, title, body]
        else:
            if not continuePost():
                return False 


def getPid(curr):
    '''
    Generates a new pid and Returns it.

    Input: curr -- sqllite3.Connection
    '''
    pid = None
    curr.execute('SELECT * FROM posts;')
    if not curr.fetchone():     # no posts in db
        pid = 'p001'
    else:
        isUnique = False
        i = 2
        while not isUnique:
            n = i
            pid = 'p{:03}'.format(n)
            curr.execute("SELECT * FROM posts WHERE pid=?;"(pid, ))
            if len(curr.fetchone()) == 0:
                isUnique = True
            i += 1
    return pid


def continuePost():
    '''
    Confirms the users if they still want to make a post.
    '''
    while True:
        checkValid = input('Do you still want to make a post? y/n ').lower()
        if checkValid == 'y':
            print()
            return True
        elif checkValid == 'n':
            return False

def checkValid():
    '''
    Prompts the user to double check their account information and returns the result.
    '''
    while True:
        checkValid = input("\nIs this correct? y/n ").lower()
        if checkValid == 'y':
            return True
        elif checkValid == 'n':
            return False
