import boto3
import logging

ssm=boto3.client('ssm')

def check_reponse(response_json):
    try:
        if response_json['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except KeyError:
        return False


def chk_doc(doc_name):
    doc_name_parameter={'key':'Name','value':doc_name}
    response=ssm.list_documents(DocumentFilterList=[doc_name_parameter])
    return response
    if check_reponse(response):
        logging.info("Document list:",response)
        if response['DocumentIdentifiers']:
            logging.info("Document Exist:",response)
            print(response)
        else:
            return False
    else:
        logging.error("Document does not exist:",response)
        return False

#chk_doc('InstallCwAgent')
response=ssm.list_documents()
print(response['DocumentIdentifiers'])

