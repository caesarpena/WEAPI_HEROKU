from django.conf.urls import url
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('profile', views.UserProfileViewSet)
router.register('projects', views.UserProjectsViewSet)
router.register('external-api-admin', views.APIAdminProfileViewSet)
router.register('project-assets', views.GetProjectAssetsViewSet, base_name='project-assets')
router.register('download-asset', views.DownloadAssetViewSet, base_name='download-asset')
router.register('sign-pydio-request', views.GetPydioSignedToken, base_name='sign-pydio-request')


""" you set a base name when the viewset is not a model viewset """
router.register('login', views.LoginViewSet, base_name='login')

urlpatterns = [
    url(r'^hello-view/', views.HelloAPIView.as_view()),
    # url(r'^sign-pydio-request/', views.GetPydioSignedToken.as_view()),
    url(r'', include(router.urls))
]