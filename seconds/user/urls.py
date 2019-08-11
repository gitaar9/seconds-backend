from django.conf.urls import url, include
from rest_framework import routers

from seconds.user.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]