"""
Views for the help_center app.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    HelpCategory, HelpArticle, FAQ, UserFeedback,
    SupportRequest, SupportResponse
)
from .serializers import (
    HelpCategorySerializer, HelpArticleSerializer, FAQSerializer,
    UserFeedbackSerializer, SupportRequestSerializer, SupportResponseSerializer
)
from regulations.permissions import IsManagerOrAdmin
from users.permissions import IsAdminUser


class HelpCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing help categories.
    """
    
    queryset = HelpCategory.objects.all().order_by('order', 'name')
    serializer_class = HelpCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """
        Get the articles in the category.
        """
        category = self.get_object()
        
        # Filter by published status for non-admin users
        if not (request.user.is_admin or request.user.is_manager):
            articles = category.articles.filter(is_published=True)
        else:
            articles = category.articles.all()
        
        serializer = HelpArticleSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def faqs(self, request, pk=None):
        """
        Get the FAQs in the category.
        """
        category = self.get_object()
        
        # Filter by published status for non-admin users
        if not (request.user.is_admin or request.user.is_manager):
            faqs = category.faqs.filter(is_published=True)
        else:
            faqs = category.faqs.all()
        
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data)


class HelpArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing help articles.
    """
    
    queryset = HelpArticle.objects.all().order_by('category', 'order', 'title')
    serializer_class = HelpArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_published', 'is_featured']
    search_fields = ['title', 'content', 'keywords']
    lookup_field = 'slug'
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        # Filter by published status for non-admin users
        if not (self.request.user.is_admin or self.request.user.is_manager):
            return HelpArticle.objects.filter(is_published=True).order_by('category', 'order', 'title')
        return HelpArticle.objects.all().order_by('category', 'order', 'title')
    
    def perform_create(self, serializer):
        """
        Set the created_by and updated_by fields to the current user.
        """
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """
        Set the updated_by field to the current user.
        """
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured articles.
        """
        # Filter by published status for non-admin users
        if not (request.user.is_admin or request.user.is_manager):
            articles = HelpArticle.objects.filter(is_published=True, is_featured=True)
        else:
            articles = HelpArticle.objects.filter(is_featured=True)
        
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, slug=None):
        """
        Get feedback for the article.
        """
        article = self.get_object()
        
        # Only managers and admins can see feedback
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to view feedback.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = article.feedback.all()
        serializer = UserFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)


class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing FAQs.
    """
    
    queryset = FAQ.objects.all().order_by('category', 'order', 'question')
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_published']
    search_fields = ['question', 'answer']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        # Filter by published status for non-admin users
        if not (self.request.user.is_admin or self.request.user.is_manager):
            return FAQ.objects.filter(is_published=True).order_by('category', 'order', 'question')
        return FAQ.objects.all().order_by('category', 'order', 'question')
    
    def perform_create(self, serializer):
        """
        Set the created_by and updated_by fields to the current user.
        """
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """
        Set the updated_by field to the current user.
        """
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        """
        Get feedback for the FAQ.
        """
        faq = self.get_object()
        
        # Only managers and admins can see feedback
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to view feedback.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = faq.feedback.all()
        serializer = UserFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)


class UserFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user feedback.
    """
    
    queryset = UserFeedback.objects.all().order_by('-created_at')
    serializer_class = UserFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['content_type', 'feedback_type', 'article', 'faq', 'user']
    search_fields = ['comment', 'email']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the user field to the current user if authenticated.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class SupportRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing support requests.
    """
    
    queryset = SupportRequest.objects.all().order_by('-created_at')
    serializer_class = SupportRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'user', 'assigned_to']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'updated_at', 'resolved_at']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['update', 'partial_update', 'destroy', 'assign', 'resolve']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user
        
        # Admins and managers can see all requests
        if user.is_admin or user.is_manager:
            return SupportRequest.objects.all().order_by('-created_at')
        
        # Other users can only see their own requests
        return SupportRequest.objects.filter(user=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Set the user field to the current user.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """
        Get the responses to the support request.
        """
        support_request = self.get_object()
        
        # Filter internal responses for non-admin users
        if not (request.user.is_admin or request.user.is_manager):
            responses = support_request.responses.filter(is_internal=False)
        else:
            responses = support_request.responses.all()
        
        serializer = SupportResponseSerializer(responses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign the support request to a user.
        """
        support_request = self.get_object()
        
        # Validate the request data
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'detail': _('user_id is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': _('User not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update the support request
        support_request.assigned_to = assigned_user
        support_request.status = SupportRequest.STATUS_IN_PROGRESS
        support_request.save()
        
        serializer = self.get_serializer(support_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve the support request.
        """
        support_request = self.get_object()
        
        # Check if the request is already resolved
        if support_request.status == SupportRequest.STATUS_RESOLVED:
            return Response(
                {'detail': _('Support request is already resolved.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the support request
        support_request.status = SupportRequest.STATUS_RESOLVED
        support_request.resolved_at = timezone.now()
        support_request.save()
        
        serializer = self.get_serializer(support_request)
        return Response(serializer.data)


class SupportResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing support responses.
    """
    
    queryset = SupportResponse.objects.all().order_by('request', 'created_at')
    serializer_class = SupportResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['request', 'user', 'is_internal']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user
        
        # Admins and managers can see all responses
        if user.is_admin or user.is_manager:
            return SupportResponse.objects.all().order_by('request', 'created_at')
        
        # Other users can only see non-internal responses to their own requests
        return SupportResponse.objects.filter(
            Q(request__user=user) & Q(is_internal=False)
        ).order_by('request', 'created_at')
    
    def perform_create(self, serializer):
        """
        Set the user field to the current user.
        """
        # Only managers and admins can create internal responses
        if not (self.request.user.is_admin or self.request.user.is_manager):
            serializer.save(user=self.request.user, is_internal=False)
        else:
            serializer.save(user=self.request.user)
