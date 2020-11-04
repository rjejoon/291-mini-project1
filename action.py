import sqlite3
import sys
import os 

from datetime import date
from collections import OrderedDict
import page
import action
import bcolor


def postQ(conn, curr, poster):
    '''
    Prompt the user for a question post.
    pid is generated by the system.
        -- format: p'x', where x is an integer 0 <= x <= 999.

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Cursor
        poster -- uid of the signed in user (str)
    '''
    print('\n' + bcolor.pink('< Post a Question >'))
    infoList = getPInfo(curr)
    if infoList:
        infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

        curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?);', infoList)
        curr.execute('INSERT INTO questions VALUES (?, NULL);', [infoList[0]])
        conn.commit()

        print()
        print(bcolor.green('Posting Completed!'))


def searchPosts(curr, isPriv):
    '''
    Prompts the user for one or more search keywords and returns the posts with the keywords.
    The search looks for the matching keywords from the three fields: title, body, and tags.
    Keywords are case-insensitive.

    Input:
        curr -- sqlite3.Cursor
        isPriv -- bool
    Return:
        targetPost -- Sqlite3.Row,
        act -- str
    '''
    keywords = getKeywords()
    searchQuery = genSearchQuery(keywords)

    curr.execute(searchQuery, keywords)
    resultTable = curr.fetchall()

    if len(resultTable) > 0:
        no, act = action.displaySearchResult(resultTable, isPriv)
        targetPost = resultTable[no]
        return targetPost, act
    else:
        print(bcolor.errmsg('No posts found.'))


def postAns(conn, curr, poster, qid):
    '''
    Prompt the user to post an answer for the selected question.
    This function assumes the type of the selected post is question.
    
    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the current user (str)
        qid -- selected post (str)
    '''
    print()
    print(bcolor.pink('< Write an Answer >'))

    infoList = getPInfo(curr) 
    if infoList:
        infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

        curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?);', infoList)

        curr.execute('INSERT INTO answers VALUES (?, ?);', [infoList[0], qid])

        conn.commit()

        print()
        print(bcolor.green('Posting Completed!'))


def castVote(conn, curr, pid, uid):
    '''
    Prompt the user to cast a vote to the selected post.

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        pid -- selected post (str)
        uid -- uid of the current user (str)
    '''
    print('\n' + bcolor.pink('< Vote on the Post >'))

    prompt = 'Do you want to vote on this post? [y/n] '
    confirm = page.getValidInput(prompt, ['y', 'n'])

    if confirm == 'y':
        # checks if the user has already voted for the selected post
        curr.execute('SELECT * FROM votes WHERE pid = ? and uid = ?;', [pid, uid])

        if curr.fetchone():
            print(bcolor.errmsg("action failed: you've already voted for this post."))
        else:
            vdate = str(date.today())
            vno = getVno(curr)
            
            curr.execute('INSERT INTO votes VALUES (?, ?, ?, ?);', [pid, vno, vdate, uid])
            conn.commit()

            print()
            print(bcolor.green('Voting Completed!'))


def displaySearchResult(resultTable, isPriv):
    '''
    Display 5 posts at a time from the search result.
    Prompt the user to select a post and choose an action to take on.
    Return the index of the selected post and the type of the selected action.

    Inputs:
        resultTable -- list
        isPriv -- bool
    Returns:
        no -- int
        action -- str
    '''
    currRowIndex = 0
    numRows = len(resultTable)
    no = action = domain = None
    validEntries = [] 
    choseAction = False

    while not choseAction and currRowIndex < numRows:
        currRowIndex = printSearchResult(resultTable, currRowIndex)

        domain = '1-{}'.format(currRowIndex) if currRowIndex > 1 else '1'
        remainingRows = numRows - currRowIndex

        if remainingRows > 0:
            suffix = 's' if remainingRows > 1 else ''
            print("There are {} more row{} to display.\n".format(remainingRows, suffix))
            prompt = "Press enter to view more, or pick no. [{}] to select: ".format(domain)
            validEntries = ['y', '']
        else:
            prompt = "Search hit bottom. Pick no. [{}] to select: ".format(domain)
            validEntries = []

        if len(domain) == 1:
            # there is only one post to choose. 
            validEntries.append('1')
        else:
            end = domain.split('-')[1]
            validEntries += list(map(str, range(1, int(end)+1)))  

        opt = page.getValidInput(prompt, validEntries) 

        # post is selected
        if opt.isdigit():
            no = int(opt) - 1      # to match zero-index array
            isQues = isQuestion(resultTable[no])
            action = getAction(isQues, isPriv)
            choseAction = True

    return no, action


def isQuestion(row):
    '''
    Return True if the type of the post is a question. 
    If not, return False.
    '''
    return True if isinstance(row['numAns'], int) else False


def getKeywords():
    '''
    Prompt the user for search keywords and return them.

    return:
        keywords -- dict
    '''
    os.system('clear')
    print(bcolor.pink('< Search Posts >'))

    prompt = "Enter keywords to search, each separated by a comma: "
    keywords = input(prompt).lower().split(',')
    keywords = list(map(lambda kw : '%'+kw.strip()+'%', keywords))
    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}

    return keywords


def getAction(isQues, isPriv):
    '''
    Prompt the user for a post action and return it. 

    inputs:
        isQues -- bool
        isPriv -- bool
    Return:
        action -- str
    '''  
    actionDict = availableActions(isQues, isPriv)

    print("Choose an option to:\n")
    for cmd, action in actionDict.items():
        print("   {0}: {1}".format(bcolor.bold(cmd), action))
    print()

    action = page.getValidInput('Enter a command: ', actionDict.keys())
    
    return action 


def availableActions(isQues, isPriv):
    '''
    Return a range of available actions which the user can choose from, 
    depending on the type of the selected post and the type of the user.

    Inputs:
        isQues -- bool
        isPriv -- bool
    Return:
        actionDict -- Dict
    '''

    actionDict = OrderedDict()
    actionDict['vp'] = '{}ote {}ost'.format(bcolor.u_ualphas[21], bcolor.u_lalphas[15])

    quesActionDict = OrderedDict()
    quesActionDict['wa'] = '{}rite an {}nswer'.format(bcolor.u_ualphas[22], bcolor.u_lalphas[0])

    privActionDict = OrderedDict()
    privActionDict['gb'] = '{}ive a {}adge'.format(bcolor.u_ualphas[6], bcolor.u_lalphas[1])
    privActionDict['t'] = 'Add {}ags'.format(bcolor.u_lalphas[19])
    privActionDict['ep'] = '{}dit {}ost'.format(bcolor.u_ualphas[4], bcolor.u_lalphas[15])

    privAnsActionDict = OrderedDict()
    privAnsActionDict['ma'] = '{}ark as {}ccepted'.format(bcolor.u_ualphas[12], bcolor.u_lalphas[0])

    if isQues:
        actionDict.update(quesActionDict)
    else:
        privActionDict.update(privAnsActionDict)
    if isPriv:
        actionDict.update(privActionDict)

    actionDict['bm'] = '{}ack to {}enu'.format(bcolor.u_ualphas[1], bcolor.u_lalphas[12])

    return actionDict


def printSearchResult(result, currRowIndex):
    '''
    Print 5 search results starting from currRowIndex and return the index of 
    the last row displayed.
    
    Inputs:
        result -- list
        currRowIndex -- int
    Return:
        currRowIndex -- int
    '''
    rowNameLenDict = OrderedDict()
    rowNameLenDict['no.'] = 6
    rowNameLenDict['pid'] = 7 
    rowNameLenDict['pdate'] = 14
    rowNameLenDict['Title'] = 19
    rowNameLenDict['Body'] = 27
    rowNameLenDict['poster'] = 9
    rowNameLenDict['# of Votes'] = 13
    rowNameLenDict['# of Answers'] = 15

    header = '|'
    for rowName in rowNameLenDict.keys():
        header += rowName.center(rowNameLenDict[rowName], ' ') + '|'

    # lb: line breaker
    lb = '|' + '|'.join(list(map(lambda s:'-'*s, rowNameLenDict.values()))) + '|'
    
    print(lb, header, sep='\n')

    limit = 5
    d = rowNameLenDict
    i = currRowIndex
    n = len(result)
    for i in range(currRowIndex, currRowIndex + limit):

        if currRowIndex >= n:
            print(lb)
            return currRowIndex

        row = result[currRowIndex]
        print(lb, sep='\n')
        s = '|'
        s += str(i+1).center(d['no.'], ' ') + '|'
        s += row[0].center(d['pid'], ' ') + '|'
        s += row[1].center(d['pdate'], ' ') + '|'
        s += row[2][:d['Title']-2].rjust(d['Title'], ' ') + '|'
        s += row[3][:d['Body']-2].rjust(d['Body'], ' ') + '|'
        s += row[4].center(d['poster'], ' ') + '|'
        s += str(row[5]).center(d['# of Votes'], ' ') + '|'
        numAns = '--' if row[6] is None else str(row[6])
        s += numAns.center(d['# of Answers'], ' ') + '|'

        print(s, sep='\n')
        i += 1
        currRowIndex += 1

    print(lb)
     
    return currRowIndex


def genSearchQuery(keywords):
    '''
    Generate a sql query for selecting posts containing the given keywords.
    Columns: (pid, pdate, title, body, poster, numVotes, numAns, numMatches)

    input:
        keywords -- dict
    return:
        searchQuery -- str
    '''
    matchesQuery = '\nUNION ALL\n'.join([getMatchesQuery(i) for i in range(len(keywords))])
    mergedMatchesQuery = mergeMatches(matchesQuery)
    numVotesTableQuery = getnumVotesTable()
    numAnsTableQuery = getnumAnsTable()

    tempSearchQuery = '''
                        SELECT 
                            pid as pid2, 
                            numMatches,
                            ifnull(numVotes, 0) as numVotes,
                            numAns
                        FROM
                            ({0}) left outer join ({1}) using (pid) 
                                left outer join ({2}) on pid = qid

                     '''.format(mergedMatchesQuery, 
                                numVotesTableQuery, 
                                numAnsTableQuery)

    searchQuery = ''' 
                    SELECT
                        pid,
                        pdate,
                        title,
                        body,
                        poster,
                        numVotes,
                        numAns,
                        numMatches
                    FROM 
                        posts p,
                        ({0}) as matches 
                    WHERE
                        pid = pid2
                    ORDER BY 
                        matches.numMatches 
                    DESC;
                    '''.format(tempSearchQuery)

    return searchQuery
                    

def mergeMatches(matchesQuery):
    '''
    Merge generated matches for each keyword into one.
    '''
    mergedMatchesQuery = '''
            SELECT 
                pid, 
                sum(numTitleBodyMatches) + sum(numTagMatches) as numMatches
            FROM
                ({})
            GROUP BY pid
            '''.format(matchesQuery)

    return mergedMatchesQuery


def getMatchesQuery(i):
    '''
    Generate and return a sql query that select posts containing ith keyword in the title, tag, and body.

    input:
        i -- int
    return:
        matchesQuery -- str
    '''

    matchingTitleBodyTable = '''
                            SELECT 
                                pid,
                                (length(lower(title))-length(replace(lower(title), :kw{0}, ''))) / length(:kw{0})
                                  + (length(lower(body))-length(replace(lower(body), :kw{0}, ''))) / length(:kw{0}) 
                                    as numTitleBodyMatches
                            FROM posts p
                            WHERE 
                                p.title LIKE :kw{0}
                                OR p.body LIKE :kw{0}
                            '''.format(i) 

    matchingTagTable = '''
                        SELECT
                            pid,
                            count(tag) as numTagMatches 
                        FROM 
                            tags t
                        WHERE
                            tag like :kw{0}
                        GROUP BY 
                            pid
                    '''.format(i)

    matchesQuery = '''
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
                            ({0}) 
                        LEFT OUTER JOIN 
                            ({1}) 
                        USING (pid) 

                        UNION

                        SELECT 
                            pid, 
                            numTitleBodyMatches, 
                            numTagMatches
                        FROM
                            ({1})
                        LEFT OUTER JOIN
                            ({0})
                        USING (pid)
                        )
                    '''.format(matchingTitleBodyTable, matchingTagTable)

    return matchesQuery


def getnumVotesTable():
    '''
    Return a sql query that returns the number of votes casted in each post.
    '''
    return  '''
                SELECT
                    pid,
                    count(vno) as numVotes
                FROM 
                    votes v
                GROUP BY 
                    pid
            '''


def getnumAnsTable():
    '''
    Return a sql query that returns the number of answer in each post.
    '''

    return '''
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
            '''


def getPInfo(curr):
    '''
    Create a new post.
    Prompt the user for the post information and return it.
    A unique pid is generated and assigned to the new post.

    Input: 
        curr -- sqllite3.Connection
    Return:
        postInfo -- list 
    '''
    while True:
        pid = genPid(curr)
        pdate = str(date.today())
        print()
        title = input("Enter your title: ")
        body = input("Enter your body: ")
        
        postInfo = [pid, pdate, title, body]

        print('\nPlease double check your information: ')
        print('   Title: {}'.format(title))
        print('   Body: {}'.format(body))
        print()

        prompt = 'Is this correct? [y/n] '
        uin = page.getValidInput(prompt, ['y', 'n'])
        if uin == 'y':
            return postInfo
        else:
            prompt = 'Do you still want to make a post? [y/n] '
            if not page.continueAction(prompt):
                return False 


def genPid(curr):
    '''
    Return a new unique pid.

    Input: 
        curr -- sqllite3.Connection
    Return: 
        pid -- str
    '''
    pid = ''
    pid_n = getLargestPidNum(curr)

    if not pid_n:     # no posts in db
        return 'p001'

    pid = 'p{:03}'.format(pid_n)    # format: 'pxxx'
    while not isPidUnique(curr, pid):
        pid_n += 1
        pid = 'p{:03}'.format(pid_n)    

    return pid


def getLargestPidNum(curr):
    '''
    Return the largest pid from the database.
    If there is no post in the database, return None.

    input:
        curr: sqlite3.Cursor
    Return:
        int
    '''
    
    curr.execute('''
                    SELECT 
                        substr(pid, 2, 4) as n 
                    FROM 
                        posts 
                    WHERE 
                        pid LIKE 'p%' 
                    ORDER BY n DESC;
                ''')
    n = curr.fetchone()
    if n:
        return int(n[0])
    return None


def isPidUnique(curr, pid):
    '''
    Return True if a post with the specified pid is not in the database.

    Inputs:
        curr -- sqlite3.Cursor
        pid -- str
    Return:
        bool
    '''
    curr.execute("SELECT * FROM posts WHERE pid=?;", (pid, ))

    if not curr.fetchone():
        return True
    return False


def getVno(curr):
    '''
    Generate a unique vno for a vote and return it.
    
    Input: 
        curr -- sqllite3.Connection
    Return: 
        vno -- int
    '''
    curr.execute('SELECT * FROM votes;')
    if not curr.fetchone():
        vno = 1
    else:
        maxVno = curr.execute('SELECT MAX(vno) FROM votes;').fetchone()[0]
        vno = int(maxVno) + 1 if maxVno else 1
    return vno


if __name__ == '__main__':
    conn = sqlite3.connect(sys.argv[1])
    curr = conn.cursor()
    searchPosts(curr)
