#python 3.11.15
import asyncio
from typing import Optional
from .reports import Reports


class Amzapi(Reports):
    """This class helps to organize code to generate automated
    routines to retrieve many kinds of reports"""
    def __init__(self, region,**kwargs):
        super().__init__(region=region, **kwargs)  
        
        
    def retrieve_reports(
        self, 
        report_type_id:str, 
        start_date:str, 
        end_date:str,
        time_unit:str='SUMMARY',
        month:Optional[str]=None,
        group_by:str='default'
        )->None:
        """Retrieves reports according to date range or monthly periodicity.
        
        Args:
            report_type_id (str): Unique identifier for report type
            start_date (str): Start date for the report in 'YYYY-MM-DD' format
            end_date (str): End date for the report in 'YYYY-MM-DD' format
            time_unit (str): Time unit for the report (default: 'SUMMARY')
            month Optional[str]: Month to retrieve if monthly periodicity is selected, in 'YYYY-MM' format
            group_by (str): Group results by a specific attribute (default: 'default')

        Returns:
            None
        """
        asyncio.run(
            self.retrieve_reports_async(
                report_type_id=report_type_id, 
                start_date=start_date, 
                end_date=end_date,
                time_unit=time_unit,
                month=month,
                group_by=group_by
            )
        )
        return