
from django.urls import path

from TwsTradingApp.trading.views import index, SignInView, SignOutView, SignUpView, \
    backtest_in_progress, all_results, add_strategy_to_portfolio, portfolio_view, added_strategy, deploy_strategy, \
    stop_strategy, remove_strategy, update_historical_data, StrategiesListView, StrategyDetailView, FeedbackView, \
    AdminFeedbackView

urlpatterns = (
    path('', index, name='index'),
    path('profile/sign-up', SignUpView.as_view(), name='sign up'),
    path('profile/sign-in', SignInView.as_view(), name='sign in'),
    path('profile/sign-out', SignOutView.as_view(), name='sign out'),
    path('backtest', StrategiesListView.as_view(), name='strategies'),
    path('backtest/<int:pk>/', StrategyDetailView.as_view(), name='strategy detail'),
    path('submit-feedback/', FeedbackView.as_view(), name='submit-feedback'),
    path('admin-feedback/', AdminFeedbackView.as_view(), name='admin-feedback'),
    path('backtest/backtest-in-progress/', backtest_in_progress, name='backtest started'),
    path('results/', all_results, name='results'),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('portfolio/add/<int:pk>/', add_strategy_to_portfolio, name='add strategy'),
    path('portfolio/add-strategy/', added_strategy, name='added strategy'),
    path('portfolio/deploy-strategy/<int:pk>/', deploy_strategy, name='deploy strategy'),
    path('portfolio/remove-strategy/<int:pk>/', remove_strategy, name='remove strategy'),
    path('portfolio/stop-strategy/<int:pk>/', stop_strategy, name='stop strategy'),
    path('update-timeseries/', update_historical_data, name='update timeseries'),

)




