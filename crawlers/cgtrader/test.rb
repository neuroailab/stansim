#this is based on the cgtrader API at https://api.cgtrader.com/docs/index.html
require 'oauth2'

client_id = ENV["CGTRADER_ID"]
secret = ENV["CGTRADER_SECRET"] 
base_url = "https://api.cgtrader.com/"

client = OAuth2::Client.new(client_id,
                            secret, 
			    site: base_url)

access_token = client.client_credentials.get_token

response = JSON.parse(access_token.get('/v1/models',
                                       params: { "keywords": "auto",
                                                 "per_page": 100,
                                               }).body)

models = response['models']

puts models.length