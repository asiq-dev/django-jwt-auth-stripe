from django.contrib.auth.models import User 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class UserAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        return Response({
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
    

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        
        if (username and password):
            if User.objects.filter(username=username).exists():
                return Response({
                    "error": "A user with that username exists",
                }, status=401)
            user = User.objects.create(username=username, password=password)
            refresh = RefreshToken.for_user(user)     
            return Response({
                "refresh": str(refresh),
                'access': str(refresh.access_token),
            }, status=201)
        
        return Response({
            "error": "Both username and password must be provided."
        })
    


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

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh_token')

    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=200)
        except Exception as e:
            return Response({'error': 'Invalid token.'}, status=400)
    else:
        return Response({'error': 'Refresh token is required.'}, status=400)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_all(request):
#     user = request.user
#     tokens = OutstandingToken.objects.filter(user=user)
#     for token in tokens:
#         token.blacklist()
#     return Response({'message': 'Successfully logged out from all sessions.'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all(request):
    user = request.user
    tokens = OutstandingToken.objects.filter(user=user)
    
    for token in tokens:
        try:
            # Check if the token is already blacklisted
            if not BlacklistedToken.objects.filter(token=token).exists():
                refresh_token = RefreshToken(token.token)
                refresh_token.blacklist()
        except Exception as e:
            # Log or handle any exceptions that may occur
            return Response({'error': f'Failed to blacklist token: {str(e)}'}, status=400)
    
    return Response({'message': 'Successfully logged out from all sessions.'}, status=200)