import sqlite3
from datetime import date
from util import page
from util import bcolor

def markAnswer(conn, curr, aid):

    curr.execute("SELECT pid FROM answers where pid=?;", (aid, ))
    pid = curr.fetchone()[0]

    curr.execute("SELECT theaid fROM questions where pid=?;", (pid, ))
    # aa: accepted answer
    aaExists = False if not curr.fetchone() else True

    if aaExists:
        prompt = "Warning: Accepted answer already exists! Proceed to change? y/n:"
        valid = False
        while not valid:
            inp = input(prompt)
            if valid == 'y':
                valid = True
                changeAA(conn, curr, pid, aid)
            elif valid == 'n':
                valid = True
            else:
                print("error: invalid command")
    
    else:
        changeAA(conn, curr, pid, aid)

    print("Accepted answer successfully updated!")
            

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
        print('\n< Give Badge >')
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
                    print(bcolor.green('\nBadge awarded to the poster!'))
                    valid = True
            
            else:
                print(bcolor.errmsg('action failed: badge: "{}" is not available.'.format(bname)))

            if not valid:
                prompt = 'Do you still want to give a badge? [y/n] '
                valid = not page.continueAction(prompt)


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
        bname = input('\nEnter a badge name to give from the list above: ')
        if bname != '':
            validBadge = True
    return bname


def addTag(conn, curr, pid):
    '''
    Adds tags to the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        pid -- pid of the selected post (str)
    '''
    print('\n< Add Tags >')

    currentTags = findCurrentTag(curr, pid)
    if len(currentTags) == 0:
        print('\nThere is no tag on this post yet.')
    else:
        csuffix = genSuffix(currentTags)
        print("\nCurrent Tag{}: {}".format(csuffix, ', '.join(currentTags)))

    valid = False
    while not valid:

        # gets new tags
        newTags = getValidTag()
        numNewTags = len(newTags)

        # checks the duplicates
        duplicates, nonDuplicates = findMatchingTag(currentTags, newTags)
        numDup = len(duplicates)
        dsuffix = genSuffix(duplicates)
        
        tagsToAdd = True
        if numDup > 0:
            print('\nThe post already has the following tag{}: {}'.format(dsuffix, ', '.join(duplicates)))
            
            if numNewTags == numDup: # user enters duplicates only
                tagsToAdd = False
                valid = not checkValid('Do you want to add another tag to the post? (y/n) ')
            else:
                newTags = nonDuplicates
        
        nsuffix = genSuffix(newTags)
        if tagsToAdd:
            valid = checkValid('\nDo you want to add: "{}" ? (y/n) '.format('", "'.join(newTags)))

            if valid:
                insertTag(conn, curr, pid, newTags)
                print("Tag{} added!".format(nsuffix))
            else:
                valid = not checkValid('Do you still want to add tags to the post? (y/n) ')


def findCurrentTag(curr, pid):
    curr.execute("SELECT tag FROM tags WHERE pid = ?;", (pid,))
    currentTags = []
    for i in curr.fetchall():
        currentTags.append(i['tag']) 
    return currentTags


def findMatchingTag(currentTags, newTags):
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
    validTag = False
    while not validTag:
        newTags = input('\nEnter tags to add, each separated by a comma: ')
        newTags = [x.strip() for x in newTags.split(',') if x.strip()]
        if len(newTags) > 0:
            validTag = True
    return newTags


def insertTag(conn, curr, pid, newTags):
    for tag in newTags:
        curr.execute('INSERT INTO tags VALUES (?, ?)',(pid, tag))
        conn.commit()


def genSuffix(lst):
    return 's' if len(lst) > 1 else ''


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

    print("< Editing >")
    print("Press enter with nothing typed if you want to keep the content the same.")
    print()
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

    print("Change complete!")



def change(oldTitle, oldBody):

    print("You are currently editing:")
    print()
    print("   Title: {}".format(oldTitle))
    print()
    nTitle = input("Type a new title: ")
    if nTitle == '':
        nTitle = oldTitle

    print()
    print("You are currently editing:")
    print()
    print("   Body: {}".format(oldBody))
    print()
    nBody = input("Type a new Body: ") 
    if nBody == '':
        nBody = oldBody
        
    return nTitle, nBody

    
def isChangeValid(nTitle, nBody):

    print("Is this correct?")
    print("\n   Title: {}".format(nTitle))
    print("\n   Body: {}".format(nBody))

    while True:
        check = input("\nType 'y' if it is correct. Type 'n' if you want to start over: ")
        if check == 'y':
            return True
        elif check == 'n':
            return False
        else:
            print("error: invalid command")


def changeAA(conn:sqlite3.Connection, curr, pid, aid):

    curr.execute('''UPDATE 
                        questions
                    SET 
                        theaid = :aid
                    WHERE
                        pid = :pid;''', {'aid': aid, 
                                         'pid': pid})
    conn.commit()

    
def checkValid(message):
    '''
    Confirms the user if the change is correct with a given message. 
    Returns True if it is correct; False otherwise
    
    Input: message (str)
    '''
    while True:
        checkValid = input(message).lower()
        if checkValid == 'y':
            return True
        elif checkValid == 'n':
            return False
