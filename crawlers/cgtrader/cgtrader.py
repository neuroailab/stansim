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
            base_url="https://api.cgtrader.com",
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
        
        
if __name__ == '__main__':
    A = CGTraderClient()
    A.test_api()
