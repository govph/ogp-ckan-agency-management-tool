import os
import datetime
import time
import urllib
import json
import csv
import random
import logging
# from settings import CHARGE, CURRENCY, CURRENT_URL
from mandrill_email import *
from user_exceptions import *
from settings import LICENSE
from functions import hp, generate_token, create_indexed_tag, uniquify, create_tags
from google.appengine.ext import ndb


# SysLog
class SL(ndb.Model):
    content = ndb.PickleProperty('ct')
    created = ndb.DateTimeProperty('c', auto_now_add=True)
    model_kind = ndb.StringProperty('k')
    parent_entity = ndb.KeyProperty('p')
    # user = ndb.KeyProperty('u')

    def to_api_object(self):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["version_id"] = str(self.key.id())
        data["id"] = str(self.content.key.id())
        # data["type"] = self.content.data_type
        data["username"] = self.content.username or ""
        # if self.content.data_type == "DATASET":
        #     status = self.content.data_api_status
        #     status = status.replace("PENDING", "FOR REVIEW")
        #     status = status.replace("SENTBACK", "SENT BACK")
        #     data["dataset_status"] = status

        # data["user"] = {}

        for key, value in self.content.additional_data.items():
            if key == "file":
                data[key] = {}
                for key2, value2 in value.items():
                    if key2 == "file_url":
                        if self.content.serving_url:
                            data[key][key2] = self.content.serving_url
                        else:
                            data[key][key2] = self.content.file_url
                    else:
                        data[key][key2] = value2
            else:
                data[key] = value

        # if self.user:
        #     user = self.user.get()
        #     if user:
        #         data["user"] = user.to_api_object()
        data["created"] = ""
        if self.created:
            created = self.created
            created += datetime.timedelta(hours=8)
            data["created"] = created.strftime("%b %d, %Y %I:%M:%S %p")
        data["updated"] = ""
        if self.content.updated_time:
            updated = self.content.updated_time
            updated += datetime.timedelta(hours=8)
            data["updated"] = updated.strftime("%b %d, %Y %I:%M:%S %p")
        return data


class SysLog(ndb.Model):
    def _post_put_hook(self, future):
        """
            Automatically creates a version of the APIData model.
        """
        sl = SL(parent=self.key)
        sl.content = self
        sl.model_kind = self.key.kind()
        sl.parent_entity = self.key
        # current_user = global_vars.user
        # if current_user:
        #     sl.user = current_user.key
        sl.put()


class User(ndb.Model):
    first_name = ndb.StringProperty(default="")
    middle_name = ndb.StringProperty(default="")
    last_name = ndb.StringProperty(default="")
    name = ndb.StringProperty(default="")
    mobile_number = ndb.StringProperty(default="")
    original_email = ndb.StringProperty(default="")
    current_email = ndb.StringProperty(default="")
    email_list = ndb.StringProperty(repeated=True)
    password = ndb.StringProperty(default="")
    salutation = ndb.StringProperty()
    designation = ndb.StringProperty()
    department = ndb.StringProperty()
    agency = ndb.StringProperty()
    region = ndb.StringProperty()
    operating_unit = ndb.StringProperty()
    uacs = ndb.StringProperty()
    csrf_token = ndb.StringProperty(default="")
    confirmation_token = ndb.StringProperty()
    password_token = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)
    role = ndb.StringProperty(default="USER")
    status = ndb.StringProperty(default="PENDING")
    permissions = ndb.StringProperty(repeated=True)
    approved_by_name = ndb.StringProperty()
    approved_by_key = ndb.KeyProperty(kind="User")
    approved_on = ndb.DateTimeProperty(default=None)
    disapproved_by_name = ndb.StringProperty()
    disapproved_by_key = ndb.KeyProperty(kind="User")
    disapproved_on = ndb.DateTimeProperty(default=None)
    last_login = ndb.DateTimeProperty()
    password_update = ndb.DateTimeProperty(default=None)
    previous_passwords = ndb.StringProperty(repeated=True)
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)

    def to_object(self, token=None):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["id"] = str(self.key.id())
        data["username"] = ""
        data["first_name"] = self.first_name
        data["middle_name"] = self.middle_name
        data["last_name"] = self.first_name
        data["name"] = " ".join([self.first_name, self.last_name])
        data["mobile_number"] = self.mobile_number
        data["email"] = self.current_email
        data["csrf_token"] = self.csrf_token
        data["active"] = self.active
        data["status"] = self.status
        data["role"] = self.role
        data["salutation"] = self.salutation
        data["designation"] = self.designation
        data["department"] = self.department
        data["agency"] = self.agency
        data["region"] = self.region
        data["operating_unit"] = self.operating_unit
        data["uacs"] = self.uacs
        data["permissions"] = self.permissions
        data["previous_passwords"] = self.previous_passwords

        data["last_login"] = ""
        if self.last_login:
            last_login = self.password_update
            last_login += datetime.timedelta(hours=8)
            data["last_login"] = last_login.strftime("%m/%d/%Y %I:%M:%S %p")

        if token:
            data["token"] = token

        data["password_update"] = ""
        if self.password_update:
            update = self.password_update
            update += datetime.timedelta(hours=8)
            data["password_update"] = update.strftime("%m/%d/%Y %I:%M:%S %p")

        created = self.created_time
        created += datetime.timedelta(hours=8)
        data["created_time"] = created.strftime("%m/%d/%Y %I:%M:%S %p")

        return data

    def to_api_object(self):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["first_name"] = self.first_name
        data["last_name"] = self.first_name
        data["name"] = " ".join([self.first_name, self.last_name])
        data["mobile_number"] = self.mobile_number
        data["email"] = self.current_email

        return data

    def to_approval_object(self):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["id"] = str(self.key.id())
        data["name"] = " ".join([self.first_name, self.last_name])
        data["mobile_number"] = self.mobile_number or "NA"
        data["email"] = self.current_email
        data["department"] = self.department
        data["agency"] = self.agency
        data["region"] = self.region
        data["operating_unit"] = self.operating_unit
        data["uacs"] = self.uacs
        data["approved_on"] = ""
        data["approved_by"] = ""
        data["disapproved_on"] = ""
        data["disapproved_by"] = ""

        if self.status == "APPROVED":
            if self.approved_on:
                approved_on = self.approved_on
                approved_on += datetime.timedelta(hours=8)
                data["approved_on"] = approved_on.strftime("%b %d, %Y %I:%M:%S %p")
                data["approved_by"] = self.approved_by_name
        elif self.status == "DISAPPROVED":
            if self.disapproved_on:
                disapp_on = self.disapproved_on
                disapp_on += datetime.timedelta(hours=8)
                disapp_on = disapp_on.strftime("%b %d, %Y %I:%M:%S %p")
                data["disapproved_on"] = disapp_on
                data["disapproved_by"] = self.disapproved_by_name

        created = self.created_time
        created += datetime.timedelta(hours=8)
        data["registered"] = created.strftime("%b %d, %Y %I:%M:%S %p")

        return data

    @classmethod
    def send_notification_emails(cls, dataset):
        """
            Sends emails to ODTF when a new dataset is created.
        """
        query = cls.query()
        query = query.filter(cls.role == "OPENDATAADMIN")
        ODTF = query.fetch()

        if ODTF:
            for od in ODTF:
                content = {
                    "dataset_title": dataset.additional_data["dataset_title"].upper(),
                    "department": dataset.additional_data["department"].upper(),
                    "dataset_id": str(dataset.key.id())
                }

                send_email(
                    receiver_name=od.first_name,
                    receiver_email=od.current_email,
                    subject="New Dataset Created",
                    content=content,
                    email_type="new_dataset")

    @classmethod
    @ndb.transactional(xg=True)
    def create_new_user(
            cls, first_name, last_name, password, email, role="USER",
            department="", agency="", region="", operating_unit="",
            uacs="", middle_name="", mobile="", designation="",
            salutation="", send=True):
        """
            Creates a new user.
        """
        user = cls()
        user.salutation = salutation
        user.first_name = first_name
        user.last_name = last_name
        user.middle_name = middle_name or ""
        user.name = " ".join([first_name, middle_name or "", last_name])
        user.mobile_number = mobile
        user.original_email = email
        user.current_email = email
        user.email_list = [email]
        user.password = hp(email, password)
        user.previous_passwords = [hp(email, password)]
        # user.department = department
        # user.position = position
        user.confirmation_token = generate_token()

        if uacs:
            user.permissions = ["->".join(["UACS_ID", uacs])]

        if role:
            user.role = role.upper()

        if designation:
            user.designation = designation.upper()

        user.department = department
        user.agency = agency
        user.region = region
        user.operating_unit = operating_unit
        user.uacs = uacs

        user.put()

        if send:
            content = {
                "token": user.confirmation_token,
                "uid": str(user.key.id())
            }

            send_email(
                receiver_name=user.first_name,
                receiver_email=user.current_email,
                subject="Email Verfication",
                content=content,
                email_type="verify")

        return user

    @classmethod
    @ndb.transactional(xg=True)
    def invite_new_opendata_admin(
            cls, email):
        """
            Creates a new ODTF member.
            Sends invitation to join CKAN Manager via Email.
        """
        user = cls()
        user.original_email = email
        user.current_email = email
        user.email_list = [email]
        user.confirmation_token = generate_token()
        user.role = "OPENDATAADMIN"
        user.status = "INVITE"
        user.put()

        content = {
            "token": user.confirmation_token,
            "uid": str(user.key.id())
        }

        send_email(
            receiver_name="OPEN DATA ADMIN",
            receiver_email=user.current_email,
            subject="Open Data Admin Invitation",
            content=content,
            email_type="invite_opendata_admin")

        return user

    @classmethod
    @ndb.transactional(xg=True)
    def complete_opendata_admin_registration(
            cls, user, first_name, last_name,
            password, mobile=""):
        """
            Saves the Agency Admin account details.
        """
        user = user.get()
        user.first_name = first_name
        user.last_name = last_name
        user.name = " ".join([first_name, last_name])
        user.mobile_number = mobile
        user.password = hp(user.current_email, password)
        user.previous_passwords = [hp(user.current_email, password)]
        user.role = "OPENDATAADMIN"
        user.status = "APPROVED"
        user.put()

        # if send:
        #     content = {
        #         "token": user.confirmation_token,
        #         "uid": str(user.key.id())
        #     }

        #     send_email(
        #         receiver_name="OPEN DATA ADMIN",
        #         receiver_email=user.current_email,
        #         subject="Open Data Admin Invitation",
        #         content=content,
        #         email_type="invite_opendata_admin")

        return user

    @classmethod
    def check_user(cls, email):
        """
            Checks if user is already registered.
        """
        query = cls.query()
        query = query.filter(cls.original_email == email)
        user = query.get()

        if user:
            return user

        return False


class APIData(SysLog):
    additional_data = ndb.JsonProperty()
    indexed_data = ndb.StringProperty(repeated=True)
    serving_url = ndb.StringProperty()
    gcs_key = ndb.BlobKeyProperty()
    file_url = ndb.StringProperty()
    user = ndb.KeyProperty()
    username = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    # data_api_status = ndb.StringProperty(default="PENDING")
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)

    def get_all_resource(self):
        """
            Returns all resources of the dataset.
        """
        query = APIData.query()
        query = query.filter(APIData.indexed_data == "TYPE->RESOURCE")
        query = query.filter(APIData.indexed_data == "DATASET_ID->" + str(self.key.id()))

        resources = query.fetch()
        resource_dict = []

        # if resources:
        #     for r in resources:
        #         resource_dict.append(r.to_api_object())

        return resources

    def get_all_versions(self):
        """
            Returns all the versions of the dataset or resource.
        """
        query = SL.query()
        query = query.filter(SL.parent_entity == self.key)
        query = query.order(-SL.created)
        versions = query.fetch()
        versions_object = []
        if versions:
            counter = 0
            first = True

            for version in versions:
                counter += 1

            for version in versions:
                ver = {}
                ver["id"] = str(version.key.id())
                ver["parent_key"] = str(version.parent_entity.id())
                ver["version"] = counter
                ver["name"] = "Version " + str(counter)
                ver["data"] = version.to_api_object()
                if first:
                    ver["current_version"] = True
                else:
                    ver["current_version"] = False
                versions_object.append(ver)
                counter -= 1
                first = False
        else:
            current_version = {}
            current_version["version"] = "1"
            current_version["name"] = "Version 1"
            current_version["data"] = self.to_api_object()
            versions_object.append(current_version)

        return versions_object

    def to_object(self):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["id"] = str(self.key.id())
        # data["type"] = self.data_type
        data["username"] = self.username or ""
        data["additional_data"] = self.additional_data
        data["indexed_data"] = self.indexed_data
        data["serving_url"] = self.serving_url
        # data["user"] = {}
        # if self.user:
        #     user = self.user.get()
        #     if user:
        #         data["user"] = user.to_object()

        return data

    def to_api_object(self):
        """
            Converts the entity to JSON.
        """
        data = {}
        data["id"] = str(self.key.id())
        # data["type"] = self.data_type
        data["username"] = self.username or ""
        # if self.data_type == "DATASET":
        #     status = self.data_api_status
        #     status = status.replace("PENDING", "FOR REVIEW")
        #     status = status.replace("SENTBACK", "SENT BACK")
        #     data["dataset_status"] = status

        # data["user"] = {}

        for key, value in self.additional_data.items():
            if key == "file":
                data[key] = {}
                for key2, value2 in value.items():
                    if key2 == "file_url":
                        if self.serving_url:
                            data[key][key2] = self.serving_url
                        else:
                            data[key][key2] = self.file_url
                    else:
                        data[key][key2] = value2
            else:
                data[key] = value

        # if self.user:
        #     user = self.user.get()
        #     if user:
        #         data["user"] = user.to_api_object()
        data["created"] = ""
        if self.created_time:
            created = self.created_time
            created += datetime.timedelta(hours=8)
            data["created"] = created.strftime("%b %d, %Y %I:%M:%S %p")
        data["updated"] = ""
        if self.updated_time:
            updated = self.updated_time
            updated += datetime.timedelta(hours=8)
            data["updated"] = updated.strftime("%b %d, %Y %I:%M:%S %p")
        return data

    @classmethod
    def check_dataset_exist(cls, dataset_name):
        """
            Checks if dataset already exists.
        """
        tag = create_indexed_tag("DATASET_CKAN_NAME", dataset_name)
        query = cls.query()
        query = query.filter(cls.indexed_data == tag)
        dataset = query.get()

        if dataset:
            return True

        return False

    @classmethod
    def create_initial_dataset(cls, dataset_name, dataset_desc, category,
                        department, uacs, user, license_id, odi=""):
        """
            Creates a new dataset.
        """
        dataset_ckan_name = dataset_name.lower().strip().replace(" ", "-")
        if cls.check_dataset_exist(dataset_ckan_name):
            raise DatasetExistsError(dataset_name)

        dataset = APIData()
        dataset.additional_data = {}
        dataset.additional_data["private"] = False
        dataset.additional_data["type"] = "DATASET"
        dataset.additional_data["status"] = "FOR REVIEW"
        dataset.additional_data["user_id"] = str(user.key.id())
        dataset.additional_data["dataset_title"] = dataset_name
        dataset.additional_data["dataset_description"] = dataset_desc
        dataset.additional_data["dataset_category"] = category
        dataset.additional_data["dataset_ckan_name"] = dataset_ckan_name
        dataset.additional_data["department"] = department
        dataset.additional_data["uacs_id"] = uacs
        dataset.additional_data["odi_certificate"] = odi

        for l in LICENSE:
            if l["code"] == license_id.lower():
                dataset.additional_data["license_id"] = license_id
                dataset.additional_data["license_title"] = l["name"]
                break

        tag = create_indexed_tag("type", "DATASET")
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("status", "FOR REVIEW")
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("user_id", str(user.key.id()))
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("dataset_ckan_name", dataset_ckan_name)
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("uacs_id", uacs)
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("department", department)
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("dataset_title", dataset_name)
        dataset.indexed_data.append(tag)
        tag = create_indexed_tag("dataset_category", category)
        dataset.indexed_data.append(tag)

        dataset.username = user.name
        dataset.user = user.key

        dataset.tags = create_tags(dataset_name)
        dataset.tags += create_tags(department)

        dataset.put()

        return dataset

    @classmethod
    def add_additional_info_dataset(cls, dataset_id, additional_info):
        """
            Updates the additional info of the dataset.
        """
        dataset = cls.get_by_id(int(dataset_id))
        if not dataset:
            return

        logging.error(additional_info)
        for key, value in additional_info.items():
            dataset.additional_data[key.lower()] = value
            if value:
                tag = create_indexed_tag(key, value)
                dataset.indexed_data.append(tag)

        dataset.indexed_data = uniquify(dataset.indexed_data)
        dataset.put()

        return dataset


class Logs(SysLog):
    user = ndb.KeyProperty(kind="User")
    dataset = ndb.KeyProperty(kind="APIData")
    resource = ndb.KeyProperty(kind="APIData")
    uacs_id = ndb.StringProperty()
    data = ndb.JsonProperty()
    # tags = ndb.StringProperty(repeated=True)
    ip_address = ndb.StringProperty(default=os.environ.get('REMOTE_ADDR'))
    user_agent = ndb.StringProperty(default=os.environ.get('HTTP_USER_AGENT'))
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    created_date = ndb.DateProperty(auto_now_add=True)

    @classmethod
    def add_log(cls, data, uacs_id, user=None, dataset=None, resource=None):
        """
            Creates a new activity log.
        """
        log = cls()
        if user:
            log.user = user

        if dataset:
            log.dataset = dataset

        if resource:
            log.resource

        if uacs_id:
            log.uacs_id = uacs_id

        log.data = data
        log.put()

    def to_object(self):
        """
            Converts log entity to JSON.
        """
        data = {}
        data["dataset"] = ""
        if self.dataset:
            data["dataset"] = self.dataset.urlsafe()
        data["action"] = self.data["action"]
        data["icon"] = self.data["icon"]
        data["color"] = self.data["color"]
        created = self.created_time
        created += datetime.timedelta(hours=8)
        data["created_time"] = created.strftime("%b %d, %Y %I:%M:%S %p")
        data["created_time_timeago"] = created.strftime("%Y-%m-%dT%H:%M:%SZ")
        return data


class LoginCode(SysLog):
    login_code = ndb.StringProperty()
    session = ndb.KeyProperty(kind="Session")
    expiry = ndb.DateTimeProperty()
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)


class Nonce(SysLog):
    nonce = ndb.StringProperty()
    timestamp = ndb.IntegerProperty()


class Token(SysLog):
    token = ndb.StringProperty()
    session = ndb.KeyProperty(kind="Session")
    token_type = ndb.StringProperty()


class Session(ndb.Model):
    owner = ndb.KeyProperty(kind='User')
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    ip_address = ndb.StringProperty()
    user_agent = ndb.TextProperty()
    status = ndb.BooleanProperty(default=True)
    data = ndb.JsonProperty()
    expires = ndb.DateTimeProperty()
