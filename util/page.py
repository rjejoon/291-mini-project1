import sys
import os 
import getpass

from datetime import date
from util import bcolor
from user import action
from user.privileged import action as privAction # TODO change name 


def mainMenu(conn, curr, uid):
    '''
    Displays the menu and Prompts the user to choose from some actions.

    Inputs:
        conn -- sqlite3.Connection
        curr -- sqlite3.Cursor
        uid -- uid of the current user
    '''
    isPriv = isPrivileged(curr, uid)
    actionOpts = {
                    'vp': 1,
                    'wa': 2,
                    'ma': 3,
                    'gb': 4,
                    't': 5,
                    'ep': 6
                            }

    valid = False
    while not valid:
        # TODO change interface
        name = getName(curr, uid)
        printMainPage(name, isPriv)
        option = getValidInput('Enter a command: ', ['pq', 'sp', 'so', 'q']) 
        if option == 'pq':
            action.postQ(conn, curr, uid)
        elif option == 'sp':
            resultTable = action.searchPosts(curr)
            if len(resultTable) > 0:
                no, act = action.displaySearchResult(resultTable, isPriv)
                
                opt = actionOpts[act]
                targetPost = resultTable[no]
                targetUid = targetPost['poster']
                targetPid = targetPost['pid']        

                if opt == 1:
                    action.castVote(conn, curr, targetPid, uid)
                elif opt == 2:
                    action.postAns(conn, curr, uid, targetPid)
                elif opt == 3:
                    privAction.markAnswer(conn, curr, targetPid)
                elif opt == 4:
                    privAction.giveBadge(conn, curr, targetUid)
                elif opt == 5:
                    privAction.addTag(conn, curr, targetPid)
                elif opt == 6:
                    privAction.edit(conn, curr, targetPid)
            else:
                print(bcolor.errmsg('No posts found.'))
            
        elif option == 'so':
            if checkSignout():
                print('...')
                print('You have been signed out.')
                valid = True

        elif option == 'q':
            print('...')
            print('You have been signed out.')
            sys.exit(0)


def signIn(conn, curr):
    '''
    Prompts the user to enter their user ID and password. Checks if they exist in the database and Returns them.

    Inputs: conn, curr
    Returns: userID
    '''

    i = 0
    validInfo = False
    while not validInfo:

        uid = input('\nEnter your user ID: ')
        pwd = getpass.getpass('Enter your password: ')

        curr.execute('SELECT * FROM users WHERE uid = :userID COLLATE NOCASE AND pwd = :password;',
                    {'userID': uid, 'password': pwd})

        userRow = curr.fetchone()

        if userRow:
            validInfo = True
        else:
            print(bcolor.errmsg('error: invalid user ID or password. Please try again.'))
        
    print(bcolor.green('You have successfully signed in.'))

    return userRow['uid']


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
        f_name = input("Enter your first name: ").capitalize() 
        l_name = input("Enter your last name: ").capitalize()
        name = ' '.join((f_name, l_name)) 
        city = input("Enter your city: ").capitalize()
        pwd = getPassword()
        crdate = str(date.today())
            
        print()
        print(bcolor.warning("Please double check your information: "))
        print("   id: {}".format(uid))
        print("   name: {}".format(name))
        print("   city: {}".format(city))

        if checkValid():
            valid = True
        else:
            cont = getValidInput('Do you wish to continue signing up? [y/n] ', ['y', 'n'])
            if cont == 'n':
                return None

    print(bcolor.green("Sign up successful!"))

    curr.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
            [uid, name, pwd, city, crdate])

    conn.commit()

    return uid


def printFirstScreen():
    '''
    Displays the UI of the first screen of the program.
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
    uid = None
    while not valid: 
        if not uid: 
            uid = input("Enter your id: ")
        if isUnique(curr, uid):
            if len(uid) > 4:
                prompt = bcolor.warning("Warning: maximum id length is 4. Use '{}' instead? [y/n] ".format(uid[:4]))
                uin = getValidInput(prompt, ['y', 'n'])
                uid = uid[:4] if uin == 'y' else None
            else:
                valid = True
        else:
            print(bcolor.errmsg("error: user id already taken."))
            uid = None

    return uid


def isUnique(curr, uid):
    
    curr.execute("SELECT * FROM users WHERE uid = ?;", [uid])
    if not curr.fetchone():
        return True
    return False
    

def getPassword():
    '''
    Gets an appropriate password and returns it.
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


def checkValid():
    '''
    Prompts the user to double check their account information and returns the result.
    '''
    print()
    prompt = 'Is this correct? [y/n] '
    uin = getValidInput(prompt, ['y','n'])
    if uin == 'y':
        return True
    return False



def continueAction(prompt):
    '''
    Confirms the users if they still want to continue the current action.
    '''
    uin = getValidInput(prompt, ['y', 'n'])
    return True if uin == 'y' else False


def isPrivileged(curr, uid):

    curr.execute("SELECT uid FROM privileged where uid = ?;", (uid, ))
    if not curr.fetchone():
        return False
    return True


def getValidInput(prompt, validEntries):

    while True:
        i = input(prompt).lower()
        if i in validEntries:
            return i 
        print(bcolor.errmsg("error: invalid command\n"))

def getName(curr, uid):

    curr.execute("SELECT name FROM users WHERE uid=?;", (uid,))
    return curr.fetchone()[0]


def printMainPage(name, isPriv):

    u_O = bcolor.u_ualphas[14]
    u_P = bcolor.u_ualphas[15]
    u_Q = bcolor.u_ualphas[16]
    u_S = bcolor.u_ualphas[18]

    userType = bcolor.cyan('privileged') if isPriv else ''

    print('\n* * WELCOME {}! * * {}'.format(name, userType)) 
    print('\n' + bcolor.pink('[ M E N U ]') + '\n')
    print('   {}: {}ost a {}uestion'.format(bcolor.bold('pq'), u_P, u_Q))
    print('   {}: {}earch for {}osts'.format(bcolor.bold('sp'), u_S, u_P))
    print('   {}: {}ign {}ut'.format(bcolor.bold('so'), u_S, u_O))
    print('   {}:  {}uit'.format(bcolor.bold('q'), u_Q))
    print()
