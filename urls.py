from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('visits/batch-void-upload', visits_batch_void_upload, name='visits/batch-void-upload'),

]