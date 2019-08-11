from django.conf.urls import url, include
from rest_framework import routers

from seconds.word.views import WordViewSet, OptionalWordViewSet

router = routers.DefaultRouter()
router.register(r'word', WordViewSet)
router.register(r'optional_word', OptionalWordViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]