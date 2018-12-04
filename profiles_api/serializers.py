from rest_framework import serializers
from collections import Counter
from rest_framework.serializers import (
    EmailField,
    CharField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from django.contrib.auth import get_user_model
from django.db.models import Q
from . import models




class HelloSerializer(serializers.Serializer):
    """ Serializes a name field for testing our APIView """
    name = serializers.CharField(max_length = 10)


User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for the users profile objects """
    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'last_name', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Creates and return a new user """

        user = models.UserProfile(
            email= validated_data['email'],
            name= validated_data['name'],
            last_name = validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

class otherAPIadminSerializer(serializers.ModelSerializer):
    """ Serializer for the users profile objects """
    # api = CharField(required = False, allow_blank= True)
    class Meta:
        model = models.OtherAPIAdmin
        fields = ('id', 'username', 'api', 'token', 'private', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Creates and return a new user """

        if validated_data.get('api', None):
            APIAdmin = models.OtherAPIAdmin(
                username= validated_data['username'],
                api= validated_data['api'],
                token = validated_data['token'],
                private = validated_data['private'],
            )
            APIAdmin.set_password(validated_data['password'])
            APIAdmin.save()

        return APIAdmin
    
    def validate(self, data):
        api = data.get("api", None)
        user = self.context['request'].user
        userModel = models.UserProfile.objects.get(email=user)
        if not userModel.is_staff:
            raise ValidationError("ACCESS DENIED")
        if not api:
            raise ValidationError("An API is required")
        adminAPI = models.OtherAPIAdmin.objects.filter(
            Q(api=api) 
        ).distinct()
        if adminAPI.exists():        
            raise ValidationError("An admin profile for this API already exist")
        return data


class otherAPIadminSerializerUpdate(serializers.ModelSerializer):
    """ Serializer for the users profile objects """
    # api = CharField(required = False, allow_blank= True)
    class Meta:
        model = models.OtherAPIAdmin
        fields = ('id', 'token', 'private',)

    # def update(self, instance, validated_data):
    #     print('this - here')
        # API = models.OtherAPIAdmin.objects.get(api=validated_data.get('api', None))
        # API.objects.filter(pk=instance.id).update(**validated_data)
        # return API


class UserLoginSerializer(serializers.ModelSerializer):
    """ Serializer for the users profile objects """
    user_obj = None
    email = EmailField(label='Email Address', required=False, allow_blank=True)
    username = CharField(required = False, allow_blank= True)
    class Meta:
        model = models.UserProfile
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data.get("username", None)
        password = data.get("password")
        # username= data.get("username", None)
        if not email:
            raise ValidationError("A username or email is required to login")
        user = User.objects.filter(
            Q(email=email) 
        ).distinct()
        if user.exists() and user.count() == 1:
            user_obj= user.first()
        else:
            raise ValidationError("This username/email is not valid")
        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect username or password")      
      
        return data

class UserRepositoriesSerializer(serializers.ModelSerializer):
    """ Serializer for users projects objects """
    name = CharField(required = False, allow_blank= True)
    class Meta:
        model = models.UserRepositories
        fields = ('id', 'user_profile', 'name', 
                'last_update', 'workspace_id', 'created_on',)
        extra_kwargs = {'user_profile': {'read_only': True}}

    def validate(self, data):
        name = data.get("name", None)

        if not name:
            raise ValidationError("A project name is required")
        project = models.UserRepositories.objects.filter(
            Q(name=name) 
        ).distinct()
        if project.exists():        
            raise ValidationError("A project with this name already exist, Please try a different name.")
        count = Counter(name)
        count = sum(dict(count).values())
        if(count <= 3):
            raise ValidationError("The project name should have more than 3 characters")
      
        return data

class UserAssetsSerializer(serializers.ModelSerializer):
    """ Serializer for the users profile objects """
    class Meta:
        model = models.UserAssets
        fields = ('id','user_id', 'asset_name', 'asset_format', 'asset_path',)
        extra_kwargs = {'user_id': {'read_only': True}}
