import sqlite3
import psycopg2

class counter:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="mnmtkjiq",
            user="mnmtkjiq",
            password="l4VVFaLXp0iG9dvnstPHvMefVl1z8Dsy",
            host="satao.db.elephantsql.com",
            port=5432
        )
        self.cursor = self.conn.cursor()
    
    def setData(self, server: int, user: int, channel: int):
        self.cursor.execute(f"UPDATE data SET t_server = {server}, t_user = {user}, t_channel = {channel} WHERE id = 1")
        self.conn.commit()

class database:
    def __init__(self):
        self.db = sqlite3.connect("./database/data.db")
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS discord(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INT,
            channel_id INT,
            embed_id INT,
            server_ip varchar(255),
            server_port varchar(255),
            server_type varchar(255)

            )''')

        # self.cursor.execute('''CREATE TABLE IF NOT EXISTS information(
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     total_member INT,
        #     total_guild INT,
        #     total_channel INT
        # )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS server(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild INT
            )''')
        self.db.commit()

    def isEmbedExist(self, id):
        self.cursor.execute(f"SELECT * FROM discord WHERE guild_id = {id}")
        data = self.cursor.fetchall()
        for x in data:
            return True
        else:
            return False
    
    def setServer(self, guild_id: int, address: str, port="25565", type="java"):
        if self.isEmbedExist(guild_id):
            # UPDATE discord SET server_ip = '" + address + "', server_port = '" + port + "', server_type = '" + type + "' WHERE guild_id = " + guild_id + ";")
            self.cursor.execute("UPDATE discord SET server_ip = ?, server_port = ?, server_type = ? WHERE guild_id = ?", (address, port, type, guild_id))
            self.db.commit()
            return True
        else:
            return False
    
    def insertData(self, guild_id, channel_id, embed_id, server_ip, server_type, port="25565"):
        if self.isEmbedExist(guild_id) == False:
            self.cursor.execute('''INSERT INTO discord(
                guild_id,
                channel_id,
                embed_id,
                server_ip,
                server_port,
                server_type
                ) VALUES(?, ?, ?, ?, ?, ?)''', (guild_id, channel_id, embed_id, server_ip, port, server_type))
            self.db.commit()
            return True
        else:
            return False

    def insertRequest(self, guild_id: int):
        self.cursor.execute(f"INSERT INTO server(guild) VALUES({int(guild_id)})")
        self.db.commit()

    def getTotalEmbed(self, guild_id: int):
        self.cursor.execute(f"SELECT * FROM discord WHERE guild_id = {guild_id}")
        data = self.cursor.fetchall()
        return len(data)

    def getMessageId(self, guild_id: int):
        self.cursor.execute(f"SELECT * FROM discord WHERE guild_id = {int(guild_id)}")
        data = self.cursor.fetchall()
        return data

    def removeEmbed(self, guild_id: int):
        if self.isEmbedExist(guild_id) == True:
            self.cursor.execute(f"DELETE FROM discord WHERE guild_id = {guild_id}")
            self.db.commit()
            return True
        else:
            return False

    def totalRequest(self):
        self.cursor.execute("SELECT * FROM server")
        data = self.cursor.fetchall()
        return len(data)

    def guildData(self):
        self.cursor.execute("SELECT * FROM discord")
        data = self.cursor.fetchall()
        return data

    def deleteData(self, id: int):
        self.cursor.execute(f"DELETE FROM discord WHERE id = {id}")
        self.db.commit()

# database().insertData(610813273817743362, 1, 1, "1", "2", "3")
# print(database().getTotalEmbed(610813273817743360))
#print(database().guildData())
# database().insertData(1, 2, 3, "a", "b", "c")
# print(database().guildData())