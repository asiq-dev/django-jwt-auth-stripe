from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import SignupUserAPIView, UserProfileAPIView




urlpatterns = [
    path('api/signup/', SignupUserAPIView.as_view(), name='signup'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/profile/', UserProfileAPIView.as_view()),
    # path('api/logout/', logout),
    # path('api/logout-all/', logout_all)
]