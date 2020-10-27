import sqlite3
from datetime import date


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
