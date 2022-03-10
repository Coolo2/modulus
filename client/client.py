from client import fileclient, httpclient, dataclient

class Client():

    def __init__(self, bot):
        
        self.bot = bot
        
        self.http = httpclient.HTTP(self)

        self.file = fileclient.FileClient(self)

        self.data = dataclient.DataClient(self)