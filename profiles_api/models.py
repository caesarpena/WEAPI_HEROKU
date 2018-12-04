from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

# Create your models here.

class UserProfileManager(BaseUserManager):
    """ Helps Django work with our custom user model """
    def create_user(self, email, name, last_name, password=None):
        """ Creates a new user profile object. """
        if not email:
            raise ValueError('Users must have an email address')
        email  = self.normalize_email(email)
        user = self.model(email=email, name=name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, last_name, password):
        """ Creates and save a new super user with the given details """
        user = self.create_user(email, name, last_name, password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """ Represent a "user profile" inside out system """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']

    def get_full_name(self):
        """ Used to tge a users full name. """
        fullname = self.name+" "+self.last_name

        return fullname
    def get_short_name(self):
        """ Used to get a users short name """
        return self.name

    def __str__(self):
        """ django uses this when it needs to convert the object to a string """
        return self.email

class UserPks(models.Model):
    """ Represent the projects that the user can create """
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=False, db_column = "user_id", related_name = "user_pks")
    API = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    private = models.CharField(max_length=255, blank=True, null=True)

    REQUIRED_FIELDS = []

    # def __str__(self):
    #     """ django uses this when it needs to convert the object to a string """
    #     if self.user_profile==None:
    #         return "ERROR-USER Profile IS NULL"


class OtherAPIAdmin(AbstractBaseUser):
    """ Represent the projects that the user can create """
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    # password = models.CharField(max_length=255, unique=True, blank=True, null=True)
    api = models.CharField(max_length=255, unique=True, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    private = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class UserRepositories(models.Model):
    """ Represent the projects that the user can create """
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=False, db_column = "user_id", related_name = "user_repositories")
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    workspace_id = models.CharField(max_length=255, blank=True, null=True)
    last_update = models.DateTimeField(auto_now_add=True, null=True)
    #scene_location = models.CharField(max_length=255, null=True)
    
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['name']

    def __str__(self):
        """ django uses this when it needs to convert the object to a string """
        return self.name

    #objects = UserProjectManager()


class UserAssets(models.Model):
    """ Represent the Assets that the user have uploaded """
    user_id = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=False, db_column = "user_id", related_name = "user_assets")
    asset_format = models.CharField(max_length=255)
    asset_name = models.CharField(max_length=255)
    asset_path = models.CharField(max_length=255)
    uploaded_on = models.DateTimeField(auto_now_add=True)  
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['asset_format', 'asset_name',]

    def __str__(self):
        """ django uses this when it needs to convert the object to a string """
        return self.asset_name