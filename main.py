import sqlite3
import os 
import sys
import getpass
from datetime import date

def main():
    '''
    The main loop of the program.
    '''
    db = getDBFromArgv(sys.argv)

    conn, curr = initConnAndCurrFrom(db)

    # TODO use try...except...finally
    run = True
    while run:
        
        # first screen
        uInput = input("\nOptions: (si) sign in, (su) sign up, (q)uit: ").lower()

        if uInput == 'q':
            run = False
        elif uInput == 'si':
            uid = signIn(conn, curr)
        elif uInput == 'su':
            signUp(conn, curr)
        else:
            print("error: command not found.")


    conn.commit()
    conn.close()


def initConnAndCurrFrom(db):
    '''
    Make a connection and cursur from a specified database.

    Keyword arguments:
    db —- database file 
    '''
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep
    db_path = dir_path + f_name

    conn = sqlite3.connect(db_path)
    curr = conn.cursor()

    return conn, curr


def signIn(conn, curr):
    '''
    Prompts the user to enter their user ID and password. Checks if they exist in the database and Returns them.

    Inputs: conn, curr
    Returns: userID, password
    '''

    validInfo = False
    while not validInfo:

        uid = input('\nEnter your user ID: ')
        pwd = getpass.getpass('Enter your password: ')

        curr.execute('SELECT * FROM users WHERE uid = :userID AND pwd = :password;',
                    {'userID': uid, 'password': pwd})

        if curr.fetchone():
            validInfo = True
        else:
            print('error: invalid user ID or password. Please try again.')
        
    print('You have successfully signed in.')
    return uid


def signUp(conn, curr):
    '''
    Prompts the user for an account information and saves in the database.

    Keyword arguments:
    conn -- sqlite3.Connection
    curr -- sqlite3.Cursor
    '''

    valid = False
    while not valid:

        print()
        uid = getID(conn, curr)
        name = input("Enter your first and last name: ")
        city = input("Enter your city: ")
        pwd = getPassword()
        crdate = str(date.today())
            
        print()
        print("Please double check your information: ")
        print("   id: {}".format(uid))
        print("   name: {}".format(name))
        print("   city: {}".format(city))

        valid = checkValid()

    print("Sign up successful!")

    curr.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
            [uid, name, pwd, city, crdate])

    conn.commit()


def getID(conn, curr):
    '''
    Gets an appropriate user id and returns it.

    Keyword arguments:
    conn -- sqlite3.Connection
    curr -- sqlite3.Cursor
    '''
    valid = False
    while not valid: 
        uid = input("Enter your id: ")
        curr.execute("SELECT * FROM users WHERE uid = ?;", [uid])
        if curr.fetchone():
            print("error: user id already taken.")
        else:
            valid = True

    return uid


def getPassword():
    '''
    Gets an appropriate password and returns it.
    '''
    valid = False
    while not valid:
        pwd = getpass.getpass("Enter your password: ")
        pwd2 = getpass.getpass("Enter the password again: ")
        if pwd == pwd2:
            valid = True
        else:
            print("error: passwords do not match.")

    return pwd


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


def getDBFromArgv(argv):

    if len(argv) != 2:
        print("Usage: python3 main.py [file]") 
        sys.exit(1)
    
    return argv[1]


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


def postAns(conn, curr, poster, qid):
    '''
    Prompts the user to post an answer to the selected question
    
    Inputs: 
        conn -- sqlite3.Connection
        curr -- sqllite3.Connection
        poster -- uid of the current user (str)
        qid -- selected post (str)
    '''
    print('\n< Post Answer >')

    # checks if the selected post is a question
    curr.execute('SELECT * from questions WHERE pid = ?;',[qid])
    if curr.fetchone():
        infoList = getPInfo(curr) 
        if infoList:
            infoList.append(poster) # infoList = [pid, pdate, title, body, poster]

            curr.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)', infoList)

            curr.execute('INSERT INTO answers VALUES (?, ?)', [infoList[0], qid])

            conn.commit()

    else:
        print('Sorry! You are not able to answer to this post.')


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
        print('   pid: {}'.format(pid))
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
    curr.execute('SELECT * FROM posts;')
    if not curr.fetchone():
        pid = 'p001'
    else:
        pidNum = getLastPid(curr) + 1
        pid = 'p{:03}'.format(pidNum)
    return pid


def getLastPid(curr):
    '''
    Gets the last pid (int) inserted in the database.

    Input: curr -- sqllite3.Connection
    '''
    # only gets the numerical part of pid
    curr.execute('SELECT substr(pid, 2, 4) FROM posts')
    lastNum = int(curr.fetchall()[-1][0])
    return lastNum


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
                    maxVno = curr.execute('SELECT MAX(vno) FROM votes WHERE pid = ?;',[pid]).fetchone()[0]
                    vno = int(maxVno) + 1
                
                curr.execute('INSERT INTO votes VALUES (?, ?, ?, ?)', [pid, vno, vdate, uid])
                conn.commit()
            
            valid = True

        elif confirm == 'n':
            valid = True


if __name__ == "__main__":

    main()
