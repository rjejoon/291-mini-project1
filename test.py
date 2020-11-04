import sqlite3


def main():

    conn = sqlite3.connect('test.db')
    curr = conn.cursor()

    d = {'kw1': '%database%'}

    curr.execute('Select * from posts where title like :kw1', d)

    for row in curr.fetchall():
        print(row)



main()
