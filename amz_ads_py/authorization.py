#python 3.11.15
from .root import Root
from .amz_credentials import (
                        CLIENT_ID, 
                        CLIENT_SECRET,
                        PROFILES, 
                        URLS
                        )


class Authorization(Root):
    """sets authorization & advertising variables """
    def __init__(self, region, **kwargs):
        super().__init__(**kwargs)
        self._region          = region        
        self.RETURN_URL       = URLS['return_url']
        self.CLIENT_ID        = CLIENT_ID
        self.CLIENT_SECRET    = CLIENT_SECRET
        self._auth_code       = ""
        self._access_tkn_dict = {}
        self._access_token    = ""
        self._refresh_token   = PROFILES[region]['refresh_token']
        self._profile_id      = PROFILES[region]['profile_id']
        self._account_id      = PROFILES[region]['account_id']
        self._mktplace_id     = PROFILES[region]['mktplace_id']
        self._mktplace_str_id = PROFILES[region]['mktplace_str_id']        
        self._prefix_acsc     = URLS[region]['access_code']
        self._prefix_auth     = URLS[region]['authorize']
        self._prefix_advt     = URLS[region]['ad']
        
        
    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, new_value):
        self._region = new_value
        return self._region       

    @region.deleter
    def region(self):
        del self._region
        
    @property
    def auth_code(self):
        return self._auth_code

    @auth_code.setter
    def auth_code(self, new_value):
        self._auth_code = new_value
        return self._auth_code        

    @auth_code.deleter
    def auth_code(self):
        del self._auth_code
   
    @property
    def access_tkn_dict(self):
        return self._access_tkn_dict

    @access_tkn_dict.setter
    def access_tkn_dict(self, new_value):
        self._access_tkn_dict = new_value
        return self._access_tkn_dict       

    @access_tkn_dict.deleter
    def access_tkn_dict(self):
        del self._access_tkn_dict
    
    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, new_value):
        self._access_token = new_value
        return self._access_token        

    @access_token.deleter
    def access_token(self):
        del self._access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, new_value):
        self._refresh_token = new_value
        return self._refresh_token       

    @refresh_token.deleter
    def refresh_token(self):
        del self._refresh_token
    
    @property
    def profile_id(self):
        return self._profile_id

    @profile_id.setter
    def profile_id(self, new_value):
        self._profile_id = new_value
        return self._profile_id        

    @profile_id.deleter
    def profile_id(self):
        del self._profile_id
        
    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, new_value):
        self._account_id = new_value
        return self._account_id        

    @account_id.deleter
    def account_id(self):
        del self._account_id
        
    @property
    def mktplace_id(self):
        return self._mktplace_id

    @mktplace_id.setter
    def mktplace_id(self, new_value):
        self._mktplace_id = new_value
        return self._mktplace_id       

    @mktplace_id.deleter
    def mktplace_id(self):
        del self._mktplace_id
        
    @property
    def mktplace_str_id(self):
        return self._mktplace_str_id

    @mktplace_str_id.setter
    def mktplace_str_id(self, new_value):
        self._mktplace_str_id = new_value
        return self._mktplace_str_id  

    @mktplace_str_id.deleter
    def mktplace_str_id(self):
        del self._mktplace_str_id
    
    @property
    def prefix_acsc(self):
        return self._prefix_acsc

    @prefix_acsc.setter
    def prefix_acsc(self, new_value):
        self._prefix_acsc = new_value
        return self._prefix_acsc       

    @prefix_acsc.deleter
    def prefix_acsc(self):
        del self._prefix_acsc
        
    @property
    def prefix_auth(self):
        return self._prefix_auth

    @prefix_auth.setter
    def prefix_auth(self, new_value):
        self._prefix_auth = new_value
        return self._prefix_auth       

    @prefix_auth.deleter
    def prefix_auth(self):
        del self._prefix_auth
    
    @property
    def prefix_advt(self):
        return self._prefix_advt

    @prefix_advt.setter
    def prefix_advt(self, new_value):
        self._prefix_advt = new_value
        return self._prefix_advt       

    @prefix_advt.deleter
    def prefix_advt(self):
        del self._prefix_advt