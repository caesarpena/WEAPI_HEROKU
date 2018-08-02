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



class PydioTokenSerializer(serializers.Serializer):
    t = serializers.CharField()
    p = serializers.CharField()


class NestedSerializer1(serializers.Serializer):
    message = serializers.CharField()
    level = serializers.CharField()

class NestedSerializer2(serializers.Serializer):
    pendingSelection = serializers.CharField()
    node = serializers.CharField(required = False, allow_blank= True)

class TestSerializer(serializers.Serializer):
        message = NestedSerializer1(source='*')
        reload = NestedSerializer2(source='*')





class ResponseTreeContent(serializers.Serializer):
    message = serializers.CharField()
    # update_checkboxes = serializers.CharField(required = False, allow_blank= True)
    
    def validate(self, data):

        message = data.get("message", None)
        if "ERROR" in message:
            raise ValidationError(message)
        # user = User.objects.filter(
        #     Q(email=email) 
        # ).distinct()
        # if user.exists() and user.count() == 1:
        #     user_obj= user.first()
        # else:
        #     raise ValidationError("This username/email is not valid")
        # if user_obj:
        #     if not user_obj.check_password(password):
        #         raise ValidationError("Incorrect username or password")      
      
        return data
    
