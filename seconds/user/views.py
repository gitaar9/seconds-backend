from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from seconds.user.models import User
from seconds.user.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['get'], permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
