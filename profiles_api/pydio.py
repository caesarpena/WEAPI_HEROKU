import http.client
import requests
import json
from rest_framework import status as _status
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from requests.auth import HTTPBasicAuth
from requests_toolbelt import MultipartEncoder
from django.core import serializers

from django.utils.encoding import smart_str
import os
from io import BytesIO

from . import models

from pydiosdkpython.remote import PydioSdk

from lxml import etree

from . import pydio_response_serializers as pydio_serializers

#baseurl = 'http://192.168.1.27:8082/pydio-core-8.0.2/api/'
baseurl = 'http://drive.geobimeng.com/api/'

def XMLDeserializer(xmldata):
    """ test XML deserialization """

    stream = BytesIO(xmldata)  
    #parse XML
    newData = etree.parse(stream)
    type = newData.find('message').get('type')

    if type is "ERROR":
        return ({'status':_status.HTTP_400_BAD_REQUEST, 'message':newData.find('message')})
    
    data = XMLParser().parse(stream)
    serializer = pydio_serializers.ResponseTreeContent(data=data)
    if serializer.is_valid(raise_exception=True):           
        message = serializer.validated_data.get('message')
        return ({'status':_status.HTTP_200_OK, 'message':message})

    return ({'status':_status.HTTP_400_BAD_REQUEST, 'message':serializer.errors})

def GeneratePydioPKs(username, password):
    url = baseurl+'1/keystore_generate_auth_token/DjangoWebApi'

    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=None)

    if(response.status_code is not _status.HTTP_200_OK):
        return Response(response.reason, status=_status.HTTP_400_BAD_REQUEST)
    
    serializer = pydio_serializers.PydioTokenSerializer(data=response.json())
    if serializer.is_valid(raise_exception=True):

        # print(serializer['t'].value)
        # print(serializer['p'].value)

        json = {
            "API": 'Pydio',
            "Token": serializer['t'].value,
            "Private": serializer['p'].value,
            }
        return json   

def SignPydioRequest(url, user=None, API=None):
    PKsInstance = None
    if(user):
        ListPks = models.UserPks.objects.filter(user_profile=user, API='Pydio')
        PKsInstance = ListPks.first()
    if(API):
        ListPks = models.OtherAPIAdmin.objects.get(api=API)
        PKsInstance = ListPks

    print(PKsInstance.token)
    print(PKsInstance.private)

    data = {}
    data['options'] = 'al'
    data['auth_token'] = PKsInstance.token
    data['auth_hash'] = PydioSdk.generate_auth_hash(url, PKsInstance.token, PKsInstance.private)
    return data

# http://192.168.20.103:8082/pydio-core-8.0.2/api/64bb2b6ce4e8f78104c557c3dbc3d89f/ls?format=json

class HandleTokens:
    def __init__(self, validated_data, user_id):
        APITokenModel = models.UserPks
        user = models.UserProfile.objects.get(id=user_id)
        
        ListUserPks = APITokenModel.objects.filter(user_profile=user, API=validated_data['API'])

        if not ListUserPks.count(): 
            models.UserPks(
                user_profile = user,
                API = validated_data['API'],
                Token = validated_data['Token'],
                Private = validated_data['Private'],
            ).save()           
            return None

        TokenInstance = ListUserPks.first()
        print(TokenInstance.token)
        TokenInstance.token = validated_data['Token']
        TokenInstance.private = validated_data['Private']
        TokenInstance.save()
        return None

class HandleAdminTokens:
    
    def __init__(self, API):
        APITokenModel = models.UserPks
        user = models.UserProfile.objects.get(id=user_id)
        
        ListAdminPks = APITokenModel.objects.filter(user_profile=user, API=validated_data['API'])

        if not ListUserPks.count(): 
            models.UserPks(
                user_profile = user,
                API = validated_data['API'],
                Token = validated_data['Token'],
                Private = validated_data['Private'],
            ).save()           
            return None

        TokenInstance = ListUserPks.first()
        TokenInstance.Token = validated_data['Token']
        TokenInstance.Private = validated_data['Private']
        TokenInstance.save()
        return None

def GetProjectAssets(projectid, user):
    
    url = baseurl+projectid+"/ls/?format=xml"

    PARAMS = SignPydioRequest(url = url, user = user)

    response = requests.get(url=url, params=PARAMS)

    return (response)

def DownloadAsset(workspace_id, assetname, user):
    
    url = baseurl+"v2/io/" + workspace_id + "/" + assetname + "? format=json"

    PARAMS = SignPydioRequest(url = url, user = user)
    
    response = requests.get(url=url, params=PARAMS)
    
    # print(response.encoding)
    # r = response.text.encode('unicode-escape')

    # print(r)

    if(response.status_code != _status.HTTP_200_OK or response.reason != 'OK'):
        return Response(response.reason, status=response.status_code)
        # return ({'status': response.status_code, 'reason': response.reason})

    # return (json.dumps(response.content))
    # return (str(response.content))
    return(response.content.decode('utf-8',errors='ignore'))
    # return(r)

def CreateUserWorkspace(wname, user):
    
    url = baseurl+"v2/admin/workspaces?format=json"

    _json = {
        "display": wname,
        "accessType": "fs",
        "isTemplate": False,
        "parameters": {
        "PATH": "AJXP_DATA_PATH/workspaces/"+user+"/"+wname,
        "CREATE": True,
        "RECYCLE_BIN": "recycle_bin",
        "CHMOD_VALUE": "0600",
        "DEFAULT_RIGHTS": "rw",
        "PAGINATION_THRESHOLD": 500,
        "PAGINATION_NUMBER": 200
        }
    }

    form_data = SignPydioRequest(url = url, API = 'Pydio')

    form_data['payload'] = json.dumps(_json)

    # form_data  = {'payload': json.dumps(_json)}

    # response = requests.post(url, data=form_data, auth=HTTPBasicAuth('caesarpena', 'Powermaxgp1!'))

    response = requests.post(url=url, data=form_data, stream=False, headers=None)

    if(response.status_code is not _status.HTTP_200_OK):
        return ({'status': response.status_code, 'reason': response.reason})
    
    serializer = pydio_serializers.TestSerializer(data=response.json())

    if serializer.is_valid(raise_exception=True):
        workspace_id = serializer.validated_data.get('pendingSelection')
        res = AssignWorkspace(wid =workspace_id, user=user)
        if (res.get('status') is not _status.HTTP_200_OK):
            return (res)
        
        return ({'status': _status.HTTP_200_OK, 'message':'workspace created succesfully', 'workspace': workspace_id})

def AssignWorkspace(wid, user):


    url = baseurl+"ajxp_conf/user_update_right/"+wid+"/"+user+"/rw"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, auth=HTTPBasicAuth('caesarpena', 'Powermaxgp1!'), headers=headers)

    if(response.status_code is not _status.HTTP_200_OK):
        # print(response.reason)
        return ({'status': response.status_code, 'reason': response.reason})
    
    res = XMLDeserializer(xmldata=response.content)

    return (res)

