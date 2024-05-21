from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/api/chat-api/', consumers.PandasAI_ChatWebsocket.as_asgi()),
    path('ws/api/make-agent/', consumers.PandasAI_MakeAgentWebsocket.as_asgi()),
    path('ws/api/resetstatus/', consumers.PandasAI_ResetWebsocket.as_asgi()),
]