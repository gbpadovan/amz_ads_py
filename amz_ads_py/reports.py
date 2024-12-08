#python 3.11.15
import os
from datetime import datetime, UTC, timedelta
#used in class ReportsAsync
import json
import aiohttp
import asyncio
import shutil
import time
from typing import Optional, Union, Dict, Any
from urllib.parse import urljoin
from tqdm import tqdm
#
from .root import Root
from .connect import Connect
from .db import ReportDatabase
from .utils import (
        is_valid_month_string, 
        verify_and_create_directory, 
        get_first_and_last_days_of_month
)
from .metrics import (
        CAMPAING_METRICS, 
        CAMP_GROUP_CAMP,
        CAMP_GROUP_ADG,
        TARGETING_METRICS, 
        METRICS
)


class Debug(Root):
    """This class stores objects from various requests,
    to investigate if the requests are going well"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._resp_step1 = None
        self._resp_step2 = None      

    @property
    def resp_step1(self):
        return self._resp_step1

    @resp_step1.setter
    def resp_step1(self, new_value):
        self._resp_step1  = new_value
        return self._resp_step1

    @resp_step1.deleter
    def resp_step1(self):
        del self._resp_step1
    
    @property
    def resp_step2(self):
        return self._resp_step2

    @resp_step2.setter
    def resp_step2(self, new_value):
        self._resp_step2 = new_value
        return self._resp_step2

    @resp_step2.deleter
    def resp_step2(self):
        del self._resp_step2


###################################################################################
class Reports(Connect, Debug, Metadata):
    """Generates data & routines to create/wait/download reports 
    using Amazon REST API & custom code"""
    def __init__(self, region, **kwargs):
        super().__init__(region=region, **kwargs)
        self.db = ReportDatabase()

    def create_msg(
        self, 
        region:str, 
        report_type_id:str, 
        date:str,
        time_unit:str,
        group_by:str
        ) -> str:
        """Generates a, informative message to be displayed while requesting
        the reports.
        
        Args:
            region (str): Region which the report represents
            report_type_id (str): Unique identifier for report type
            date (str): Date for the report in 'YYYY-MM-DD' format            
            time_unit (str): Time unit for the report            
            group_by (str): Group results by a specific attribute
            
        Returns:
            m (str): informative message        
        """
        m = f"Region: {region} | Report Type: {report_type_id} | Date: {date} | "+\
            f"TimeUnit: {time_unit} | Group by: {group_by}"        
        return m
      

    def create_filter(self, field:str, values:list) -> dict:
        """The filter will be the key filter
    
        Parameters:
            field (str): The field to filter on
            values (list): The values to filter with
        
        Returns:
            dict: The filter dictionary
        """
        filter_dict = {
            "filters": [
                {
                    "field":field,
                    "values":values,
                }
            ],        
        }
        return filter_dict


    def create_report_body(
        self,
        report_type_id:str,
        start_date:str,               
        end_date:str,
        time_unit:str,
        metrics:list,        
        group_by:Union[str, list],
        filter_field:Optional[dict]= None
        ) -> str:
        """Creates the data to post in the report api.

        Parameters:
            start_date (str): fmt %Y-%m-%d
            end_date (str): fmt %Y-%m-%d
            group_by (str or list): representing the groupby
            metrics (list): list with the advertising metrics for this report
            report_type_id (str): unique report id fmt %Y-%m-%d
            time_unit (str): fmt %Y-%m-%d
            filter_field (dict or None):

        Returns:
            raw_data (str): representing a json
        ========================================================================
        NOTE:
            timeUnit and supported columns
            timeUnit can be set to DAILY or SUMMARY. If you set timeUnit to DAILY, 
            you should include date in your column list. If you set timeUnit to 
            SUMMARY you can include startDate and endDate in your column list.        
        """
        try:
            assert time_unit in ["DAILY","SUMMARY"]
        except:
            raise ValueError(f"The timeUnit: {time_unit} does not correspond to 'DAILY' or 'SUMMARY'. Verify if there are any typos or different values." )
            
        if time_unit == "DAILY":            
            metrics   = metrics.copy() + ['date']            
        
        if time_unit == "SUMMARY":            
            metrics   = metrics.copy() + ['startDate','endDate']            
        
        if isinstance(group_by,str):
            group_by = [group_by]
    
        grp_by = {"groupBy": [f"{group}" for group in group_by]}        
        
        raw_data = {
            "name":f"SP {report_type_id} report {start_date}_{end_date}",
            "startDate":f"{start_date}",
            "endDate":f"{end_date}",
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                #"groupBy": [
                #    f"{group_by}" 
                #],
                "columns": metrics,
                "reportTypeId": f"{report_type_id}",
                "timeUnit": f"{time_unit}",
                "format": "GZIP_JSON" # CONSTANT
            }
        }
        
        raw_data['configuration'].update(grp_by)
        
        if isinstance(filter_field, dict):
            raw_data['configuration'].update(filter_field)
        
        return json.dumps(raw_data)
    
        
    async def generate_report(self, data_payload: str, info_msg: str = "") -> Optional[str]:  
        """STEP 1- Generates repost document in the Amazon Cloud

        Args:
            data_payload (str): json like string serving as payload in a request
            info_msg (str): message containing information about the reports, such as region, date, report type, etc.
            
        Returns:
            report_id (str): The report_id

        Note:        
            Equivalent cURL example:
        ```
        curl --location --request POST 'https://advertising-api.amazon.com/reporting/reports' \
            --header 'Content-Type: application/vnd.createasyncreportrequest.v3+json' \
            --header 'Amazon-Advertising-API-ClientId: amzn1.application-oa2-client.xxxxxxxxxx' \
            --header 'Amazon-Advertising-API-Scope: xxxxxxxxxx' \
            --header 'Authorization: Bearer Atza|xxxxxx' \
            --data-raw '{
                "name":"SP campaigns report 7/5-7/10",
                "startDate":"2022-07-05",
                "endDate":"2022-07-10",
                "configuration":{
                    "adProduct":"SPONSORED_PRODUCTS",
                    "groupBy":["campaign","adGroup"],
                    "columns":["campaignId","adGroupId","impressions","clicks","cost","purchases1d","purchases7d","purchases14d","purchases30d","startDate","endDate"],
                    "reportTypeId":"spCampaigns",
                    "timeUnit":"SUMMARY",
                    "format":"GZIP_JSON"
                }
            }'       
        ```
        """        
        lst_headers  = ['amz_ad_api_cli_id','authorize',
                        'amz_ad_api_scope','cont_rep_json_v3']
        self.URL = urljoin(self.prefix_advt, '/reporting/reports')
        self.HEADERS = self._set_header_payload(
                                    list_of_keys=lst_headers, 
                                    kind='headers', 
                                    return_as='dict')
               
        self.DATA = data_payload
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.URL, headers=self.HEADERS, data=self.DATA) as response:
                self.resp_step1 = await response.json()  # Debug.method
                
                if response.status == 200:                    
                    report_data = await response.json()
                    report_id = report_data.get('reportId')
                    
                    # Store report information in database with API response data
                    payload = json.loads(data_payload)
                    await self.db.add_report({
                        'report_id': report_id,
                        'profile_id': self.profile_id,
                        'record_type': payload.get('configuration', {}).get('recordType'),
                        'report_name': payload.get('name'),
                        'start_date': payload.get('startDate'),
                        'end_date': payload.get('endDate'),
                        'time_unit': payload.get('configuration', {}).get('timeUnit'),
                        'format': payload.get('configuration', {}).get('format', 'GZIP_JSON'),
                        'status': 'PENDING',
                        'created_time': datetime.now(UTC).isoformat(),
                        'last_updated_time': datetime.now(UTC).isoformat(),
                        'configuration': payload.get('configuration'),
                        'metrics': payload.get('configuration', {}).get('columns'),
                        'filters': payload.get('configuration', {}).get('filters'),
                        'request_time': datetime.now(UTC).isoformat(),
                        'api_request_id': response.headers.get('x-amz-requestid'),
                        'api_timestamp': response.headers.get('x-amz-date'),
                        'api_status_code': response.status
                    })
                    
                    print(f"Step 1 concluded.{info_msg}")
                    return report_id
                else:
                    error_msg = f"Expected response.status == 200.\nResponse:{self.resp_step1}"
                    error_msg2= f"\nurl:{self.URL}\nheaders:{self.HEADERS}\ndata:{self.DATA}"
                    await self.db.add_report({
                        'status': 'FAILED',
                        'error_message': error_msg + error_msg2,
                        'api_status_code': response.status,
                        'api_request_id': response.headers.get('x-amz-requestid'),
                        'api_timestamp': response.headers.get('x-amz-date')
                    })
                    raise RuntimeError(error_msg+error_msg2)

    async def check_report_status(
            self,
            report_id: str,
            retries: int = 25,
            backoff_factor: float = 1,
            limit_wait: int = 32,
            info_msg: str = ""
    ) -> Optional[str]:
        """
        STEP 2- Check the status of a report and retrieve its download URL if it's completed.
    
        Args:
            report_id (str): The ID of the report to check.
            retries (int): The number of retries to attempt before giving up.
            backoff_factor (float): The factor to use for exponential backoff between retries.
            limit_wait (int): max number of sec. tolerated to asyncio.wait inside the function
            info_msg (str): message containing information about the reports
    
        Returns:
            download_url (str): The download URL for the completed report
        """
        for attempt in range(retries):
            lst_headers = ['amz_ad_api_cli_id', 'authorize', 
                           'amz_ad_api_scope', 'cont_rep_json_v3']
            self.URL = urljoin(self.prefix_advt, f'/reporting/reports/{report_id}')
            self.HEADERS = self._set_header_payload(
                                        list_of_keys=lst_headers, 
                                        kind='headers', 
                                        return_as='dict')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.URL, headers=self.HEADERS) as response:
                    self.resp_step2 = await response.json() # Debug.method
                    
                    if response.status == 200:
                        report_data = await response.json()
                        status = report_data.get('status')
                        
                        # Update database with latest status
                        await self.db.update_report_status(
                            report_id=report_id,
                            status=status,
                            response_data={
                                'status': status,
                                'status_details': report_data.get('statusDetails'),
                                'last_updated_time': datetime.now(UTC).isoformat(),
                                'url': report_data.get('url'),
                                'file_size_bytes': report_data.get('fileSize'),
                                'api_request_id': response.headers.get('x-amz-requestid'),
                                'api_timestamp': response.headers.get('x-amz-date'),
                                'api_status_code': response.status
                            }
                        )
                        
                        if status == 'COMPLETED':
                            download_url = report_data.get('url')
                            print(f"Step 2 concluded.{info_msg}")
                            return download_url
                        elif status in ['FAILED', 'CANCELLED']:
                            error_message = report_data.get('statusDetails', 'Report generation failed')
                            raise Exception(f"Report generation failed: {error_message}")
                    
                    # Backoff logic
                    wait_time = min(backoff_factor * (2 ** attempt), limit_wait)
                    for _ in tqdm(range(wait_time), desc=f"Attempt#{attempt}. Waiting {wait_time}s.{info_msg}"):
                        await asyncio.sleep(1)
        
        error_message = f"Report generation timed out after {retries} attempts"
        await self.db.update_report_status(
            report_id=report_id,
            status='FAILED',
            error_message=error_message
        )
        raise Exception(error_message)

    async def download_compressed_file(
            self,
            url: str,
            path: Union[str, os.PathLike],
            info_msg: str = "",
            report_id: Optional[str] = None
    ) -> None:
        try:
            lst_headers = ['amz_ad_api_cli_id', 'authorize', 
                           'amz_ad_api_scope', 'cont_rep_json_v3']
            self.URL = url
            self.HEADERS = self._set_header_payload(
                                        list_of_keys=lst_headers, 
                                        kind='headers', 
                                        return_as='dict')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.URL, headers=self.HEADERS) as response:
                    response.raise_for_status()
                    
                    local_filename = path + ".gz"
                    with open(local_filename, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    if report_id:
                        await self.db.update_report_status(
                            report_id=report_id,
                            status='DOWNLOADED',
                            response_data={
                                'location': local_filename,
                                'download_time': datetime.now(UTC).isoformat(),
                                'api_request_id': response.headers.get('x-amz-requestid'),
                                'api_timestamp': response.headers.get('x-amz-date'),
                                'api_status_code': response.status
                            }
                        )
                    
                    print(f"Step 3 concluded.{info_msg} Downloaded {local_filename}")
        except Exception as e:
            if report_id:
                await self.db.update_report_status(
                    report_id=report_id,
                    status='FAILED',
                    error_message=f"Download failed: {str(e)}"
                )
            raise

    async def fetch_report(
        self,
        report_type_id:str,
        date:str,
        time_unit:str,
        group_by:Union[str, list],
        metrics:list,
        filter_field:Optional[dict],
        month:Optional[str]
        )-> None:
        """Retrieves one report by following all the necessary steps:
            STEP 1 - POST report
            STEP 2 - GET report status & url
            STEP 3 - GET download report
        
        Args:
            report_type_id (str): Unique identifier for report type
            date (str): Date for the report in 'YYYY-MM-DD' format            
            time_unit (str): Time unit for the report            
            group_by (str): Group results by a specific attribute
            metrics:list,
            filter_field
            month Optional[str]: Month to retrieve if monthly periodicity is selected, in 'YYYY-MM' format

        Returns:
            None
        """
        if month:
            start_date, end_date = get_first_and_last_days_of_month(month)  #from utils.py
            peridiocity = "monthly"
        else:
            start_date, end_date = date, date # it will be the same day
            peridiocity = "daily"
        
        body = self.create_report_body(
                        start_date=start_date,
                        end_date=end_date,          
                        group_by=group_by,
                        metrics=metrics,
                        report_type_id=report_type_id,
                        time_unit=time_unit,
                        filter_field=filter_field)
        
        self.fetch_access_tkn(method='refresh')

        msg = self.create_msg(self.region, report_type_id, date, time_unit, group_by)     
        
        #### STEP 1 - GENERATING REPORT
        report_id = await self.generate_report(data_payload=body,info_msg=msg)

        #### STEP 2 - CHECKING REPORT STATUS
        download_url = await self.check_report_status(report_id=report_id,info_msg=msg)

        #### STEP 3 - DOWNLOADING REPORT FILE
        # group_by can be a str, list
        if isinstance(group_by, list):
            group_by = "_".join(group_by)        
        
        folder_path = os.path.join(
                        os.getcwd(),
                        'reports',
                        f'{self.region}',
                        f'{report_type_id}',
                        f'{peridiocity}',
                        f'{time_unit}',
                        f'{group_by}',
                        )
        verify_and_create_directory(directory_path=folder_path)
        #
        file_name = f"{start_date}_{end_date}_{report_type_id}" 
        full_path = os.path.join(folder_path,file_name)            
        await self.download_compressed_file(url=download_url, path=full_path,info_msg=msg, report_id=report_id)
        return

    
    async def retrieve_reports_async(
        self,
        report_type_id:str,
        start_date:str, 
        end_date:str,
        time_unit:str,
        month:Optional[str],
        group_by:str
        )->None:
        """
        Retrieves reports according to date range or monthly periodicity.
        
        Args:
            report_type_id (str): Unique identifier for report type
            start_date (str): Start date for the report in 'YYYY-MM-DD' format
            end_date (str): End date for the report in 'YYYY-MM-DD' format
            time_unit (str): Time unit for the report
            month Optional[str]: Month to retrieve if monthly periodicity is selected, in 'YYYY-MM' format
            group_by (str): Group results by a specific attribute

        Returns:
            None        
        """        
        # TODO: change this function to work with other reports
        # Avaiable report_types:
        # report_types = ['spCampaigns','spTargeting']
        try:
            assert report_type_id in ['spCampaigns','spTargeting']
        except:
            raise ValueError(f"The report_type_id: {report_type_id} does not correspond to 'spCampaigns' or 'spTargeting'. Verify if there are any typos or different values." )
        
        
        if report_type_id == 'spCampaigns':          
            metrics = CAMPAING_METRICS.copy() + METRICS.copy()            
            
            if group_by == 'default':
                group_by = ["campaign","adGroup"]
                dict_filter = None               
                metrics = metrics.copy()+CAMP_GROUP_CAMP.copy()+CAMP_GROUP_ADG.copy()
                # it has to remove this, otherwise we have reponse error
                metrics.remove('topOfSearchImpressionShare')
            
            else:
                try:
                    assert group_by in ['campaign','adGroup']
                except:
                    raise ValueError(f"Group by {grouper} is not supported by this {report_type_id}")
                    
                if group_by == 'campaign':                    
                    filter_field = "campaignStatus"
                    metrics = metrics.copy() + CAMP_GROUP_CAMP.copy() # add metricsspecific to campaign
                      
                if group_by == 'adGroup':
                    filter_field = "adStatus"
                    metrics = metrics.copy() + CAMP_GROUP_ADG.copy() # add metricsspecific to adGroups
            
                filter_values = ["ENABLED","PAUSED","ARCHIVED"]
                #        
                dict_filter = self.create_filter(
                                    field=filter_field, 
                                    values=filter_values)
            
        if report_type_id == 'spTargeting':        
            group_by = 'targeting' #default
            metrics = TARGETING_METRICS.copy() + METRICS.copy()
            #
            filter_field = "keywordType"
            filter_values = ["BROAD","PHRASE","EXACT"]
            #        
            dict_filter = self.create_filter(
                                field=filter_field, 
                                values=filter_values)        
        
        # =====================X===========X========================#
        tasks = []
        async with aiohttp.ClientSession() as session:
            
            if month is not None:                
                is_valid_month_string(month) #from utils.py
                print("This will be a 'monthly report'")
                # the day does't matter,
                # start_date & end_date will be defined in the fetch_report method                
                date = month + "-01"  
                #
                task = asyncio.create_task(
                    # my async function
                    #######################################                    
                        self.fetch_report(
                            report_type_id=report_type_id,
                            date=date,
                            time_unit=time_unit,
                            group_by=group_by,
                            metrics=metrics,
                            filter_field=dict_filter,
                            month=month
                        ) # ends fetch_report
                    #######################################
                    ) # ends create_task
                
                tasks.append(task)      
           
            else:
                # this will be a day-by-day report, according to date range 
                for date in pd.date_range(start_date, end_date).astype(str):
                             
                    task = asyncio.create_task(
                    # my async function
                    #######################################                    
                        self.fetch_report(
                            report_type_id=report_type_id,
                            date=date,
                            time_unit=time_unit,
                            group_by=group_by,
                            metrics=metrics,
                            filter_field=dict_filter,
                            month=month
                        )
                    #######################################
                    )
                    tasks.append(task)
    
            await asyncio.gather(*tasks)