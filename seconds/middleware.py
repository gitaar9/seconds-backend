from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from oauth2_provider.models import AccessToken

from seconds.chat.consumers import send_game_update


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
            query_params = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
            token_key = query_params.get('token', None)
            game_code = query_params.get('game_code', None)
        except ValueError:
            token_key = None
            game_code = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        scope['game_code'] = game_code
        return await super().__call__(scope, receive, send)


class GameUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # Still not perfect but a lot less updates than with a post_save signal
        if ('game' in request.path or 'team' in request.path) and request.user is not None and \
                not isinstance(request.user, AnonymousUser) and request.user.in_game:
            send_game_update(request.user.game)

        return response