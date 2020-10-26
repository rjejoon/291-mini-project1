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
            

def changeAA(conn:sqlite3.Connection, curr, pid, aid):

    curr.execute('''UPDATE 
                        questions
                    SET 
                        theaid = :aid
                    WHERE
                        pid = :pid;''', {'aid': aid, 
                                         'pid': pid})
    conn.commit()

                        
                     

    
