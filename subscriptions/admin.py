from django.contrib import admin
from .models import Feature, SubscriptionPlan, UserSubscription


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    list_per_page = 50


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "billing_cycle", "created_at"]
    list_filter = ["billing_cycle", "created_at"]
    search_fields = ["name", "description"]
    filter_horizontal = ["features"]
    list_per_page = 50


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan",
        "plan_cost",
        "start_date",
        "end_date",
        "is_active"
    ]
    list_filter = ["is_active", "start_date", "plan__billing_cycle"]
    search_fields = ["user__username", "user__email", "plan__name"]
    date_hierarchy = "start_date"
    list_per_page = 50
    autocomplete_fields = ["user", "plan"]
