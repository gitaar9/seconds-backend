from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from oauth2_provider.models import AccessToken


@database_sync_to_async
def get_user(token_key):
    try:
        token = AccessToken.objects.get(token=token_key)
        return token.user
    except AccessToken.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Setting a header with a javascript websocket is not possible, therefore we set it in query params.
    This solution comes from here: https://gist.github.com/AliRn76/1fb99688315bedb2bf32fc4af0e50157
    """
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)
