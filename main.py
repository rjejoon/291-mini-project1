import sqlite3
import os 
import sys
import traceback

from util import bcolor
from util import page


def main(argv):
    '''
    The main loop of the program.

    Error codes:
        0: Success
        2: invalid command line argument
    '''
    db = getDBFrom(argv)
    conn, curr = initConnAndCurrFrom(db)
    tempTestData(curr, 'testSchema.sql')

    try:
        os.system('clear')
        run = True
        while run:
            page.printFirstScreen() 

            prompt = "Enter a command: "
            opt = page.getValidInput(prompt, ['si', 'su', 'q'])
            if opt == 'si':
                uid = page.signIn(conn, curr)
                os.system('clear')
                page.mainMenu(conn, curr, uid)
            elif opt == 'su':
                uid = page.signUp(conn, curr)
                # TODO do we need to re-sign in ?
            else:
                run = False
        sys.exit(0)

    except SystemExit as e:
        if int(str(e)) > 0:
            print(traceback.format_exc())   # TODO change to simple error messeage
    except Exception as e:
        print(traceback.format_exc())
    finally:
        print("\nClosing connection...")
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
        sys.exit(2)
    
    return argv[1]

# TODO delete after testing
def tempTestData(curr, filename):
    sqlFile = open(filename)
    sqlString = sqlFile.read()
    curr.executescript(sqlString)




if __name__ == "__main__":

    main(sys.argv)
