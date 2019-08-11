from django.conf.urls import url, include
from rest_framework import routers

from seconds.game.views import GameViewSet, TeamViewSet

router = routers.DefaultRouter()
router.register(r'game', GameViewSet)
router.register(r'team', TeamViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]