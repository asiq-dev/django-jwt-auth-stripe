# from django.contrib.auth.models import User 
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from .serializers import UserProfileSrializer
from .models import UserProfile

from rest_framework import status
import stripe
from ventureAI import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSrializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserProfileSrializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)




#stripe implementation#

# checkout for webhook implementation (webhook way)
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        domain = request.build_absolute_uri('/')
        try:
            user = request.user
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': '',
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=user.email,
                success_url= domain + reverse('payment-success'),
                cancel_url= domain + reverse('payment-cancel'),
                metadata={
                    'user_id': user.id,
                },
            )
            return Response({'checkout_url': checkout_session['url']})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@csrf_exempt
def StripeWebhookView(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')

        if user_id:
            try:
                user = UserProfile.objects.get(id=user_id)
                user.is_subscribed = True
                user.save()
            except UserProfile.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

    return HttpResponse(status=200)
class PaymentSuccessView(APIView):
    def get(self, request):
        return Response({'message': 'Payment was Siccessfull.'})

class PaymentCancelView(APIView):
    def get(self, request):
        return Response({'message': 'Payment was canceled.'})


# checkout for payment checkout by success and cancel(normal way)
# class CreateCheckoutSessionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         domain = request.build_absolute_uri('/')
#         user = request.user

#         # Create Stripe Checkout Session
#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=[
#                     {
#                         'price': '',
#                         'quantity': 1,
#                     }
#                 ],
#                 mode='subscription',  # Use 'payment' for one-time payments
#                 success_url=domain + reverse('payment-success') + '?session_id={CHECKOUT_SESSION_ID}',
#                 cancel_url=domain + reverse('payment-cancel'),
#                 customer_email=user.email,  # Pre-fill the user's email
#             )
#             return Response({'url': checkout_session.url}, status=200)
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)

# class PaymentSuccessView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request):
#         session_id = request.query_params.get('session_id')
#         if not session_id:
#             return Response({'error': 'Session ID is missing'}, status=400)

#         try:
#             session = stripe.checkout.Session.retrieve(session_id)
#             customer_email = session['customer_details']['email']
#             # Retrieve and update the user profile
#             user = UserProfile.objects.get(email=customer_email)
#             user.is_subscribed = True
#             user.save()
#             return Response({'message': 'Subscription successful!'})
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)


# class PaymentCancelView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         return Response({'message': 'Payment was canceled.'})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_all(request):
#     user = request.user
#     tokens = OutstandingToken.objects.filter(user=user)
#     for token in tokens:
#         token.blacklist()
#     return Response({'message': 'Successfully logged out from all sessions.'}, status=200)

# class LogoutAllView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             user = request.user
            
#             # Get all outstanding refresh tokens for the user
#             outstanding_tokens = OutstandingToken.objects.filter(user=user)
            
#             # Blacklist all refresh tokens
#             for token in outstanding_tokens:
#                 RefreshToken(token.token).blacklist()
            
#             return Response({"message": "Successfully logged out from all devices."},
#                             status=status.HTTP_205_RESET_CONTENT)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all(request):
    user = request.user
    tokens = OutstandingToken.objects.filter(user=user)
    
    for token in tokens:
        try:
            if not BlacklistedToken.objects.filter(token=token).exists():
                refresh_token = RefreshToken(token.token)
                refresh_token.blacklist()
        except Exception as e:
            return Response({'error': f'Failed to blacklist token: {str(e)}'}, status=400)
    
    return Response({'message': 'Successfully logged out from all sessions.'}, status=200)