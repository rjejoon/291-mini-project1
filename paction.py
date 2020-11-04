import sqlite3

from datetime import date
import page
import bcolor

def markAnswer(conn, curr, aid):
    '''
    Mark the selected answer post as accepted and update it into the database.
    Prompts the user whether to overwrite if an accepted answer already exists.

    inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        aid -- pid of answer post (str)
    '''

    print(bcolor.pink('\n< Mark as Accepted Answer >'))

    curr.execute("SELECT * FROM answers where pid=?;", (aid, ))
    qid = curr.fetchone()['qid']

    prompt = 'Do you want to mark this post as an accepted answer? [y/n] '
    uin = page.getValidInput(prompt, ['y','n'])

    if uin == 'y':

        curr.execute("SELECT * FROM questions where pid=? and theaid IS NOT NULL;", (qid, ))
        aaExists = True if curr.fetchone() else False       # aa: accepted answer
            
        if aaExists:
            prompt = bcolor.warning("Warning: Accepted answer already exists. Proceed to change? [y/n] ")
            uin = page.getValidInput(prompt, ['y','n'])
            if uin == 'y':
                changeAA(conn, curr, qid, aid)
                conn.commit()
            else:
                print('\nMarking answer is cancelled.')
    
        else:
            changeAA(conn, curr, qid, aid)
            conn.commit()
            

def giveBadge(conn, curr, uid):
    '''
    Gives a badge to the poster of the selected post.

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        uid -- poster of the selected post (str)
    '''
    bdate = str(date.today())

    if not badgeAvailable(curr):
        print(bcolor.errmsg("action failed: badge is not available now."))

    elif isBadgeGivenTdy(curr, uid, bdate):
        print(bcolor.errmsg("action failed: this poster has already received a badge today."))

    else:
        print(bcolor.pink('\n< Give a Badge >'))
        displayAvailBadges(curr)
        valid = False
        while not valid:

            bname = getBadge()
            badgeRow = getBadgeRow(curr, bname)
        
            if badgeRow:    # badge already exists
                prompt = 'Do you want to give badge: "{}" to the poster? [y/n] '.format(badgeRow['bname'])
                uin = page.getValidInput(prompt, ['y','n'])

                if uin == 'y':
                    curr.execute('INSERT INTO ubadges VALUES (?, ?, ?);',(uid, bdate, badgeRow['bname']))
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
    Add tags to the selected post.

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Cursor
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
        numDups = len(duplicates)
        dsuffix = genSuffix(duplicates)
        
        tagsToAdd = True
        if numDups > 0:
            print(bcolor.errmsg('error: post already has the following tag{}: {}'.format(dsuffix, ', '.join(duplicates))))
            
            if numNewTags == numDups: # user enters duplicates only
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


def editPost(conn, curr, pid):
    '''
    Edit the title and body of the selected post.

    inputs:
        conn: sqlite3.Connection
        curr: sqlite3.Cursor
        pid: pid
    '''
    curr.execute("SELECT title, body FROM posts WHERE pid=?;", (pid, )) 
    currT, currB = curr.fetchone()

    print(bcolor.pink("\n< Edit Post >"))

    confirmed = False
    while not confirmed:
        nTitle, nBody = changeTitleAndBody(currT, currB)
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


def changeTitleAndBody(oldTitle, oldBody):
    '''
    Prompt the user for a new title and new body.

    Inputs:
        oldTitle -- str
        oldBody -- str
    Return:
        nTitle -- str
        nBody -- str
    '''
    print()
    print(bcolor.cyan("You are currently editing:"))
    print("\n   Title: {}".format(oldTitle))
    print("\n   Body: {}".format(oldBody))
    
    print()
    print("Press enter with nothing typed if you want to keep the content the same.")
    print()
    nTitle = input("Enter a new title: ")
    if nTitle == '':
        nTitle = oldTitle

    print()
    nBody = input("Enter a new body: ") 
    if nBody == '':
        nBody = oldBody
        
    return nTitle, nBody

    
def isChangeValid(nTitle, nBody):
    '''
    Prompt the user to double check the new title and body, and return True if they are valid.

    Inputs:
        nTitle -- str
        nBody -- str
    Return: 
        bool
    '''

    print("\nIs the following information correct?")
    print("\n   Title: {}".format(nTitle))
    print("\n   Body: {}".format(nBody))

    prompt = "\nType 'y' if it is correct. Type 'n' if you want to start over: "
    check = page.getValidInput(prompt, ['y', 'n'])
    if check == 'n':
        return False 
    return True 


def changeAA(conn, curr, pid, aid):
    '''
    Update the selected answer post as accepted to the database. 

    inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        pid -- str
        aid -- str
    '''
    curr.execute('''UPDATE 
                        questions
                    SET 
                        theaid = :aid
                    WHERE
                        pid = :pid;''', {'aid': aid, 
                                         'pid': pid})
    conn.commit()

    print(bcolor.green("\nAccepted Answer Updated!"))


def isBadgeGivenTdy(curr, uid, bdate):
    '''
    Return True if a badge is already given to the poster today.

    Inputs:
        curr -- sqlite3.Connection
        uid --- str
        bdate -- date
    '''
    curr.execute("SELECT * FROM ubadges WHERE uid = ? and bdate = ?;",(uid, bdate))
    return True if curr.fetchone() else False


def badgeAvailable(curr):
    '''
    Return True if there is at least one badge in the database.

    Input: curr -- sqlite3.Connection
    '''
    curr.execute("SELECT * FROM badges;")
    return True if curr.fetchone() else False


def getBadgeRow(curr, bname):
    '''
    Return a row of the badge table that includes the same bname entered.

    Inputs:
        curr -- sqlite3.Connection
        bname -- str
    Returns: 
        sqlite3.Row
    '''
    curr.execute("SELECT * FROM badges WHERE bname = ? COLLATE NOCASE;",(bname,))
    return curr.fetchone()


def displayAvailBadges(curr):
    '''
    Displays the badges available in the database.

    Input: curr -- sqlite3.Cursor
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


def getBadge():
    '''
    Prompt the user for a badge name.

    Return:
        bname -- str
    '''
    validBadge = False
    while not validBadge:
        bname = input('\nEnter a badge name to give from the list above: ').strip()
        if bname != '':
            validBadge = True
        else:
            print(bcolor.errmsg('error: badge name cannot be empty.'))
    return bname


def getCurrentTag(curr, pid):
    '''
    Return currently attached tags to the selected post.

    Inputs: 
        curr -- sqllite3.Cursor
        pid -- pid of the selected post (str)
    Return:
        list
    '''
    curr.execute("SELECT tag FROM tags WHERE pid = ?;", (pid,))

    return [r['tag'] for r in curr.fetchall()]


def displayCurrentTag(currentTags):
    '''
    Display the attached tags. 

    Input: currentTags -- list
    '''
    if len(currentTags) == 0:
        print('There is no tag attached to this post yet.')
    else:
        suffix = genSuffix(currentTags)
        print("Current Tag{}: {}".format(suffix, ', '.join(currentTags)))


def getDuplicateTag(currentTags, newTags):
    '''
    Classify the currently attached tags and the new tags entered by the user.
    into duplicated and non-duplicate tags and return them.

    Inputs:
        currentTags -- list
        newTags -- list of tags entered
    Returns:
        duplicates -- list
        nonDuplicates -- list
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
    Prompt the user for tags and return them.

    Return:
        newTags -- list
    '''
    validTag = False
    while not validTag:
        tags = input('\nEnter tags to add, each separated by a comma: ')
        newTags = []
        for x in tags.split(','):
            x = x.strip()
            if x and x not in newTags:
                newTags.append(x)
        if len(newTags) > 0:
            validTag = True
        else:
            print(bcolor.errmsg('error: tag name cannot be empty'))
    return newTags


def insertTag(conn, curr, pid, newTags):
    '''
    Insert the new tags into the database. 

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        pid -- str
        newTags -- list
    '''
    for tag in newTags:
        curr.execute("INSERT INTO tags VALUES (?, ?);", (pid, tag))
    conn.commit()


def genSuffix(l):
    '''
    Return an appropriate suffix depending on the number of elements in the list.
    '''
    return 's' if len(l) > 1 else ''



