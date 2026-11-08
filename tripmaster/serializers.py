from rest_framework import serializers
from django.contrib.auth.models import User
from tripmaster.models import TripDb


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDb
        
        fields = "__all__"
        
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
        
    
    