import sqlite3
import os 

def main():
    
    conn, curr = initConnAndCurrFrom('schema.sql')

    run = True
    while run:
        
        # first screen
        uInput = input("Options: (si) sign in, (su) sign up, (q)uit: ").lower()

        if uInput == 'q':
            run = False
        elif uInput == 'si':
            signIn()
        elif uInput == 'su':
            signUp()
        else:
            print("error: command not found.")

def initConnAndCurrFrom(f_name):

    conn = sqlite3.connect('./socialmedia.db')
    curr = conn.cursor()

    path = os.path.abspath(os.path.dirname(__file__)) + os.sep + f_name
    with open(path, 'r') as f:
        
        query = ''.join(f.readlines())
       
    curr.executescript(query)

    conn.commit()

    return conn, curr

def signUp():
    pass






if __name__ == "__main__":

    main()
