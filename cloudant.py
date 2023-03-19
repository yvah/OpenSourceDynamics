import ibm_cloud_sdk_core
from ibmcloudant.cloudant_v1 import CloudantV1 as Cloudant
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from time import sleep
import threading

CLOUDANT_URL = "https://e90cf857-4d01-42b7-a5a9-22b66c91c13e-bluemix.cloudantnosqldb.appdomain.cloud"
CLOUDANT_APIKEY = "UN7N-RKZkoI-zwC20g6fwlLQPvOQZf-7g6dKGxU1XJsf"
IAM_auth = IAMAuthenticator(CLOUDANT_APIKEY)

service = Cloudant(authenticator=IAM_auth)
service.set_service_url(CLOUDANT_URL)

temp = 0


# returns true if databaseName exists, else false
def checkDatabases(databaseName):
    databases = service.get_all_dbs().get_result()
    return databaseName in databases


# creates a database with with the passed in name, returns true on success, false otherwise
def createDatabase(name):

    try:
        response = service.put_database(db=name).get_result()
        return response["ok"]
    except ibm_cloud_sdk_core.api_exception.ApiException:
        return False


# function for adding documents to the database
def addDocument(doc, database):

    success = False
    while not success:
        try:
            response = service.put_document(
                db=database,
                doc_id=str(doc["number"]),
                document=doc
            )
            success = response.get_result()["ok"]
        except ibm_cloud_sdk_core.api_exception.ApiException:
            sleep(0.5)
    return True


# helper function to add multiple documents
def addMultipleDocs(documents, database):

    for doc in documents:
        addDocument(doc, database)


# clears the database by deleting and recreating it
def clearDatabase(database):

    try:
        service.delete_database(db=database)
    except ibm_cloud_sdk_core.api_exception.ApiException:
        return False

    return createDatabase(database)
