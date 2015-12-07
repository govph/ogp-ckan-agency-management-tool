# User Guides and Features


User Guides and Features: https://govph.github.io/ogp-ckan-agency-management-tool/


---


# Developer Documentation


## Setting up the Tool


This tool is built to run on the Google AppEngine Platform. To learn more about Google AppEngine, visit: https://cloud.google.com/appengine/

This tool interacts with CKAN using the CKAN API. To learn more about CKAN and the CKAN API, visit the following links:

* http://ckan.org/
* http://docs.ckan.org/en/latest/api/index.html



## Settings and Configuration

Open `settings.py` and configure the variables. Important variables:
* `MANDRILL_API_KEY` - for sending email via Mandrill
* `MANDRILL_SENDER` - the email sender
* `CKAN_API_KEY` - the CKAN API Key of the user account registered in your CKAN instance.



## Deploying the Tool to AppEngine

Read the getting started guide of AppEngine. You may also skip to the last part that focuses on deployment:

https://cloud.google.com/appengine/docs/python/gettingstartedpython27/introduction


---


# About Open Data Philippines

As one of the eight founding states of the Open Government Partnership, the [Philippine government][1] is committed to open governance through initiatives such as this.

Data.gov.ph aims to make national government data searchable, accessible, and useful, with the help of the different agencies of government, and with the participation of the public.

The primary goal of data.gov.ph is to foster a citizenry empowered to make informed decisions, and to promote efficiency and transparency in government.

Learn more about [Open Data PH][2] and our [data policy statement][3].

[1]: http://www.gov.ph/
[2]: http://data.gov.ph/about
[3]: http://data.gov.ph/about/data-policy-statement