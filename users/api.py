from django.contrib.auth.models import User 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from .serializers import UserProfileSrializer
from .models import UserProfile
import stripe
from ventureAI import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class SignupUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserProfileSrializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=201)
        return Response(serializer.errors, status=400)   


class UserProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        serializer = UserProfileSrializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserProfileSrializer(user, date=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)




#stripe implementation
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        domain = request.build_absolute_uri('/')
        user = request.user

        # Create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'price_1Ql6YZIWTrSQrl9xxmIHijky',
                        'quantity': 1,
                    }
                ],
                mode='subscription',  # Use 'payment' for one-time payments
                success_url=domain + reverse('payment-success') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain + reverse('payment-cancel'),
                customer_email=user.email,  # Pre-fill the user's email
            )
            return Response({'url': checkout_session.url}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is missing'}, status=400)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            customer_email = session['customer_details']['email']
            # Retrieve and update the user profile
            user = UserProfile.objects.get(email=customer_email)
            user.is_subscribed = True
            user.save()
            return Response({'message': 'Subscription successful!'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class PaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'message': 'Payment was canceled.'})

# class UserAPI(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [AllowAny]

    
#     def get(self, request):
#         user = request.user
#         if not user.is_authenticated:
#             raise NotAuthenticated()
#         return Response({
#             "username": user.username,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#         })
    

#     def post(self, request):
#         username = request.data.get("username", "")
#         password = request.data.get("password", "")
        
#         if (username and password):
#             if User.objects.filter(username=username).exists():
#                 return Response({
#                     "error": "A user with that username exists",
#                 }, status=401)
#             user = User.objects.create(username=username, password=password)
#             refresh = RefreshToken.for_user(user)     
#             return Response({
#                 "refresh": str(refresh),
#                 'access': str(refresh.access_token),
#             }, status=201)
        
#         return Response({
#             "error": "Both username and password must be provided."
#         })
    


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     refresh_token = request.data.get('refresh_token')

#     if not refresh_token:
#         return Response({'error': 'Refresh token is required.'}, status=400)

#     try:
#         token = RefreshToken(refresh_token)
#         token.blacklist()
#         return Response({'message': 'Successfully logged out.'}, status=200)
#     except Exception as e:
#         return Response({'error': f'Invalid token: {str(e)}'}, status=400)

    
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     refresh_token = request.data.get('refresh_token')

#     if refresh_token:
#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response({'message': 'Successfully logged out.'}, status=200)
#         except Exception as e:
#             return Response({'error': 'Invalid token.'}, status=400)
#     else:
#         return Response({'error': 'Refresh token is required.'}, status=400)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_all(request):
#     user = request.user
#     tokens = OutstandingToken.objects.filter(user=user)
#     for token in tokens:
#         token.blacklist()
#     return Response({'message': 'Successfully logged out from all sessions.'}, status=200)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_all(request):
#     user = request.user
#     tokens = OutstandingToken.objects.filter(user=user)
    
#     for token in tokens:
#         try:
#             # Check if the token is already blacklisted
#             if not BlacklistedToken.objects.filter(token=token).exists():
#                 refresh_token = RefreshToken(token.token)
#                 refresh_token.blacklist()
#         except Exception as e:
#             # Log or handle any exceptions that may occur
#             return Response({'error': f'Failed to blacklist token: {str(e)}'}, status=400)
    
#     return Response({'message': 'Successfully logged out from all sessions.'}, status=200)