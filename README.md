# User Guides and Features


User Guides and Features: https://govph.github.io/ckan-agency-management-tool/


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

