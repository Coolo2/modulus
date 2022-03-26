from client import client
import json  
import aiohttp 
import asyncio
import nest_asyncio
import aiofiles

class HTTP():
    def __init__(self, client : client):
        self.client = client

        self.loop = asyncio.new_event_loop()
        nest_asyncio.apply(self.loop)

        self.headers = {}

        
    
    async def get_file(
        self, url = None, params : dict = {}
    ):
        
        headers = self.headers

        async with aiohttp.ClientSession() as session:
            
            async with session.request("GET", url, headers=headers, params=params) as r:

                try:
                    return await r.read()
                    
                except aiohttp.ContentTypeError:
                    return None
    
    async def post_file(
        self, url, file_name : str, file_path : str
    ):
        async with aiofiles.open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=file_name)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    
                    return response 
        
        

    async def json_request(
        self, method : str, data = None, url = None, params : dict = {}, headers=None
    ):
        
        if not headers:
            headers = self.headers
        if data != None:
            data = json.dumps(data)

        async with aiohttp.ClientSession() as session:
            
            async with session.request(method, url, data=data, headers=headers, params=params) as r:


                try:
                    return await r.json()
                    
                except aiohttp.ContentTypeError:
                    return None