import sys
import getpass
from user import action


def mainMenu(conn, curr, uid):
    '''
    Displays the menu and Prompts the user to choose from some actions.

    Inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        uid -- uid of the current user
    '''
    valid = False
    while not valid:
        print('\n* * WELCOME {}! * *'.format(uid)) # TODO use nane of the user instead of uid
        print('\n[ M E N U ]')
        print('\n1. Post a question')
        print('2. Search for posts')
        print('   -> Vote on a post')
        print('   -> Post an answer')
        print('3. Sign out')
        print('4. Quit')
        option = input('\nChoose from 1-4: ')
        if option == '1':
            action.postQ(conn, curr, uid)
        elif option == '2':
            resultTable = action.searchPosts(curr)
        
            initLimit = 5
            no, opt = action.displaySearchResult(resultTable, initLimit)
            targetPost = resultTable[no]
            targetpid = targetPost[0]           # TODO row factory & use col name

            if opt == 1:
                action.castVote(conn, curr, targetpid, uid)
            elif opt == 2:
                action.postAns(conn, curr, uid, targetpid)

        elif option == '3':
            if page.checkSignout():
                print('...')
                print('You have been signed out.')
                valid = True

        elif option == '4':
            sys.exit(0)


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
        # TODO uid must be 4 chars
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

    return uid


def checkSignout():
    '''
    Checks if the user wants to sign out.
    '''
    while True:
        signout = input('Do you want to sign out? y/n ').lower()
        if signout == 'y':
            return True
        elif signout == 'n':
            return False


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
