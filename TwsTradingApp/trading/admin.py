from django.contrib import admin

from django.contrib import admin

from TwsTradingApp.trading.models import Profile, Strategy, Feedback


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    pass

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = ('display_username', 'display_email', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'user__email')  # Searching by user's username and email
    ordering = ('-timestamp',)

    def display_username(self, obj):
        return obj.user.username
    display_username.short_description = 'Username'

    def display_email(self, obj):
        return obj.user.email
    display_email.short_description = 'Email'


