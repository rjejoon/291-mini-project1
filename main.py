import sqlite3
import os 
import sys
import traceback

from util import page


def main():
    '''
    The main loop of the program.

    Error codes:
        0: Success
        1: invalid command line argument
    '''
    db = getDBFrom(sys.argv)
    conn, curr = initConnAndCurrFrom(db)
    tempTestData(curr, 'testSchema.sql')

    # TODO clear out the terminal whenever user goes to the first screen
    try:
        # first screen
        run = True
        while run:
            # TODO change interface of the first screen    
            uInput = input("\nOptions: (si) sign in, (su) sign up, (q)uit: ").lower()

            if uInput == 'q':
                run = False
            elif uInput in ('si', 'su'):    # TODO checks strings twice. Prob change this to one if..else statement
                if uInput == 'si':
                    uid, name = page.signIn(conn, curr)
                else:
                    uid, name = page.signUp(conn, curr)
                page.mainMenu(conn, curr, uid, name)
            else:
                print("error: invalid command")
    except:
        print(traceback.format_exc())
    finally:
        print("Closing connection...")
        conn.commit()
        conn.close()


def initConnAndCurrFrom(db):
    '''
    Make a connection and cursur from a specified database.

    Keyword arguments:
    db —- database file 
    '''
    dir_path = os.path.abspath(os.path.dirname(__file__)) + os.sep
    db_path = dir_path + db 

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    curr = conn.cursor()

    return conn, curr


def getDBFrom(argv):

    if len(argv) != 2:
        print("Usage: python3 main.py [file]") 
        sys.exit(1)
    
    return argv[1]

# TODO delete after testing
def tempTestData(curr, filename):
    sqlFile = open(filename)
    sqlString = sqlFile.read()
    curr.executescript(sqlString)


if __name__ == "__main__":

    main()
