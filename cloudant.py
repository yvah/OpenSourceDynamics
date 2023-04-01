import ibm_cloud_sdk_core
from ibmcloudant.cloudant_v1 import CloudantV1 as Cloudant
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from time import sleep
from db import load_json


class Database:
    def __init__(self, credentials_file):
        self.credentials = load_json(credentials_file)
        iam_auth = IAMAuthenticator(self.credentials["apikey"])

        self.service = Cloudant(authenticator=iam_auth)
        self.service.set_service_url(self.credentials["url"])

    # returns true if databaseName exists, else false
    def checkDatabases(self, databaseName):
        databases = self.service.get_all_dbs().get_result()
        return databaseName in databases

    # creates a database with with the passed in name, returns true on success, false otherwise
    def createDatabase(self, name):

        try:
            response = self.service.put_database(db=name).get_result()
            return response["ok"]
        except ibm_cloud_sdk_core.api_exception.ApiException:
            return False

    # function for adding documents to the database
    def addDocument(self, doc, database):

        success = False
        while not success:
            try:
                response = self.service.put_document(
                    db=database,
                    doc_id=str(doc["number"]),
                    document=doc
                )
                success = response.get_result()["ok"]
            except ibm_cloud_sdk_core.api_exception.ApiException:
                sleep(0.5)
        return True

    # helper function to add multiple documents
    def addMultipleDocs(self, documents, database):

        for doc in documents:
            self.addDocument(doc, database)

    # clears the database by deleting and recreating it
    def clearDatabase(self, database):

        try:
            self.service.delete_database(db=database)
        except ibm_cloud_sdk_core.api_exception.ApiException:
            return False

        return self.createDatabase(database)
