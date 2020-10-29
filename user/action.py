import sqlite3
import sys
import os 

from datetime import date
from collections import OrderedDict
from util import page
from util import bcolor


def postQ(conn, curr, poster):
    '''
    Prompts the user to post a question

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the current user (str)
    '''
    print('\n' + bcolor.pink('< Post Question >'))
    infoList = getPInfo(curr)
    if infoList:
        infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

        curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?);', infoList)

        curr.execute('INSERT INTO questions VALUES (?, NULL);', [infoList[0]])

        conn.commit()

        print('Posting Complete!')


def searchPosts(curr):

    # TODO interface

    keywords = getKeywords(curr)
    fullSearchQuery = genSearchResult(keywords)
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
    print('\n' + bcolor.pink('< Cast Vote >'))
    valid = False
    while not valid:
        confirm = input('Confirmation: Do you want to vote for this post? y/n ').lower()

        if confirm == 'y':
            # checks if the user has already voted for the selected post
            curr.execute('SELECT * FROM votes WHERE pid = ? and uid = ?',[pid, uid])
            if curr.fetchone():
                print(bcolor.errmsg("error: you've already voted for this post."))
            else:
                curr.execute('SELECT * FROM votes;')
                vdate = str(date.today())

                #TODO make a function
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


def displaySearchResult(resultTable, isPriv):

    currRowIndex = 0
    numRows = len(resultTable)
    no = action = domain = validEntries = None
    while currRowIndex < numRows: 
        currRowIndex = display(resultTable, currRowIndex)
        remainingRows = numRows - currRowIndex

        if remainingRows > 0:
            suffix = 's' if remainingRows > 1 else ''
            domain = "1-{}".format(currRowIndex) if currRowIndex > 1 else '1'
            prompt = "There are {} more row{} to display.\nPress enter to view more, or pick no. ({}) to select: ".format(remainingRows, suffix, domain)
            validEntries = ['y', '']

        else:
            domain = "1-{}".format(currRowIndex) if currRowIndex > 1 else '1'
            prompt = "Search hit bottom. Pick no. ({}) to select: ".format(domain)
            validEntries = []

        if len(domain) == 1:
            validEntries += [1]
        else:
            end = domain.split('-')[1]
            validEntries += list(map(str, range(1, int(end)+1)))  

        opt = page.getValidInput(prompt, validEntries) 

        if opt.isdigit():
            no = int(opt) - 1      # to match zero-index array
            postType = getPostType(resultTable[no])
            action = getAction(postType, isPriv)

    return no, action


def getPostType(resultRow):

    # resultRow = (pid, pdate, title, body, poster, numVotes, numAns, numMatches)

    # TODO could use row factory to use name of the col instead index.
    return 'q' if isinstance(resultRow[6], int) else 'a'


def getKeywords(curr):

    os.system('clear')
    print(bcolor.pink('< Search Posts >'))
    prompt = "Enter keywords to search, each separated by a comma: "
    keywords = input(prompt).lower().replace("'", "''").split(',')
    keywords = list(map(lambda kw : kw.strip(), keywords))
    keywords = {'kw{}'.format(i) : kw for i, kw in enumerate(keywords)}

    return keywords


def getAction(postType, isPriv):

    options = OrderedDict()
    options['vp'] = '{}ote {}ost'.format(bcolor.u_ualphas[21], bcolor.u_lalphas[15])

    quesOption = OrderedDict()
    quesOption['wa'] = '{}rite an {}nswer'.format(bcolor.u_ualphas[22], bcolor.u_lalphas[0])

    privOptions = OrderedDict()
    privOptions['gb'] = '{}ive a {}adge'.format(bcolor.u_ualphas[6], bcolor.u_lalphas[1])
    privOptions['t'] = '{}dd a {}ag'.format(bcolor.u_ualphas[0], bcolor.u_lalphas[19])
    privOptions['ep'] = '{}dit {}ost'.format(bcolor.u_ualphas[4], bcolor.u_lalphas[15])

    privAnsOption = OrderedDict()
    privAnsOption['ma'] = '{}ark as {}ccepted'.format(bcolor.u_ualphas[12], bcolor.u_lalphas[0])


    if postType == 'q':
        options.update(quesOption)
    elif postType == 'a':
        privOptions.update(privAnsOption)
    if isPriv:
        options.update(privOptions)
        
    print("Choose an option to:\n")
    for cmd, option in options.items():
        print("   {0}: {1}".format(bcolor.bold(cmd), option))
    print()

    cmd = page.getValidInput('Enter a command: ', options.keys())
    
    return cmd


def display(result, currRowIndex):

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

    lim = 5
    i = currRowIndex
    n = len(result)
    for i in range(currRowIndex, currRowIndex+5):

        if currRowIndex >= n:
            print(lb)
            return currRowIndex

        row = result[currRowIndex]
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
        i += 1
        currRowIndex += 1
    print(lb)
        
    return currRowIndex

def genSearchResult(keywords):

    matchingPostsQuery = '\nUNION ALL\n'.join([getMatchingPostsQuery(i) for i in range(len(keywords))])
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

    # write full query for debuging 
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'test'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    testf_path = dir_path + os.sep + 'searchQuery.sql' 

    with open(testf_path, 'w') as f:
        f.write(fullSearchQuery)

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
                        FROM 
                            tags t
                        WHERE
                            tag like '%'||:kw{0}||'%'
                        GROUP BY 
                            pid
                    '''.format(i)

    matchingPostsQuery = '''
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



    return matchingPostsQuery


def getnumVotesTable():

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
    Gets an info for making a post and Returns a list of pid, pdate, title, body

    Input: curr -- sqllite3.Connection
    '''
    valid = False
    while not valid:
        pid = genPid(curr)
        pdate = str(date.today())
        title = input("Enter your title: ")
        body = input("Enter your body: ")

        print('\nPlease double check your information: ')
        print('   Title: {}'.format(title))
        print('   Body: {}'.format(body))

        if checkValid():
            valid = True
            return [pid, pdate, title, body]
        else:
            if not continuePost():
                return False 


def genPid(curr):
    '''
    Generate and return a new pid.

    Input: curr -- sqllite3.Connection
    Return: pid -- str
    '''
    pid = ''
    pid_n = getLargestPidNum(curr)

    if not pid_n:     # no posts in db
        return 'p001'

    isUnique = False
    while not isUnique:
        pid = 'p{:03}'.format(pid_n)    # format: 'pxxx'
        isUnique = isPidUnique(curr, pid)
        pid_n += 1

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


def getLargestPidNum(curr):
    
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

    curr.execute("SELECT * FROM posts WHERE pid=?;", (pid, ))

    if not curr.fetchone():
        return True
    return False





if __name__ == '__main__':
    conn = sqlite3.connect(sys.argv[1])
    curr = conn.cursor()
    searchPosts(curr)
