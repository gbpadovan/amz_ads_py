#python 3.11.15
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

URLS = {
    'return_url':os.getenv('RETURN_URL'),    
    'usa'     :{
        # url mode:
        # https://advertising.amazon.com/API/docs/en-us/guides/get-started/create-authorization-grant#determine-the-url-prefix-for-your-region
        'access_code':"https://www.amazon.com",
        'authorize'  :"https://api.amazon.com",
        'ad'         :"https://advertising-api.amazon.com",
    },
    'ca'      :{
        # url mode:
        'access_code':"https://www.amazon.com",
        'authorize'  :"https://api.amazon.com",
        'ad'         :"https://advertising-api.amazon.com",
    },
    'uk'      :{
        # url mode:
        'access_code':"https://eu.account.amazon.com",
        'authorize'  :"https://api.amazon.co.uk",
        'ad'         :"https://advertising-api-eu.amazon.com",
    },
    'au'      :{
        # url mode:
        'access_code':"https://apac.account.amazon.com",
        'authorize'  :"https://api.amazon.co.jp",
        'ad'         :"https://advertising-api-fe.amazon.com",
    },
    'sandbox'      :{
        # url mode:
        'access_code':"https://www.amazon.com",
        'authorize'  :"https://api.amazon.com",
        'ad'         :"https://advertising-api-test.amazon.com",
    },            
}


PROFILES ={
    'usa': {
        'profile_id'     :os.getenv('USA_PROFILE_ID'),
        'account_id'     :os.getenv('USA_ACCOUNT_ID'),
        'mktplace_id'    :os.getenv('USA_MKTPLACE_ID'),
        'mktplace_str_id':os.getenv('USA_MKTPLACE_STR_ID'),
        'refresh_token'  :os.getenv('USA_REFRESH_TOKEN'),
    },
    'uk': {
        'profile_id'     :os.getenv('UK_PROFILE_ID'),
        'account_id'     :os.getenv('UK_ACCOUNT_ID'),
        'mktplace_id'    :os.getenv('UK_MKTPLACE_ID'),
        'mktplace_str_id':os.getenv('UK_MKTPLACE_STR_ID'),
        'refresh_token'  :os.getenv('UK_REFRESH_TOKEN'),
    },
    'au': {
        'profile_id'     :os.getenv('AU_PROFILE_ID'),
        'account_id'     :os.getenv('AU_ACCOUNT_ID'),
        'mktplace_id'    :os.getenv('AU_MKTPLACE_ID'),
        'mktplace_str_id':os.getenv('AU_MKTPLACE_STR_ID'),
        'refresh_token'  :os.getenv('AU_REFRESH_TOKEN'),
    },
    'ca': {
        'profile_id'     :os.getenv('CA_PROFILE_ID'),
        'account_id'     :os.getenv('CA_ACCOUNT_ID'),
        'mktplace_id'    :os.getenv('CA_MKTPLACE_ID'),
        'mktplace_str_id':os.getenv('CA_MKTPLACE_STR_ID'),
        'refresh_token'  :os.getenv('CA_REFRESH_TOKEN'),
    },
}
