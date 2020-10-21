import sqlite3
import os 
import getpass
from datetime import date

def main():
    '''
    The main loop of the program.
    '''
    conn, curr = initConnAndCurrFrom('schema.sql', 'socialmedia.db')

    run = True
    while run:
        
        # first screen
        uInput = input("\nOptions: (si) sign in, (su) sign up, (q)uit: ").lower()

        if uInput == 'q':
            run = False
        elif uInput == 'si':
            signIn()
        elif uInput == 'su':
            signUp(conn, curr)
        else:
            print("error: command not found.")

    conn.commit()
    conn.close()


def initConnAndCurrFrom(f_name, db_name):
    '''
    Reads in DDL from a text file and returns sqlite3 connection and cursor associated to the specified database.

    Keyword arguments:
    f_name —- text file containing SQL DDL
    db_name -- .db file
    '''
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep
    f_path = dir_path + f_name
    db_path = dir_path + db_name 

    conn = sqlite3.connect(db_path)
    curr = conn.cursor()
    with open(f_path, 'r') as f:
        
        query = ''.join(f.readlines())
       
    curr.executescript(query)

    conn.commit()

    return conn, curr


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
