"""
Views for the users app.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, UserActivity, UserPermission
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer, UserActivitySerializer,
    UserPermissionSerializer
)
from .permissions import IsAdminUser, IsSelfOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """
    
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'department']
    search_fields = ['email', 'first_name', 'last_name', 'department']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined', 'last_login']
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['update', 'partial_update', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
        elif self.action in ['list', 'create', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        elif self.action == 'change_password':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Change a user's password.
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': _('Password changed successfully.')}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Log in a user and return JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update user login statistics
            user.last_login = timezone.now()
            user.last_activity = timezone.now()
            user.login_count += 1
            user.save()
            
            # Create activity log
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Log out a user.
        """
        if request.user.is_authenticated:
            # Create activity log
            UserActivity.objects.create(
                user=request.user,
                action='logout',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        
        return Response({'detail': _('Successfully logged out.')}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's information.
        """
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({'detail': _('Not authenticated.')}, status=status.HTTP_401_UNAUTHORIZED)
    
    def get_client_ip(self, request):
        """
        Get the client's IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing user activities.
    """
    
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action']
    search_fields = ['action', 'ip_address', 'page']
    ordering_fields = ['action_time', 'user']
    
    def get_queryset(self):
        """
        Return the queryset based on the user's role.
        """
        if self.request.user.is_admin:
            return UserActivity.objects.all().order_by('-action_time')
        return UserActivity.objects.filter(user=self.request.user).order_by('-action_time')


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user permissions.
    """
    
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'module']
    search_fields = ['module']
    
    def get_queryset(self):
        """
        Return the queryset based on the user's role.
        """
        if self.request.user.is_admin:
            return UserPermission.objects.all()
        return UserPermission.objects.filter(user=self.request.user)
