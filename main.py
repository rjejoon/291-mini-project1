import sqlite3
import os 
import getpass
from datetime import date

def main():
    '''
    The main loop of the program.
    '''
    conn, curr = initConnAndCurrFrom('schema.sql')

    run = True
    while run:
        
        # first screen
        uInput = input("\nOptions: (si) sign in, (su) sign up, (q)uit: ").lower()

        if uInput == 'q':
            run = False
        elif uInput == 'si':
            userID, password = signIn(conn, curr)
        elif uInput == 'su':
            signUp(conn, curr)
        else:
            print("error: command not found.")

    conn.commit()
    conn.close()


def initConnAndCurrFrom(f_name):
    '''
    Reads in DDL from a text file and makes database in memory and returns connection and cursor.

    Keyword arguments:
    f_name —- text file containing SQL DDL
    '''
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep
    f_path = dir_path + f_name

    conn = sqlite3.connect(':memory:')
    curr = conn.cursor()
    with open(f_path, 'r') as f:
        
        query = ''.join(f.readlines())
       
    curr.executescript(query)

    conn.commit()

    return conn, curr


def signIn(conn, curr):
    '''
    Prompts the user to enter their user ID and password. Checks if they exist in the database and Returns them.

    Inputs: conn, curr
    Returns: userID, password
    '''

    validInfo = False
    while not validInfo:

        userID = input('\nEnter your user ID: ')
        password = input('Enter your password: ')

        curr.execute('SELECT * FROM users WHERE uid = :userID AND pwd = :password;',
                    {'userID': userID, 'password': password})

        if curr.fetchone():
            validInfo = True
        else:
            print('error: invalid user ID or password. Please try again.')

    print('You have successfully signed in.\n')
    return userID, password


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
            [uid, name, city, pwd, crdate])

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


if __name__ == "__main__":

    main()
