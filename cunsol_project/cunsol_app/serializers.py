from rest_framework import serializers
from .models import users


class UserdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['id', 'name', 'email', 'password','contact', 'is_active', 'created_at' ]
