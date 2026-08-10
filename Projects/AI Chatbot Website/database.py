import sqlite3


def create_database():

    con=sqlite3.connect(
        "database/chats.db"
    )

    cur=con.cursor()


    cur.execute("""

    CREATE TABLE IF NOT EXISTS chats(

    id INTEGER PRIMARY KEY,

    role TEXT,

    message TEXT

    )

    """)


    con.commit()

    con.close()



def save_message(role,message):

    con=sqlite3.connect(
        "database/chats.db"
    )

    cur=con.cursor()


    cur.execute(

    "INSERT INTO chats(role,message) VALUES (?,?)",

    (role,message)

    )


    con.commit()

    con.close()