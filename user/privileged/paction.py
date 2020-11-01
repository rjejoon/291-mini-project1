import sqlite3
from datetime import date
from util import page
from util import bcolor

def markAnswer(conn, curr, aid):

    print(bcolor.pink('\n< Mark as Accepted Answer >'))

    curr.execute("SELECT * FROM answers where pid=?;", (aid, ))
    qid = curr.fetchone()['qid']

    prompt = 'Do you want to mark this post as an aceepted answer? [y/n] '
    uin = page.getValidInput(prompt, ['y','n'])

    if uin == 'y':

        curr.execute("SELECT * FROM questions where pid=? and theaid IS NOT NULL;", (qid, ))
        aaExists = True if curr.fetchone() else False # aa: accepted answer
            
        if aaExists:
            prompt = bcolor.warning("Warning: Accepted answer already exists. Proceed to change? [y/n] ")
            uin = page.getValidInput(prompt, ['y','n'])
            if uin == 'y':
                changeAA(conn, curr, qid, aid)
            else:
                print(bcolor.green('\nAccepted answer was not updated.'))
    
        else:
            changeAA(conn, curr, qid, aid)
            

def giveBadge(conn, curr, uid):
    '''
    Gives a badge to the poster of the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqlite3.Connection
        uid -- uid of the selected post (str)
    '''
    bdate = str(date.today())

    if not badgeAvailable(curr):
        print(bcolor.errmsg("action failed: badge is not available now."))

    elif badgeGivenTdy(curr, uid, bdate):
        print(bcolor.errmsg("action failed: this poster has already received a badge today."))

    else:
        print(bcolor.pink('\n< Give Badge >'))
        displayBadge(curr)
        valid = False
        while not valid:

            bname = getValidBadge()
            badgeRow = getBadgeRow(curr, bname)
        
            if badgeRow: # entered bname exists
                prompt = 'Do you want to give badge: "{}" to the poster? [y/n] '.format(badgeRow['bname'])
                uin = page.getValidInput(prompt, ['y','n'])

                if uin == 'y':
                    curr.execute('INSERT INTO ubadges VALUES (?, ?, ?)',(uid, bdate, badgeRow['bname']))
                    conn.commit()
                    print(bcolor.green('\nBadge Awarded to the poster!'))
                    valid = True
            
            else:
                print(bcolor.errmsg('action failed: badge: "{}" is not available.'.format(bname)))

            if not valid:
                prompt = 'Do you still want to give a badge? [y/n] '
                valid = not page.continueAction(prompt)



def addTag(conn, curr, pid):
    '''
    Adds tags to the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        pid -- pid of the selected post (str)
    '''
    print(bcolor.pink('\n< Add Tags >'))

    currentTags = getCurrentTag(curr, pid)
    displayCurrentTag(currentTags)
    
    valid = False
    while not valid:

        newTags = getValidTag()
        numNewTags = len(newTags)

        duplicates, nonDuplicates = getDuplicateTag(currentTags, newTags)
        numDup = len(duplicates)
        dsuffix = genSuffix(duplicates)
        
        tagsToAdd = True
        if numDup > 0:
            print(bcolor.errmsg('the post already has the following tag{}: {}'.format(dsuffix, ', '.join(duplicates))))
            
            if numNewTags == numDup: # user enters duplicates only
                tagsToAdd = False
                prompt = 'Do you want to add another tag to the post? [y/n] '
                valid = not page.continueAction(prompt)
            else:
                newTags = nonDuplicates
        
        nsuffix = genSuffix(newTags)
        if tagsToAdd:
            prompt = 'Do you want to add: "{}" ? [y/n] '.format('", "'.join(newTags))
            uin = page.getValidInput(prompt, ['y','n'])
            
            if uin == 'y':
                valid = True
                insertTag(conn, curr, pid, newTags)
                print(bcolor.green("\nTag{} Added!".format(nsuffix)))
            else:
                prompt = 'Do you still want to add tags to the post? [y/n] '
                valid = not page.continueAction(prompt)


def edit(conn, curr, pid):
    '''
    Edit the selected post.

    inputs:
        conn: sqlite3.Connection
        curr: sqlite3.Cursor
        pid: posts.pid
    '''
    curr.execute("SELECT title, body FROM posts WHERE pid=?", (pid, )) 
    currT, currB = curr.fetchone()

    print(bcolor.pink("\n< Editing >"))
    print("Press enter with nothing typed if you want to keep the content the same.")

    confirmed = False
    while not confirmed:
        nTitle, nBody = change(currT, currB)
        confirmed = isChangeValid(nTitle, nBody)

    curr.execute(''' 
                    UPDATE
                        posts
                    SET
                        title = ?,
                        body = ?
                    WHERE
                        pid = ?;''', (nTitle, nBody, pid))
    conn.commit()

    print(bcolor.green("\nPost Edited!"))


def change(oldTitle, oldBody):
    print()
    print(bcolor.cyan("You are currently editing:"))
    print("\n   Title: {}".format(oldTitle))
    print("\n   Body: {}".format(oldBody))
    
    print()
    nTitle = input("Type a new title: ")
    if nTitle == '':
        nTitle = oldTitle

    print()
    nBody = input("Type a new Body: ") 
    if nBody == '':
        nBody = oldBody
        
    return nTitle, nBody

    
def isChangeValid(nTitle, nBody):

    print("\nIs the following information correct?")
    print("\n   Title: {}".format(nTitle))
    print("\n   Body: {}".format(nBody))

    while True:
        check = input("\nType 'y' if it is correct. Type 'n' if you want to start over: ")
        if check == 'y':
            return True
        elif check == 'n':
            return False
        else:
            print(bcolor.errmsg("error: invalid command"))


def changeAA(conn:sqlite3.Connection, curr, pid, aid):

    curr.execute('''UPDATE 
                        questions
                    SET 
                        theaid = :aid
                    WHERE
                        pid = :pid;''', {'aid': aid, 
                                         'pid': pid})
    conn.commit()

    print(bcolor.green("\nAccepted Answer Updated!"))


def badgeGivenTdy(curr, uid, bdate):
    '''
    Checks if a badge is already given to the poster today

    Inputs:
        curr -- sqlite3.Connection
        uid --- str
        bdate -- date
    '''
    curr.execute('SELECT * FROM ubadges WHERE uid = ? and bdate = ?;',(uid, bdate))
    return True if curr.fetchone() else False


def badgeAvailable(curr):
    '''
    Checks if a badge is available in the database

    Input: curr -- sqlite3.Connection
    '''
    curr.execute('SELECT * FROM badges;')
    return True if curr.fetchone() else False


def getBadgeRow(curr, bname):
    '''
    Gets a row of the badge table that includes the same bname entered

    Inputs:
        curr -- sqlite3.Connection
        bname -- str
    Returns: 
        curr.fetchone() -- sqlite3.Row
    '''
    curr.execute('SELECT * FROM badges WHERE bname = ? COLLATE NOCASE;',(bname,))
    return curr.fetchone()


def displayBadge(curr):
    '''
    Displays the badges available in the database

    Input: curr -- sqlite3.Connection
    '''
    print('\nAvailable badges:')
    curr.execute("SELECT type, bname FROM badges ORDER BY type;")

    frame = '+'+'-'*10+'+'+'-'*25+'+'
    print(frame)
    print('|{:^10}|{:^25}|'.format('type','badge name'))
    print(frame)
    for aBadge in curr.fetchall():
        print('|{:^10}|{:^25}|'.format(aBadge['type'],aBadge['bname']))
        print(frame)


def getValidBadge():
    '''
    Prompts the user for a valid badge name
    '''
    validBadge = False
    while not validBadge:
        bname = input('\nEnter a badge name to give from the list above: ').strip()
        if bname != '':
            validBadge = True
    return bname


def getCurrentTag(curr, pid):
    '''
    Gets the current tags that the post has

    Inputs: 
        curr -- sqllite3.Connection
        pid -- pid of the selected post (str)
    '''
    curr.execute("SELECT tag FROM tags WHERE pid = ?;", (pid,))
    currentTags = []
    for i in curr.fetchall():
        currentTags.append(i['tag']) 
    return currentTags


def displayCurrentTag(currentTags):
    '''
    Displays the current tags

    Input: currentTags -- list
    '''
    if len(currentTags) == 0:
        print('There is no tag on this post yet.')
    else:
        csuffix = genSuffix(currentTags)
        print("Current Tag{}: {}".format(csuffix, ', '.join(currentTags)))


def getDuplicateTag(currentTags, newTags):
    '''
    Gets the duplicated tags in currentTags and newTags

    Inputs:
        currentTags -- list
        newTags -- list of tags entered
    '''
    duplicates = []
    nonDuplicates = []
    lst = [x.lower() for x in currentTags]
    for i in newTags:
        if i.lower() in lst:
            duplicates.append(i)
        else:
            nonDuplicates.append(i)
    return duplicates, nonDuplicates


def getValidTag():
    '''
    Gets the valid tags and Returns a list
    '''
    validTag = False
    while not validTag:
        newTags = input('\nEnter tags to add, each separated by a comma: ')
        newTags = [x.strip() for x in newTags.split(',') if x.strip()]
        if len(newTags) > 0:
            validTag = True
    return newTags


def insertTag(conn, curr, pid, newTags):
    '''
    Inserts the valid tags in newTags

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqlite3.Connection
        pid -- str
        newTags -- list
    '''
    for tag in newTags:
        curr.execute('INSERT INTO tags VALUES (?, ?)',(pid, tag))
        conn.commit()


def genSuffix(lst):
    '''
    Gets a suffix depending on the subject (lst)
    
    Input: lst -- list
    '''
    return 's' if len(lst) > 1 else ''
