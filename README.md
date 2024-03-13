# AMAZON ADS PY

* Author: Gustavo B. Padovan
* Last update: 2024-03-13
* Python version: 3.11.15
* Watch this program working here: https://www.youtube.com/watch?v=bjMvQax7AM0

## Introduction:

* This module generates and downloads reports on advertising campaigns on the Amazon Platform.
* Utilizes a custom solution to interact with Amazon REST API V3.

## Configure `.env` file:

* IMPORTANT: YOU MUST FOLLOW THE ONBOARDING STEPS BEFORE YOU CAN USE THIS PYTHON APP!
    * https://advertising.amazon.com/API/docs/en-us/guides/onboarding/overview
* Set `RETURN_URL`, `CLIENT_ID`, `CLIENT_SECRET`, `PROFILE_ID` & `REFRESH_TOKEN` in the `.env` file,
* (Optional) - for future implementation: `MKTPLACE_ID`, `MKTPLACE_STR_ID`,
* For any other additional marketplace, follow the same pattern as 'USA' below

```env
# This is a model for the .env file
# OAuth2 Credentials:
export RETURN_URL="https://www.yoururl.com/"
export CLIENT_ID="amzn1.application-oa2-client.XXXXXXXXXXXX"
export CLIENT_SECRET="XXXXXXXXXX"

# Advertising credentials:
# credentials usa account
export USA_PROFILE_ID=123456789
export USA_ACCOUNT_ID="A123456789"
export USA_MKTPLACE_ID="ENTITY123456789"
export USA_MKTPLACE_STR_ID="XXXXXXXXXXXX"
export USA_REFRESH_TOKEN="Atzr|XXXXX123456789XXXXXX"

# Follow the same pattern for accounts in other markets
```

## How to use:

*  Adjust desired dates and markets in `collect_reports.py`.
    * avaiable markets: 'usa','uk','ca' and 'au'.
*  Run `collect_reports.py`.

```bash
$ python collect_reports.py
```

## Reports Avaiable:

### spTargeting
* Available `timeUnits`: 'SUMMARY' and 'DAILY'.
* Available `groupBy`: "campaign", "adGroup", and ["campaign","adGroup"].
* Monthly: Covers from the first to the last day of the month.

### spCampaigns
* Available `timeUnits`: 'SUMMARY' and 'DAILY'.
* Monthly: Covers from the first to the last day of the month.

**NOTE**:

* Additional reports supported by Amazon REST API will be added in future versions.
* Reports downloaded and saved at the `reports/` folder.
    
## Project Structure:

```
📁 amz_ads_api
 |_ 📁 amz_ads_api
    |_ 📄 __init__.py
    |_ 📄 amz_credentials.py
    |_ 📄 amzapi.py
    |_ 📄 authorization.py
    |_ 📄 connect.py
    |_ 📄 metrics.py
    |_ 📄 reports.py
    |_ 📄 root.py
    |_ 📄 utils.py
 |_ 📁 examples
 |_ 📁 html
 |_ 📁 metadata
 |_ 📁 reports
 |_ 📄 MANIFEST.in
 |_ 📄 README.md
 |_ 📄 requirements.txt
 |_ 📄 setup.py
 |_ 📄 collect_reports.py
```

## More information:

### Amazon REST Api V3

* https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types/overview