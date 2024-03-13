#python 3.11.15
import os
import requests
from urllib.parse import urljoin
from typing import Optional, Union
#
from .authorization import Authorization


class Connect(Authorization):
    """Generates HEADERS and DATA payload used in requests.
    Methods are used to get access_token & refresh_token.
    """    
    def __init__(self, region, **kwargs):
        super().__init__(region=region, **kwargs)
        self._URL      = None
        self._HEADERS  = None
        self._DATA     = None
        self._RAW_RESP = None

    @property
    def URL(self):
        return self._URL

    @URL.setter
    def URL(self, new_value):
        self._URL = new_value
        return self._URL       

    @URL.deleter
    def URL(self):
        del self._URL
    
    @property
    def HEADERS(self):
        return self._HEADERS

    @HEADERS.setter
    def HEADERS(self, new_value):
        self._HEADERS = new_value
        return self._HEADERS       

    @HEADERS.deleter
    def HEADERS(self):
        del self._HEADERS

    @property
    def DATA(self):
        return self._DATA

    @DATA.setter
    def DATA(self, new_value):
        self._DATA = new_value
        return self._DATA       

    @DATA.deleter
    def DATA(self):
        del self._DATA

    @property
    def RAW_RESP(self):
        return self._RAW_RESP

    @RAW_RESP.setter
    def RAW_RESP(self, new_value):
        self._RAW_RESP = new_value
        return self._RAW_RESP     

    @RAW_RESP.deleter
    def RAW_RESP(self):
        del self._RAW_RESP
                

    def examine_resp(self, response):
        """examines response"""
        print(f'Status code:{response.status_code}',"\n")
        print(f"raw url: {self.URL}",'\n')
        print(f"headers: {self.HEADERS}",'\n')
        print(f"data content: {self.DATA}",'\n')
        print(f"url full: {response.url}",'\n')
        return


    def _update_headers(self)->dict:
        "Updates header data"
        headers_dict  = {
            'user_agent'        :{"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"},
            'content_url'       :{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}, 
            'cont_rep_json_v3'  :{"Content-Type":"application/vnd.createasyncreportrequest.v3+json"},# V3
            #'content_json_v2'   :{"Content-Type":"application/json"}, # V2, maybe deprecated
            'authorize'         :{"Authorization":f"Bearer {self.access_token}"},
            'amz_ad_api_cli_id' :{"Amazon-Advertising-API-ClientId":f"{self.CLIENT_ID}"},        
            'amz_ad_api_scope'  :{"Amazon-Advertising-API-Scope":f"{self.profile_id}"},
            'accept*/*'         :{"Accept":"*/*"},
            'cache_no_cache'    :{"Cache-Control":"no-cache"},
            'connect_keep_alive':{"Connection":"keep-alive"},
            'host_api_test'     :{"Host":"advertising-api-test.amazon.com"},            
        }        
        return headers_dict
   
    
    def _update_payload(self)->dict:
        "Updates payload data"
        payload_dict ={
            "grant_auth_code":{"grant_type":"authorization_code"},
            "grant_refresh":{"grant_type":"refresh_token"},
            "code":{"code":f"{self.auth_code}"}, # enhireted by Authorization obj, default = ""
            "redirect_uri":{"redirect_uri":f"{self.RETURN_URL}"},
            "client_id":{"client_id":f"{self.CLIENT_ID}"},
            "client_secret":{"client_secret":f"{self.CLIENT_SECRET}"},
            "refresh_token":{"refresh_token":f"{self.refresh_token}"},
            "scope_ads":{"scope":"advertising::campaign_management"},
            "resp_code":{"response_type":"code"},
        }
        return payload_dict


    def _set_header_payload(
        self, 
        list_of_keys:list, 
        kind:str, 
        return_as='dict'
        )-> Union[dict, list[str], str]:
        """Create a either a dictionary or a list or a string
        containing headers or data payload to be used in a request.

        Args:
            list_of_keys (list): List with the keys containing the desired headers
            kind (str): Any stings in ['headers','payload']
            return_as (str): Any strings in ['dict','list','string']. Default = 'dict'
    
        Returns: 
            headers/payload: Union[dict, list[str], str]
            
        Raises:
            AssertionError: if the input is not a list or the kind is not 'headers' or 'payload'
            Exception: if the header/payload is incorrect.
    
        Notes:
            This function is used to create a payload or headers to be used in a request.
            The function takes a list of keys and a kind (headers or payload) as input.
            The function returns a dictionary, list or string containing the headers or payload.
            The function raises an AssertionError if the input is not a list or the kind is not 'headers' or 'payload'.
            The function raises an Exception if the header/payload is incorrect.
        """        
        try:
            assert isinstance(list_of_keys,list)
            assert kind in ['headers','payload']
        except:
            raise Exception("Provide right list or right kind.")        
    
        if kind == 'headers':
            work_dict = self._update_headers()
            separator = ':'
        if kind == 'payload':
            work_dict = self._update_payload()
            separator = '='
        
        new_work_dict = {}
    
        for k in list_of_keys:
            try:
                assert k in work_dict.keys()
                new_work_dict.update(work_dict[k])
            except:
                raise Exception(f"Header/payload {k} is incorrect.")
    
        if return_as == 'dict':
            return new_work_dict    
        else:
            work_as_list =[]
            for key in list(new_work_dict.keys()):            
                work_as_list.append(key + separator + new_work_dict[key])
            # this is used when making request with pycurl, instead of requests
            if return_as == 'list':
                return work_as_list
    
            if return_as == 'string':
                return "&".join(work_as_list)
                
       
    def get_url_auth_code(self):        
        """Gets the url which one can manually login on the amazon to 
        receive the authorization code.
        
        Args:
            
        Returns:
            resp: request.response or resp.url:str

        Read:
            https://advertising.amazon.com/API/docs/en-us/guides/get-started/create-authorization-grant#determine-the-values-for-the-required-query-parameters

        Equivalent request GET:
        ```    
        https://www.amazon.com/ap/oa
            ?client_id=amzn1.application-oa2-client.12345678901234567890
            &scope=advertising::campaign_management
            &response_type=code
            &redirect_uri=https://amazon.com        
        ```
        * Once you obtain the url and login, you'll be redirected.
        * Locate the code inside the url in the browser url panel.
        * THIS CODE ONLY LASTS 5 MINUTES SO YOU'LL HAVE TO GET THE ACCESS TOKEN IN THE MEAN TIME, OTHERWISE REPEAT THIS PROCESS        
        """
        lst_headers  = ['user_agent','content_url']
        lst_payload  = ["client_id","scope_ads","resp_code","redirect_uri"]

        self.URL     = urljoin(self.prefix_acsc,'/ap/oa')    
        self.HEADERS = self._set_header_payload(
                                    list_of_keys=lst_headers, 
                                    kind='headers', 
                                    return_as='dict')    
        
        self.DATA    = self._set_header_payload(
                                list_of_keys=lst_payload, 
                                kind='payload', 
                                return_as='string')
        
        self.RAW_RESP = requests.get(
            url=self.URL,
            headers= self.HEADERS, # must be dict
            params= self.DATA      # must be str
        )      

        if self.RAW_RESP.status_code != 200:
            self.examine_resp(response=self.RAW_RESP)
            return self.RAW_RESP
        else:
            return self.RAW_RESP.url

    
    def fetch_access_tkn(self, method:str, return_tokens:bool=False):        
        """Retrieves access token.
        
        Args:
            method (str): Either 'auth_code' or 'refresh'
            return_token (bool): If True returns self.access_token, False -> None

        Returns:
            self.access_tkn_dict (dict) or None
        
        Equivalent request POST:
        ```     
        curl  \
        -X POST \
        --data "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=YOUR_RETURN_URL&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET_KEY" \
        https://api.amazon.com/auth/o2/token
        ``` 
        """
        assert method in ['auth_code','refresh']
        
        lst_headers  = ['content_url']
        self.URL = urljoin(self.prefix_auth,'/auth/o2/token')
        self.HEADERS = self._set_header_payload(
                                    list_of_keys=lst_headers, 
                                    kind='headers', 
                                    return_as='dict')
        
        if method == 'auth_code':
            lst_payload = ['grant_auth_code','code','redirect_uri',
                           'client_id','client_secret']
            
        if method == 'refresh':
            lst_payload = ['grant_refresh','refresh_token',
                           'client_id','client_secret']
            
        # request.post uses 'dict' as payload in 'data' parameter         
        self.DATA = self._set_header_payload(
                            list_of_keys=lst_payload, 
                            kind='payload', 
                            return_as='dict') # must be a dict
        
        self.RAW_RESP = requests.post(
            url= self.URL, 
            headers=self.HEADERS,
            data=self.DATA
        )

        if self.RAW_RESP.status_code != 200:
            self.examine_resp(response=self.RAW_RESP)            
            return self.RAW_RESP
        else:
            self.access_tkn_dict = self.RAW_RESP.json()
            self.access_token = self.access_tkn_dict['access_token']
            
            if return_tokens:
                return self.access_tkn_dict
            pass
        return