from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Feature, SubscriptionPlan, UserSubscription
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator


class SignInInputSerializer(serializers.Serializer):
    """Serializer for User Sign In."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class SignUpInputSerializer(serializers.Serializer):
    """Serializer for User Sign Up."""

    username = serializers.CharField()
    email = serializers.EmailField(
        required=True, validators=[EmailValidator()]
    )
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = self.Meta.model.objects.create_user(
            **validated_data
        )
        return user

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        ]

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value


class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for Feature model."""

    class Meta:
        model = Feature
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model."""
    features = FeatureSerializer(many=True, read_only=True)
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Feature.objects.all(),
        source='features'
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'price',
            'billing_cycle',
            'description',
            'features',
            'feature_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing subscription plans."""

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'billing_cycle']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for UserSubscription model."""
    user = UserSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source='user'
    )
    plan_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=SubscriptionPlan.objects.all(),
        source='plan'
    )

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user',
            'user_id',
            'plan',
            'plan_id',
            'plan_cost',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSubscriptionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing user subscriptions."""
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user_username',
            'plan_name',
            'plan_cost',
            'start_date',
            'end_date',
            'is_active'
        ]
