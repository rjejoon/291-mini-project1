import sqlite3
import os 
import sys
import traceback

from util import page


def main(argv):
    '''
    The main loop of the program.

    Error codes:
        0: Success
        1: invalid command line argument
    '''
    db = getDBFrom(argv)
    conn, curr = initConnAndCurrFrom(db)

    try:
        run = True
        while run:
            os.system('clear')
            page.printFirstScreen() 

            validEntries = ['si', 'su', 'q']
            prompt = "Choose one of the following options... "
            opt = getValidInput(prompt, validEntries)
            if opt == 'si':
                uid = page.signIn(conn, curr)
                page.mainMenu(conn, curr, uid)
            elif opt == 'su':
                uid = page.signUp(conn, curr)
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
    curr = conn.cursor()

    return conn, curr


def getDBFrom(argv):

    if len(argv) != 2:
        print("Usage: python3 main.py [file]") 
        sys.exit(1)
    
    return argv[1]


def getValidInput(prompt, validEntries):

    while True:
        i = input(prompt).lower()
        if i in validEntries:
            return i 
        print("error: invalid command\n")


if __name__ == "__main__":

    main(sys.argv)
