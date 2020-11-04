import sys
import os 
import getpass

from datetime import date
import bcolor
import action
import paction  


def mainMenu(conn, curr, uid):
    '''
    The main loop of the main menu available after successful sign in.

    Inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        uid -- uid of signed in user
    '''
    isPriv = isPrivileged(curr, uid)

    valid = False
    while not valid:

        name = getName(curr, uid)
        printMainPage(name, isPriv)

        option = getValidInput('Enter a command: ', ['pq', 'sp', 'so', 'q']) 
        if option == 'pq':
            action.postQ(conn, curr, uid)

        elif option == 'sp':
            resultTable = action.searchPosts(curr)
            if len(resultTable) > 0:
                no, act = action.displaySearchResult(resultTable, isPriv)
                targetPost = resultTable[no]
                targetPoster = targetPost['poster']
                targetPid = targetPost['pid']
                executeAction(conn, curr, act, uid, targetPid, targetPoster)
            else:
                print(bcolor.errmsg('No posts found.'))
            
        elif option == 'so':
            if checkSignout():
                print('...')
                print(bcolor.green('You have been signed out.'))
                valid = True

        elif option == 'q':
            print('...')
            print(bcolor.green('You have been signed out.'))
            sys.exit(0)


def executeAction(conn, curr, act, uid, targetPid, targetPoster):
    '''
    Execute a post action on the selected post.

    inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        act -- action command
        uid -- signed in user id
        targetPid -- selected post id
        targetPoster -- user id of the user who wrote the selected post
    '''
    actionOpts = {
                    'vp': 1,
                    'wa': 2,
                    'ma': 3,
                    'gb': 4,
                    't': 5,
                    'ep': 6,
                    'bm': 7
                            }
    opt = actionOpts[act]
    if opt == 1:
        action.castVote(conn, curr, targetPid, uid)
    elif opt == 2:
        action.postAns(conn, curr, uid, targetPid)
    elif opt == 3:
        paction.markAnswer(conn, curr, targetPid)
    elif opt == 4:
        paction.giveBadge(conn, curr, targetPoster)
    elif opt == 5:
        paction.addTag(conn, curr, targetPid)
    elif opt == 6:
        paction.editPost(conn, curr, targetPid)
    elif opt == 7:
        os.system('clear')


def signIn(curr):
    '''
    Prompts the user to enter their user ID and password. Checks if they exist in the database. 
    If not, it returns the user ID. 

    Inputs: 
        curr -- sqlite3.Cursor
    Returns: 
        str
    '''
    validInfo = False
    while not validInfo:

        uid = input('\nEnter your user ID: ')
        pwd = getpass.getpass('Enter your password: ')

        curr.execute('SELECT * FROM users WHERE uid = :userID COLLATE NOCASE AND pwd = :password;',
                    {'userID': uid, 'password': pwd})

        userRow = curr.fetchone()

        if userRow:
            validInfo = True
            print(bcolor.green('You have successfully signed in.'))
            return userRow['uid']
            
        else:
            print(bcolor.errmsg('error: invalid user ID or password.'))
            prompt = "Do you stil want to sign in? [y/n] "
            uin = getValidInput(prompt, ['y','n'])
            if uin == 'n':
                return None
            

def signUp(conn, curr):
    '''
    Prompt the user for necessary information for account creation, and save it into the database.

    inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
    '''
    valid = False
    while not valid:

        print()
        # ask for id, name, city, password
        uid = getNewID(curr)
        f_name = input("Enter your first name: ").capitalize() 
        l_name = input("Enter your last name: ").capitalize()
        name = ' '.join((f_name, l_name)) 
        city = input("Enter your city: ").capitalize()
        pwd = getNewPassword()
        crdate = str(date.today())
            
        if checkValid(uid, name, city):
            valid = True
        else:
            cont = getValidInput('Do you still want to sign up? [y/n] ', ['y', 'n'])
            if cont == 'n':
                return 

    print(bcolor.green("Sign up successful!"))

    curr.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?);", 
            [uid, name, pwd, city, crdate])

    conn.commit()


def printFirstScreen():
    '''
    Display the interface of the first screen of the program.
    '''
    print()
    print(bcolor.pink('Menu:'))
    print()
    print('   {}: {}ign {}n'.format(bcolor.bold('si'), bcolor.u_ualphas[18], bcolor.u_ualphas[8]))
    print('   {}: {}ign {}p'.format(bcolor.bold('su'), bcolor.u_ualphas[18], bcolor.u_ualphas[20]))
    print('   {}: {}uit'.format(bcolor.bold('q'), bcolor.u_ualphas[16]))
    print()


def checkSignout():
    '''
    Check if the user wants to sign out.
    '''
    so = getValidInput('Do you want to sign out? [y/n] ', ['y', 'n'])
    if so == 'y':
        return True
    return False


def getNewID(curr):
    '''
    Get an appropriate user id and return it.

    input:
        curr -- sqlite3.Cursor
    '''
    valid = False
    uid = None
    while not valid: 
        if not uid: 
            uid = input("Enter your id: ")

        if uid.isalnum():
            if isUidUnique(curr, uid):
                if len(uid) > 4:
                    prompt = bcolor.warning("Warning: maximum id length is 4. Use '{}' instead? [y/n] ".format(uid[:4]))
                    uin = getValidInput(prompt, ['y', 'n'])
                    uid = uid[:4] if uin == 'y' else None
                else:
                    valid = True
            else:
                print(bcolor.errmsg("error: user id already taken."))
                uid = None
        else:
            print(bcolor.errmsg("error: password cannot contain any special characters.")) 
            uid = None

    return uid


def isUidUnique(curr, uid):
    '''
    Return True if the given uid is unique in the database.

    inputs:
        curr -- sqlite3.Cursor
        uid -- str
    '''
    curr.execute("SELECT * FROM users WHERE uid = ?;", [uid])
    if not curr.fetchone():
        return True
    return False


def getNewPassword():
    '''
    Get a new password from the user.
    Passwords are case-sensitive and can only contain alphanumeric characters.

    Return:
        pwd -- str
    '''
    valid = False
    while not valid:
        pwd = getpass.getpass("Enter your password: ")
        if pwd.isalnum():
            pwd2 = getpass.getpass("Enter the password again: ")
            if pwd == pwd2:
                valid = True
            else:
                print(bcolor.errmsg("error: passwords do not match."))
        else:
            print(bcolor.errmsg("error: password cannot contain any special characters.")) 

    return pwd


def checkValid(uid, name, city):
    '''
    Prompt the user to double check their account information, and return True if yes.
    '''
    print()
    print(bcolor.warning("Please double check your information: "))
    print("   id: {}".format(uid))
    print("   name: {}".format(name))
    print("   city: {}".format(city))
    print()

    prompt = 'Is this correct? [y/n] '
    uin = getValidInput(prompt, ['y','n'])
    if uin == 'y':
        return True
    return False


def continueAction(prompt):
    '''
    Confirm the users if they still want to continue the current action.
    '''
    uin = getValidInput(prompt, ['y', 'n'])
    return True if uin == 'y' else False


def isPrivileged(curr, uid):
    '''
    Return True if the user is priviledged.
    '''
    curr.execute("SELECT uid FROM privileged where uid = ?;", (uid, ))
    if not curr.fetchone():
        return False
    return True


def getValidInput(prompt, validEntries):
    '''
    Prompt the user with the provided prompt.
    If the user input is not in validEntries, print error.

    inputs:
        prompt -- str
        validEntries -- list
    '''
    while True:
        i = input(prompt).lower()
        if i in validEntries:
            return i 
        print(bcolor.errmsg("error: invalid entry\n"))


def getName(curr, uid):
    '''
    Return the name of the user.
    '''
    curr.execute("SELECT name FROM users WHERE uid=?;", (uid,))
    return curr.fetchone()[0]


def printMainPage(name, isPriv):
    '''
    Display the main menu interface along with the name of the user.

    inputs:
        name -- str
        isPriv -- bool
    '''
    # underlined letter
    u_O = bcolor.u_ualphas[14]
    u_P = bcolor.u_ualphas[15]
    u_Q = bcolor.u_ualphas[16]
    u_S = bcolor.u_ualphas[18]

    userType = bcolor.cyan('privileged') if isPriv else ''

    print()
    print('* * WELCOME {}! * * {}'.format(name, userType)) 
    print()
    print(bcolor.pink('[ M E N U ]'))
    print()
    print('   {}: {}ost a {}uestion'.format(bcolor.bold('pq'), u_P, u_Q))
    print('   {}: {}earch for {}osts'.format(bcolor.bold('sp'), u_S, u_P))
    print('   {}: {}ign {}ut'.format(bcolor.bold('so'), u_S, u_O))
    print('   {}:  {}uit'.format(bcolor.bold('q'), u_Q))
    print()
