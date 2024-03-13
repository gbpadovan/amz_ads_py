from amz_ads_py.amzapi import Amzapi


start_date='2024-01-01'
end_date='2024-02-29'

month =None # meaning, there'll be a day-by-day report

def main():
	for region in [
			'usa',
			#'uk',
			#'au',
			#'ca'
			]:

		api = Amzapi(region=region)
		
		for report_type_id in [
					'spTargeting',
					'spCampaigns'
					]:

			for time_unit in [
						'SUMMARY',
						'DAILY'
						]:		

				for group_by in [
						'default',
						'campaign',
						'adGroup'
						]:

					if report_type_id == 'spTargeting' and (group_by == 'campaign' or group_by == 'adGroup'):
						pass
					else:
						api.retrieve_reports(
						    report_type_id=report_type_id,
						    start_date=start_date,
						    end_date=end_date,
						    time_unit=time_unit,
						    month=month,
						    group_by=group_by
						)
		del api

	print("All tasks concluded.")
	return


if __name__=="__main__":
	main()