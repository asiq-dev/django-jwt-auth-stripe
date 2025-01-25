from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import (
    SignupUserAPIView, UserProfileAPIView, CreateCheckoutSessionView, PaymentSuccessView,
    PaymentCancelView,
)




urlpatterns = [
    path('api/signup/', SignupUserAPIView.as_view(), name='signup'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('api/profile/', UserProfileAPIView.as_view()),
    path('api/create-checkout/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('api/payment-success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('api/payment-cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    # path('api/logout/', logout),
    # path('api/logout-all/', logout_all)
]