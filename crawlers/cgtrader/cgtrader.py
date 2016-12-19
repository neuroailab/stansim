import json
import os

from rauth import OAuth2Service		  
						  
base_url = "https://api.cgtrader.com"
client_id = os.environ['CGTRADER_ID']
client_secret = os.environ['CGTRADER_SECRET']
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
				

class ExampleOAuth2Client:
    def __init__(self):
        self.access_token = None

        self.service = OAuth2Service(
            client_id=client_id,
            client_secret=client_secret,
            access_token_url="https://api.cgtrader.com/oauth/token",
            authorize_url="https://api.cgtrader.com/oauth/authorize",
            base_url="https://api.cgtrader.com",
        )

        self.get_access_token()

    def get_access_token(self):
        data = {
                'grant_type': 'client_credentials',
                'redirect_uri': '..'
                }

        session = self.service.get_auth_session(data=data, decoder=json.loads)

        self.access_token = session.access_token
        
        print(self.access_token)
        
if __name__ == '__main__':
	A = ExampleOAuth2Client()
	A.get_access_token()