"""
Serializers for the users app.
"""

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import User, UserActivity, UserPermission


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'department',
                  'phone', 'profile_image', 'preferred_language', 'date_joined',
                  'last_login', 'is_active')
        read_only_fields = ('id', 'date_joined', 'last_login')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.
    """

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name',
                  'role', 'department', 'phone', 'profile_image', 'preferred_language')
        read_only_fields = ('id',)

    def validate(self, data):
        """
        Check that the passwords match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": _("Passwords don't match.")})
        return data

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a user.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'department',
                  'phone', 'profile_image', 'preferred_language', 'is_active')
        read_only_fields = ('id', 'username', 'email')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.
    """

    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Check that the new passwords match and the old password is correct.
        """
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": _("New passwords don't match.")})
        return data

    def validate_old_password(self, value):
        """
        Check that the old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect."))
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    identifier = serializers.CharField(required=True, help_text=_('Username or Email'))
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Validate user credentials.
        """
        identifier = data['identifier']
        password = data['password']

        # Check if identifier is an email or username
        if '@' in identifier:
            # Try to authenticate with email
            user = User.objects.filter(email=identifier).first()
            if user:
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError(_("User account is disabled."))
                    return {'user': user}
        else:
            # Try to authenticate with username
            user = authenticate(username=identifier, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(_("User account is disabled."))
                return {'user': user}

        # If we get here, authentication failed
        raise serializers.ValidationError(_("Invalid username/email or password."))


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the UserActivity model.
    """

    user_email = serializers.SerializerMethodField()

    class Meta:
        model = UserActivity
        fields = ('id', 'user', 'user_email', 'action', 'action_time', 'ip_address', 'user_agent', 'page')
        read_only_fields = ('id', 'user', 'user_email', 'action_time')

    def get_user_email(self, obj):
        """
        Get the user's email.
        """
        return obj.user.email


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserPermission model.
    """

    user_email = serializers.SerializerMethodField()

    class Meta:
        model = UserPermission
        fields = ('id', 'user', 'user_email', 'module', 'can_view', 'can_add', 'can_edit', 'can_delete')
        read_only_fields = ('id', 'user_email')

    def get_user_email(self, obj):
        """
        Get the user's email.
        """
        return obj.user.email
