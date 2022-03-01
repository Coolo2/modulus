import datetime
import aiofiles

class Version():
    def __init__(self, name : str, release_date : datetime.datetime):
        self.release_date = release_date
        self.name = name 
    
    async def get_changelogs(self):
        with aiofiles.open(f"resources/changelogs/{self.name}") as f:
            return await f.read()

versions = [
    Version("1.0.0", datetime.date(2022, 6, 10))
]