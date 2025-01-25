from rest_framework import serializers
from .models import UserProfile

class UserProfileSrializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone', 'is_subscribed', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user