from client import fileclient, httpclient

class Client():

    def __init__(self):
        
        
        self.http = httpclient.HTTP(self)

        self.file = fileclient.FileClient(self)