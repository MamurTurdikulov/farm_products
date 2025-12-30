from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_seller', 'is_customer']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_seller = serializers.BooleanField(default=False)
    is_customer = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_seller', 'is_customer']

    def validate(self, data):
        if not data.get('is_seller') and not data.get('is_customer'):
            raise serializers.ValidationError("User must be at least seller or customer.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_seller=validated_data['is_seller'],
            is_customer=validated_data['is_customer']
        )
        return user

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()