from client import client
import aiosqlite
import aiofiles


class FileClient():

    def __init__(self, client):
        
        self.client = client

        self.db = None
        self.databases = []
    
    async def initialise_databases(self):
        self.db = Database(self, "data.db")

        await self.db.initialise()

        self.databases.append(self.db)

    async def sync_databases(self):
        
        for database in self.databases:

            await database.reload()

            await self.client.http.post_file(url=database.url_post, file_name=database.name, file_path=database.path)

            print(f"done {database.path}")

class Database():

    def __init__(self, fileclient : FileClient, name : str):
        self.name = name
        self.path = f"sql/{self.name}"
        self.url_get = f"https://helperdata.glitch.me/get/{self.path}"
        self.url_post = f"https://helperdata.glitch.me/post/{self.path}"
        
        print(f"Getting database {self.path}")
        fileData = fileclient.client.http.loop.run_until_complete(
            fileclient.client.http.get_file(url=self.url_get)
        )

        with open(self.path, "wb") as f:
            f.write(fileData)
        
        self.db = None 
        
    
    async def initialise(self):
        await self.reload()

    async def reload(self):
        if self.db:
            await self.db.commit()
            await self.db.close()

        self.db = await aiosqlite.connect(self.path)