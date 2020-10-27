import sqlite3

def markAnswer(conn, curr, aid):

    curr.execute("SELECT pid FROM answers where pid=?;", (aid, ))
    pid = curr.fetchone()[0]

    curr.execute("SELECT theaid fROM questions where pid=?;", (pid, ))
    # aa: accepted answer
    aaExists = False if not curr.fetchone() else True

    if aaExists:
        prompt = "Warning: Accepted answer already exists! Proceed to change? y/n:"
        valid = False
        while not valid:
            inp = input(prompt)
            if valid == 'y':
                valid = True
                changeAA(conn, curr, pid, aid)
            elif valid == 'n':
                valid = True
            else:
                print("error: invalid command")
    
    else:
        changeAA(conn, curr, pid, aid)

    print("Accepted answer successfully updated!")
            

def edit(conn, curr, pid):
    '''
    Edit the selected post.

    inputs:
        conn: sqlite3.Connection
        curr: sqlite3.Cursor
        pid: posts.pid
    '''
    curr.execute("SELECT title, body FROM posts WHERE pid=?", (pid, )) 
    currT, currB = curr.fetchone()

    print("< Editing >")
    print("Press enter with nothing typed if you want to keep the content the same.")
    print()
    confirmed = False
    while not confirmed:
        nTitle, nBody = change(currT, currB)
        confirmed = isChangeValid(nTitle, nBody)

    curr.execute(''' 
                    UPDATE
                        posts
                    SET
                        title = ?,
                        body = ?
                    WHERE
                        pid = ?;''', (nTitle, nBody, pid))
    conn.commit()

    print("Change complete!")


def change(oldTitle, oldBody):

    print("You are currently editing:")
    print()
    print("   Title: {}".format(oldTitle))
    print()
    nTitle = input("Type a new title: ")
    if nTitle == '':
        nTitle = oldTitle

    print()
    print("You are currently editing:")
    print()
    print("   Body: {}".format(oldBody))
    print()
    nBody = input("Type a new Body: ") 
    if nBody == '':
        nBody = oldBody
        
    return nTitle, nBody

    
def isChangeValid(nTitle, nBody):

    print("Is this correct?")
    print("\n   Title: {}".format(nTitle))
    print("\n   Body: {}".format(nBody))

    while True:
        check = input("\nType 'y' if it is correct. Type 'n' if you want to start over: ")
        if check == 'y':
            return True
        elif check == 'n':
            return False
        else:
            print("error: invalid command")


def changeAA(conn:sqlite3.Connection, curr, pid, aid):

    curr.execute('''UPDATE 
                        questions
                    SET 
                        theaid = :aid
                    WHERE
                        pid = :pid;''', {'aid': aid, 
                                         'pid': pid})
    conn.commit()

                        
                     

    
