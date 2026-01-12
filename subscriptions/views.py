from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Q, FloatField
from django.db.models.functions import Coalesce, TruncMonth
from datetime import datetime
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from .models import Feature, SubscriptionPlan, UserSubscription
from .serializers import (
    SignInInputSerializer,
    SignUpInputSerializer,
    UserSerializer,
    FeatureSerializer,
    SubscriptionPlanSerializer,
    SubscriptionPlanListSerializer,
    UserSubscriptionSerializer,
    UserSubscriptionListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Users"],),
    retrieve=extend_schema(tags=["Users"],),
    create=extend_schema(
        summary="Create a new user (Sign Up)",
        description="Register a new user account. This endpoint is public and does not require authentication. "
                    "Creates a new user and automatically generates an authentication token.",
        request=SignUpInputSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Invalid input data."),
        },
        tags=["Users"],
    ),
    update=extend_schema(tags=["Users"]),
    partial_update=extend_schema(tags=["Users"]),
    destroy=extend_schema(tags=["Users"]),
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User CRUD operations."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return SignUpInputSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return []
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return super().get_permissions()

    def get_authenticators(self):
        if self.request:
            # Get the action name from the method mapping
            action = self.action_map.get(self.request.method.lower())
            if action == 'create':
                return []
        return super().get_authenticators()

    @extend_schema(
        summary="User Login",
        description="Authenticate a user with username and password. Returns an authentication token that should be used in subsequent API requests. This endpoint is public and does not require authentication.",
        request=SignInInputSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "token": drf_serializers.CharField(),
                    "user_id": drf_serializers.IntegerField(),
                    "username": drf_serializers.CharField(),
                    "email": drf_serializers.EmailField(),
                }
            ),
            401: OpenApiResponse(description="Invalid credentials."),
            400: OpenApiResponse(description="Invalid input data."),
        },
        tags=["Users"],
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='login',
        authentication_classes=[],
        permission_classes=[]
    )
    def login(self, request):
        """
        Login action that authenticates user and returns auth token.
        """
        serializer = SignInInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        )

    @extend_schema(
        summary="User Logout",
        description="Invalidate the authentication token for the current user. This endpoint requires authentication.",
        responses={
            200: OpenApiResponse(description="Logged out successfully."),
            401: OpenApiResponse(description="Authentication required."),
        },
        tags=["Users"],
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='logout',
    )
    def logout(self, request):
        """
        Logout action.
        """
        request.user.auth_token.delete()
        return Response(
            {
                'message': 'Logged out successfully'
            }
        )


@extend_schema_view(
    list=extend_schema(tags=["Features"]),
    retrieve=extend_schema(tags=["Features"]),
    create=extend_schema(tags=["Features"]),
    update=extend_schema(tags=["Features"]),
    partial_update=extend_schema(tags=["Features"]),
    destroy=extend_schema(tags=["Features"]),
)
class FeatureViewSet(viewsets.ModelViewSet):
    """ViewSet for Feature CRUD operations."""

    queryset = Feature.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = FeatureSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


@extend_schema_view(
    list=extend_schema(tags=["Subscription Plans"]),
    retrieve=extend_schema(tags=["Subscription Plans"]),
    create=extend_schema(tags=["Subscription Plans"]),
    update=extend_schema(tags=["Subscription Plans"]),
    partial_update=extend_schema(tags=["Subscription Plans"]),
    destroy=extend_schema(tags=["Subscription Plans"]),
)
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for SubscriptionPlan CRUD operations."""

    queryset = SubscriptionPlan.objects.prefetch_related('features').all()
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubscriptionPlanListSerializer
        return SubscriptionPlanSerializer


@extend_schema_view(
    list=extend_schema(tags=["User Subscriptions"]),
    retrieve=extend_schema(tags=["User Subscriptions"]),
    create=extend_schema(tags=["User Subscriptions"]),
    update=extend_schema(tags=["User Subscriptions"]),
    partial_update=extend_schema(tags=["User Subscriptions"]),
    destroy=extend_schema(tags=["User Subscriptions"]),
)
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for UserSubscription CRUD operations."""

    queryset = UserSubscription.objects.select_related('user', 'plan').all()
    serializer_class = UserSubscriptionListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__email', 'plan__name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserSubscriptionSerializer
        return super().get_serializer_class()


@extend_schema_view(
    get=extend_schema(tags=["Analytics"]),
)
class AnalyticsDashboardView(APIView):
    """

    Returns comprehensive analytics data:
    - Total Recurring Revenue (sum of plan_cost for active subscriptions)
    - Average Subscription Cost
    - Monthly Revenue History (last 12 months)
    - Top 5 Users by subscription value
    """

    def get(self, request):
        today = datetime.now().date()
        twelve_months_ago = today.replace(year=today.year - 1)
        start_of_current_month = today.replace(day=1)

        revenue_stats = UserSubscription.objects.aggregate(
            total_recurring_revenue=Coalesce(
                Sum(
                    'plan_cost',
                    filter=Q(is_active=True)
                ),
                0,
                output_field=FloatField(),
            ),
            average_subscription_cost=Coalesce(
                Avg('plan_cost'),
                0,
                output_field=FloatField(),
            )
        )

        total_recurring_revenue = revenue_stats['total_recurring_revenue']
        average_subscription_cost = revenue_stats['average_subscription_cost']

        monthly_revenue = (
            UserSubscription.objects
            .filter(start_date__gte=twelve_months_ago, start_date__lt=start_of_current_month)
            .annotate(month=TruncMonth('start_date'))
            .values('month')
            .annotate(total_revenue=Sum('plan_cost'))
            .order_by('month')
        )

        top_users = (
            User.objects
            .annotate(total_subscription_value=Sum('user_subscriptions__plan_cost'))
            .filter(total_subscription_value__isnull=False)
            .order_by('-total_subscription_value')
            .values('id', 'username', 'email', 'total_subscription_value')[:5]
        )

        return Response(
            {
                'total_recurring_revenue': total_recurring_revenue,
                'average_subscription_cost': average_subscription_cost,
                'monthly_revenue_history': monthly_revenue,
                'top_users': top_users,
            }
        )
