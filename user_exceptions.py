from settings import *


class Error(Exception):
    def __str__(self):
        return str(self.msg)


class DatasetExistsError(Error):
    def __init__(self, name):
        self.name = name
        self.msg = "A similar dataset with title " + str(name).upper() + " already exists."
        self.msg += " Please enter a new title."


class LoginCodeDoesNotExist(Error):
    def __init__(self, code):
        self.name = name
        self.msg = "A similar dataset with title " + str(name).upper() + " already exists."
        self.msg += " Please enter a new title."


class CannotGenerateSignature(Error):
    def __init__(self):
        self.msg = "Cannot generate signature"