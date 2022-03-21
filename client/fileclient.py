from client import client
import aiosqlite
import aiofiles
import setup


class FileClient():

    def __init__(self, client):
        
        self.client = client

        self.db = None
        self.databases = []
    
    async def initialise_databases(self):
        self.db = Database(self, "data.db")
        self.tracking = Database(self, "tracking.db")

        await self.db.initialise()
        await self.tracking.initialise()

        self.databases.append(self.db)
        self.databases.append(self.tracking)

    async def sync_databases(self):
        
        for database in self.databases:

            await database.reload()

            data = await self.client.http.post_file(url=database.url_post, file_name=database.name, file_path=database.path)

class Database():

    def __init__(self, fileclient : FileClient, name : str):
        self.name = name
        self.path = f"sql/{self.name}"
        self.url_get = f"https://helperdata.glitch.me/get/{self.path}"
        self.url_post = f"https://helperdata.glitch.me/post{setup.env('databaseToken')}/{self.path}"
        
        print(f"Getting database {self.path}")
        fileData = fileclient.client.http.loop.run_until_complete(
            fileclient.client.http.get_file(url=self.url_get)
        )

        with open(self.path, "wb") as f:
            f.write(fileData)
        
        self.db = None 
        
    
    async def initialise(self):
        await self.reload()
    
    async def table_exists(self, table : str):
        cursor = await self.db.execute( "SELECT name FROM sqlite_master WHERE type='table' ")
        tables = await cursor.fetchall()

        return  (table,) in tables
    
    async def row_exists_with_value(self, table : str, attribute : str, value):
        cursor = await self.db.execute(f"SELECT * FROM {table} WHERE {attribute}=?", [value])
        f = await cursor.fetchall()

        return len(f) > 0


    async def reload(self):
        if self.db:
            await self.db.commit()
            #await self.db.close()
        else:
            self.db = await aiosqlite.connect(self.path)
