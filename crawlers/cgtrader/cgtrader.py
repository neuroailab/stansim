"""Illustrative use of CGTrader API
based on https://api.cgtrader.com/docs/index.html
"""
import json
import os

from rauth import OAuth2Service		  
						  
base_url = "https://api.cgtrader.com"
client_id = os.environ['CGTRADER_ID']
client_secret = os.environ['CGTRADER_SECRET']
				

class CGTraderClient():
    def __init__(self):
        self.access_token = None

        self.service = OAuth2Service(
            client_id=client_id,
            client_secret=client_secret,
            access_token_url="https://api.cgtrader.com/oauth/token",
            authorize_url="https://api.cgtrader.com/oauth/authorize",
            base_url=base_url,
        )

    def test_api(self):
        data = {
                'grant_type': 'client_credentials',
                'redirect_uri': '..'
                }

        session = self.service.get_auth_session(data=data, decoder=json.loads)

        self.access_token = session.access_token

        res = session.get('/v1/models',
                          params = { "keywords": "auto",
                                     "per_page": 100}).json()

        print(len(res['models']))

    def list_categories(self):
        data = {
            'grant_type': 'client_credentials',
                'redirect_uri': '..'
            }
        
        session = self.service.get_auth_session(data=data, decoder=json.loads)
        
        self.access_token = session.access_token
        
        res = session.get('/v1/categories').json()

        for i in res['categories']:
            print i

        return res['categories']

    def get_model(self, modelID):
        data = {
            'grant_type': 'client_credentials',
            'redirect_uri': '..'
            }
        
        session = self.service.get_auth_session(data=data, decoder=json.loads)
        
        self.access_token = session.access_token
        

        res = session.get("/v1/models/%i" % modelID,params = { "id": "%i" % modelID })

        # Handle the case when a model with a given ID does not exist.
        if res.status_code == 200:
            res = res.json()
            print "Model %i (%s), price: $%i, files %i, downloadable %r" % (res["id"],res["slug"],res['prices']['download'], len(res['files']),res['downloadable'])
        else:
            res = None
        
        return res



    def save_model_file(self,modelID,fileID, fileName):
        data = {
            'grant_type': 'client_credentials',
            'redirect_uri': '..'
            }
        
        session = self.service.get_auth_session(data=data, decoder=json.loads)
        
        self.access_token = session.access_token

        res = session.get("/v1/models/%i/files/%i" % (modelID,fileID),
                          params = {"model_id" : "%i" % modelID, "id": "%i" % fileID}, stream=True)
        
        with open(fileName, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)




if __name__ == '__main__':
    A = CGTraderClient()
    # A.test_api()
    A.list_categories()

    mdl = A.get_model(11)
    
    # for fileEntry in mdl["files"]:
    #    print fileEntry
    #    A.save_model_file(mdl["id"],fileEntry["id"],fileEntry["name"])

    # A.get_model_files_list(77169)
    # A.get_model_file(77169,24)
