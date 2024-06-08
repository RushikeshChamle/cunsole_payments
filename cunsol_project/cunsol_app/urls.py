from django.urls import path
from .views import call_elevenlabs_api
# from .views import get_dubbed_file
from .views import create_dub
from .views import fetch_file
from .views import signup, signin , session_data



urlpatterns = [
    path('call-api/', call_elevenlabs_api, name='call_api'),
    # path('get_dubbed_file/', get_dubbed_file, name='get_dubbed_file' ),
    path('create_dub/', create_dub, name='create_dub'),
    path('fetch_file/<str:dubbing_id>/<str:language_code>/', fetch_file, name='fetch_file'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('sessiondata/<str:user_id>/', session_data, name='session_data'),

]

