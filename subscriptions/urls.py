from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    FeatureViewSet,
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
    AnalyticsDashboardView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'features', FeatureViewSet, basename='feature')
router.register(r'plans', SubscriptionPlanViewSet, basename='subscriptionplan')
router.register(
    r'subscriptions',
    UserSubscriptionViewSet,
    basename='usersubscription'
)

urlpatterns = [
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics'),
] + router.urls
