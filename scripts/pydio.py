# using django-extentions to run tests from this file under the function run():
# to run the function from the terminal execute the following command
# python manage.py runscript pydio

import http.client
import requests
import json
from rest_framework import status as _status
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from requests.auth import HTTPBasicAuth
from requests_toolbelt import MultipartEncoder
from django.core import serializers
import platform


from django.utils.encoding import smart_str
import os
from io import BytesIO

# import xml.dom.minidom as minidom
from lxml import etree

from . import serializers as _serializers

from pydiosdkpython.remote import PydioSdk







def XMLDeserializerTest():
    """ test XML deserialization """
     # get current directory
    module_dir = os.path.dirname(__file__) 
    file_path = os.path.join(module_dir, 'response.xml')
    #read xml as bytes
    xmldata = open(file_path, "rb").read()
    stream = BytesIO(xmldata)  
    #parse XML
    newData = etree.parse(stream)
    type = newData.find('message').get('type')

    if type is "ERROR":
        return Response(newData.find('message'), status=_status.HTTP_400_BAD_REQUEST)
    
    data = XMLParser().parse(stream)
    serializer = _serializers.ResponseTreeContent(data=data)
    if serializer.is_valid(raise_exception=True):
             
        message = serializer.validated_data.get('message')
        return Response(message, status=_status.HTTP_200_OK)

    return Response(serializer.errors, status=_status.HTTP_400_BAD_REQUEST)


def XMLDeserializer(xmldata):
    """ test XML deserialization """

    stream = BytesIO(xmldata)  
    #parse XML
    newData = etree.parse(stream)
    type = newData.find('message').get('type')

    if type is "ERROR":
        return Response(newData.find('message'), status=_status.HTTP_400_BAD_REQUEST)
    
    data = XMLParser().parse(stream)
    serializer = _serializers.ResponseTreeContent(data=data)
    if serializer.is_valid(raise_exception=True):
             
        message = serializer.validated_data.get('message')
        return Response(message, status=_status.HTTP_200_OK)

    return Response(serializer.errors, status=_status.HTTP_400_BAD_REQUEST)

    

def run():

    print (platform.architecture()[0])

    # TestPydioGeneratePKs()

    # TestPydioSDK()
    # sdk = PydioSdk("http://192.168.20.103:8082/pydio-core-8.0.2/", "my-files", "/", '', auth=('cesar_raynell@hotmail.com', 'Powermaxgp1!'))
    # print(sdk.list[0])


# def run():
#     url = "http://192.168.20.103:8082/pydio-core-8.0.2/api/v2/admin/workspaces?format=json"

#     _json = {
#         "display": "bim-project-2",
#         "accessType": "fs",
#         "isTemplate": False,
#         "parameters": {
#         "PATH": "AJXP_DATA_PATH/workspaces/cesar_raynell@hotmail.com/bim-project-2",
#         "CREATE": True,
#         "RECYCLE_BIN": "recycle_bin",
#         "CHMOD_VALUE": "0600",
#         "DEFAULT_RIGHTS": "rw",
#         "PAGINATION_THRESHOLD": 500,
#         "PAGINATION_NUMBER": 200
#         }
#     }

#     form_data  = {'payload': json.dumps(_json)}

#     response = requests.post(url, data=form_data, auth=HTTPBasicAuth('caesarpena', 'Powermaxgp1!'))

#     if(response.status_code is not _status.HTTP_200_OK):
#         return Response(response.reason, status=_status.HTTP_400_BAD_REQUEST)
    
#     serializer = _serializers.TestSerializer(data=response.json())
#     if serializer.is_valid(raise_exception=True):
#         workspace_id = serializer.validated_data.get('pendingSelection')
#         AssignWorkspace(workspace_id, "cesar_raynell@hotmail.com")
#         return Response(workspace_id, status=_status.HTTP_200_OK)


    

def TestPydioGeneratePKs():
    url = 'http://192.168.20.103:8082/pydio-core-8.0.2/api/1/keystore_generate_auth_token/Token'

    response = requests.post(url, auth=HTTPBasicAuth('cesar_raynell@hotmail.com', 'Powermaxgp1!'), headers=None)

    if(response.status_code is not _status.HTTP_200_OK):
        return Response(response.reason, status=_status.HTTP_400_BAD_REQUEST)
    
    serializer = _serializers.PydioTokenSerializer(data=response.json())
    if serializer.is_valid(raise_exception=True):
        Token = serializer.validated_data.get('t')
        # return Response(workspace_id, status=_status.HTTP_200_OK)
        print(Token)


class SignPydioRequest():
    def __init__(self, user, url):
        url = 'http://192.168.20.103:8082/pydio-core-8.0.2/api/64bb2b6ce4e8f78104c557c3dbc3d89f/ls?format=json'

        ListUserPks = APITokenModel.objects.filter(user_profile=user, API='Pydio')
        PKsInstance = ListUserPks.first()
        data = {}
        data['options'] = 'al'
        data['auth_token'] = PKsInstance.Token
        data['auth_hash'] = PydioSdk.generate_auth_hash(url, PKsInstance.Token, PKsInstance.Private)
        resp = requests.post(url=url, data=data, stream=False, headers=None)
        print(resp.content)
        return data

def TestPydioSDK():
    url = 'http://192.168.20.103:8082/pydio-core-8.0.2/api/64bb2b6ce4e8f78104c557c3dbc3d89f/ls?format=json'

    data = {}
    data['options'] = 'al'
    data['auth_token'] = 'jVgEX6DVgOqiR147QrELzCsf'
    data['auth_hash'] = PydioSdk.generate_auth_hash(url, 'jVgEX6DVgOqiR147QrELzCsf', 'pIn18Mi95pyFFYYjPR2PJwRf')
    resp = requests.post(url=url, data=data, stream=False, headers=None)
    # 64bb2b6ce4e8f78104c557c3dbc3d89f
    print(resp.content)

def AssignWorkspace(wid, user):


    url = "http://192.168.20.103:8082/pydio-core-8.0.2/api/ajxp_conf/user_update_right/"+wid+"/"+user+"/rw"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, auth=HTTPBasicAuth('caesarpena', 'Powermaxgp1!'), headers=headers)

    if(response.status_code is not _status.HTTP_200_OK):
        # print(response.reason)
        return Response(response.reason, status=_status.HTTP_400_BAD_REQUEST)
    
    XMLDeserializer(response.content)

