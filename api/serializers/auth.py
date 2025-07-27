from rest_framework import serializers

class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()
