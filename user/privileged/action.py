import sqlite3
from datetime import date

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
            

def giveBadge(conn, curr, poster):
    '''
    Gives a badge to the poster of the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the selected post (str)
    '''
    print('\n< Give Badge >')
    valid = False

    while not valid:
        bdate = str(date.today())
        bname = input('\nWhat is the badge name?: ')

        # checks if bname exists in the database
        curr.execute('SELECT * FROM badges WHERE bname = ?;',[bname])
        if curr.fetchone():

            valid = checkValid('Do you want to give badge: "{}" to the poster? y/n '.format(bname))

            if valid:
                # inserts a new badge
                curr.execute('INSERT INTO ubadges VALUES (?, ?, ?)',[poster, bdate, bname])
                conn.commit()
                print('You gave badge: "{}"!'.format(bname))

        else:
            print('Sorry! badge name: "{}" does not exist.'.format(bname))

        if not valid:
            valid = not checkValid('Do you still want to give a badge? y/n ')


def addTag(conn, curr, pid):
    '''
    Adds a tag to the selected post

    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        pid -- pid of the selected post (str)
    '''
    # TODO print tag names
    curr.execute("SELECT tag FROM tags WHERE pid = ?;", (pid, ))
    print("Current tags: ")
    for tag in curr.fetchall():
        print(tag)
    # TODO check for duplicates 

    print('\n< Add Tag >')
    valid = False
    while not valid:
        validTag = False

        while not validTag:
            # TODO can they add more than one tag at once?
            tag = input('\nEnter a tag name to this post: ').strip()
            if tag != '':
                validTag = True

        valid = checkValid('Do you want to add tag: "{}"? y/n '.format(tag))
        if valid:
            # inserts a new tag
            curr.execute('INSERT INTO tags VALUES (?, ?)',[pid, tag])
            conn.commit()
            print("You've added the tag!")

        else:
            valid = not checkValid('Do you still want to add a tag to the post? y/n ')

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
