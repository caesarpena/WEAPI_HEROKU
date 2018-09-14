from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.core import serializers as core_serializer
from rest_framework import status as _status

from . import models
from . import serializers
from . import permissions
from . import pydio as P

from rest_framework import status
from rest_framework import viewsets

# Create your views here.

class HelloAPIView(APIView):
    """ Test API view """
    serializer_class = serializers.HelloSerializer
    def get(self, request, format=None):
        """ Returns a list of APIView features. """

        an_apiview = [
            'User HTTP Methods as function (get, post patch, put, delete)',
            'It is similar to a traditional django view',
            'Gives you the most control over your logic',
            'Is mapped manually to URLs'
        ]

        return Response({'message': 'Hello!', 'an_apiview': an_apiview})

    def post(self, request):
         """ Create a hello message wth our name """
         serializer = serializers.HelloSerializer(data = request.data)
         
         if serializer.is_valid():
             name = serializer.data.get('name')
             message = 'Hello {0}'.format(name)
             return Response({'message': message})
         else:
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """ Handles updating object. """
        return Response({'method': 'Put'})
    
    def patch(self, request, pk=None):
        """ Patch request, only updates fields provided in the request. """
        return Response({'method': 'patch'})

    def delete(self, request, pk=None):
        """ Deletes an object. """
        return Response({'method': 'delete'})

class HelloViewSet(viewsets.ViewSet):
    """Test API ViewSet."""

    serializer_class = serializers.HelloSerializer
    
    def list(self, request):
        """Return a hello message."""

        a_viewset = [
            'Uses actions (list, create, retrieve, update, partial_update)',
            'Automatically maps to URLs using Routers',
            'Provides more functionality with less code.'
        ]

        return Response({'message': 'Hello!', 'a_viewset': a_viewset})

    def create(self, request):
        """Create a new hello message."""

        serializer = serializers.HelloSerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.data.get('name')
            message = 'Hello {0}'.format(name)
            return Response({'message': message})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handles getting an object by its ID."""

        return Response({'http_method': 'GET'})

    def update(self, request, pk=None):
        """Handles updating an object."""

        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        """Handles updating part of an object."""

        return Response({'http_method': 'PATCH'})

class UserProfileViewSet(viewsets.ModelViewSet):
    """ Handle creating and updating profiles """

    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    """ put a comma so that django knows that it should be created as a touple """
    authentication_classes = (TokenAuthentication,) 
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)

class APIAdminProfileViewSet(viewsets.ModelViewSet):
    """ Handle creating and updating Third API's Admins profiles """
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.otherAPIadminSerializer
    queryset = models.OtherAPIAdmin.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def partial_update(self, request, pk):
        """ Patch request, only updates fields provided in the request. """  
           
        model = models.OtherAPIAdmin.objects.get(id=pk)
        print(model) 
        serializer = serializers.otherAPIadminSerializerUpdate(model, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

    def get_queryset(self):
        return models.OtherAPIAdmin.objects.all() 
    
    def get_serializer_context(self):
        return {'request': self.request}

class LoginViewSet(viewsets.ViewSet, ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    
    """ its called when an http post is make to the viewset  """
    def create(self, request, *args, **kwargs):

        data = request.data
        serializer = serializers.UserLoginSerializer(data=data)
        # serializer_Apis = serializers.UserAPIsSerializer()
        if serializer.is_valid(raise_exception=True):
            # new_data = serializer.data
            """ Use the ObtainAuthToken APIView to validate and create a token """    
            response = super(LoginViewSet, self).post(request, *args, **kwargs)
            token = Token.objects.get(key=response.data['token'])
            queryset = models.UserProfile.objects.get(id=token.user_id)
            
            json  = {   'token': token.key, 
                        'id': token.user_id,
                        'name': queryset.name,
                        'last_name': queryset.last_name,
                    }
            """ Generates a New Token/Private for this.user in Pydio """ 
            r = P.GeneratePydioPKs(username=request.data.get('username'), password=str(request.data.get('password')))         

            """ Save/Edit the new generated tokens in this.db """ 
            h = P.HandleTokens(validated_data=r, user_id = token.user_id)

            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProjectsViewSet(viewsets.ModelViewSet):
    """ Handle creating and updating projects """

    authentication_classes = (TokenAuthentication,)
    #permission_classes = (permissions.GetOwnData,)
    serializer_class = serializers.UserProjectSerializer
    queryset = models.UserProjects.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        projectname = self.request.data.get('project_name')
        """ Sets the user profile to the logged in user """
        """ First create a workspace in Pydio """
        response = P.CreateUserWorkspace(wname=projectname,user=str(user))
        # validated_data['workspace_id'] = response.get('workspace')
        serializer.save(user_profile=user, workspace_id=response.get('workspace'))
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()
    
    def get_queryset(self):
        user = self.request.user
        return models.UserProjects.objects.filter(user_profile=user.id)        

class GetProjectAssetsViewSet(viewsets.ViewSet):
    """ Handles retrieving a list of assets by project ID from the PYDIO API """
    authentication_classes = (TokenAuthentication,)
    # serializer_class = serializers.UserAssetsSerializer

    def create(self, request):

        response = P.GetProjectAssets(request.data['PROJECT_ID'], self.request.user)

        if(response.status_code != _status.HTTP_200_OK or response.reason != 'OK'):
            return Response(response.reason, status=response.status_code)

        return Response(response.content)

class GetPydioSignedToken(viewsets.ViewSet):
    """ Handles retrieving a list of assets by project ID from the PYDIO API """
    authentication_classes = (TokenAuthentication,)
    # serializer_class = serializers.UserAssetsSerializer

    def create(self, request):

        r = P.SignPydioRequest(url = request.data['url'], user = self.request.user)

        return Response(r)

class DownloadAssetViewSet(viewsets.ViewSet):
    """ Handles Downloading a single asset from a given workspace using the PYDIO API """
    authentication_classes = (TokenAuthentication,)

    def create(self, request):

        response = P.DownloadAsset(request.data['PROJECT_ID'], request.data['ASSET_NAME'], self.request.user)

        return Response(response)