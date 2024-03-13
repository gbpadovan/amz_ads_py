import os
import sys
# Add the parent directory of the amz_ads_api directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from amz_ads_py.amzapi import Amzapi


region = 'usa'

#start_date='2023-12-09'
#end_date='2024-01-01'

start_date='2024-03-01'
end_date='2024-03-03'

#report_type = 'spCampaigns'
report_type = 'spTargeting'

#time_unit = 'SUMMARY'# 'DAILY'
time_unit ="DAILY"

month = None
#month = '2024-02'

group_by='campaign' #only works for spCampaigns
#group_by='adGroup' #only works for spCampaigns
#group_by='default'

def main():	
	api = Amzapi(region=region)

	api.retrieve_reports(
	    report_type_id=report_type,
	    start_date=start_date,
	    end_date=end_date,
	    time_unit=time_unit,
	    month=month,
	    group_by=group_by
	    )
	del api


if __name__=="__main__":
	main()