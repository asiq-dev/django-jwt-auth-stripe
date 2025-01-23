from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import UserAPI, logout, logout_all




urlpatterns = [
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/user/', UserAPI.as_view()),
    path('api/logout/', logout),
    path('api/logout-all/', logout_all)
]