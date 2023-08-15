
from django.contrib.auth import forms as auth_forms, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from TwsTradingApp.trading.tws_contract_details import contract_trading_specs
from TwsTradingApp.trading.forms import StrategyForm, FeedbackForm
from TwsTradingApp.trading.models import Strategy, BacktestResults, Portfolio, Feedback
from django.views import generic as views, generic

from TwsTradingApp.trading.strategies import loxbars, prevrange, matrend
from TwsTradingApp.trading.tws_deploy_strategies import SimpleOrderStrategy
from TwsTradingApp.trading.tws_historical_data import get_historical_data
from TwsTradingApp.trading.visualize import plot_pnl
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib import messages


def index(request):
    if request.user.is_authenticated:
        return render(request, 'profile/with-profile.html')
    else:
        return render(request, 'profile/no-profile.html')

class SignUpForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)
        field_classes = {'username': auth_forms.UsernameField}

class SignUpView(views.CreateView):
    template_name = 'profile/sign-up.html'
    form_class = SignUpForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)

        login(self.request, self.object)
        return response

class SignInView(auth_views.LoginView):
    template_name = 'profile/sign-in.html'
    success_url = reverse_lazy('index')

    def get_success_url(self):
        if self.success_url:
            return self.success_url

        return self.get_redirect_url() or self.get_default_redirect_url()

class SignOutView(auth_views.LogoutView):
    pass


class FeedbackView(generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/feedback.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AdminFeedbackView(ListView):
    model = Feedback
    template_name = 'feedback/admin-feedback.html'
    ordering = ['-timestamp']


class StrategiesListView(ListView):
    model = Strategy
    template_name = 'strategies/all-strategies.html'
    context_object_name = 'strategies'


class StrategyDetailView(DetailView, FormMixin):
    model = Strategy
    template_name = 'strategies/strategy-inputs.html'
    form_class = StrategyForm
    context_object_name = 'strategy'

    def get_success_url(self):
        return reverse_lazy('backtest started')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        strategy_instance = self.get_object()
        context['form'] = self.form_class(instance=strategy_instance)

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        parameters = {
            'parameter1': form.cleaned_data.get('parameter1'),
            'parameter2': form.cleaned_data.get('parameter2'),
            'parameter3': form.cleaned_data.get('parameter3'),
        }
        ticker = form.cleaned_data.get('symbol')
        ticker = ticker.split(' ')[0].lower()

        strategy = self.get_object()

        if strategy.name == 'LOXBARS':
            loxbars.delay(ticker, parameters['parameter1'], parameters['parameter2'],
                           parameters['parameter3'], strategy.id, parameters)

        elif strategy.name == 'PREVRANGE':
            prevrange.delay(ticker, parameters['parameter1'], parameters['parameter2'],
                            strategy.id, parameters)

        elif strategy.name == 'MATREND':
            matrend.delay(ticker, parameters['parameter1'], strategy.id, parameters)

        return super().form_valid(form)


def backtest_in_progress(request):
    return render(request, 'strategies/backtest-in-progress.html')


def all_results(request):
    results = BacktestResults.objects.all().order_by('-finish_time')

    strategy_data = []
    for strategy in results:
        strategy_data.append({
            'ticker': strategy.ticker.upper(),
            'strategy': strategy.name,
            'parameter1': strategy.parameter_values['parameter1'],
            'parameter2': strategy.parameter_values['parameter2'],
            'parameter3': strategy.parameter_values['parameter3'],
            'graph': plot_pnl(strategy.pnl_results['cumsum']),
            'biggest_loss': strategy.pnl_results['biggest_loss'],
            'biggest_win': strategy.pnl_results['biggest_win'],
            'avg_pnl': strategy.pnl_results['avg_pnl'],
            'backtest_finished': strategy.finish_time,
            'results_id': strategy.id
        })
    return render(request, 'results/results.html', {'strategy_data': strategy_data})


def add_strategy_to_portfolio(request, pk):
    strategy = get_object_or_404(BacktestResults, pk=pk)

    if not Portfolio.objects.filter(results_id=strategy.id).exists():
        portfolio_item = Portfolio(
            ticker=strategy.ticker.upper(),
            name=strategy.name,
            parameter_values=strategy.parameter_values,
            results_id=strategy.id
        )

        portfolio_item.save()

        return render(request, 'portfolio/portfolio-add-strategy.html', {'message': 'Portfolio is updated!'})

    return render(request, 'portfolio/portfolio-add-strategy.html', {'message': 'Strategy already exists in portfolio!'})


def portfolio_view(request):
    portfolio = Portfolio.objects.order_by('-added_at')

    deployed_strategies = []
    inactive_strategies = []
    for folio in portfolio:
        item = {
            'ticker': folio.ticker,
            'name': folio.name,
            'parameter1': folio.parameter_values['parameter1'],
            'parameter2': folio.parameter_values['parameter2'],
            'parameter3': folio.parameter_values['parameter3'],
            'id': folio.id,
            'deployed': folio.deployed
        }

        if folio.deployed:
            deployed_strategies.append(item)
        else:
            inactive_strategies.append(item)

    return render(request, 'portfolio/portfolio.html', {
        'deployed_strategies': deployed_strategies,
        'inactive_strategies': inactive_strategies
    })


def added_strategy(request):
    return render(request, 'portfolio/portfolio-add-strategy.html')


def deploy_strategy(request, pk):
    strategy = get_object_or_404(Portfolio, pk=pk)

    if not Portfolio.objects.filter(ticker=strategy.ticker, deployed=True).exists():
        exchange, month, client_id = contract_trading_specs(strategy.ticker)

        order_strategy = SimpleOrderStrategy(strategy.ticker, exchange, month, client_id)
        order_strategy.place_order()

        strategy.deployed = True
        strategy.save()
        return render(request, 'portfolio/portfolio-deploy-strategy.html',
                      {'message': f'Strategy is deployed!'})
    else:
        return render(request, 'portfolio/portfolio-deploy-strategy.html',
                      {
                          'message': f"Strategy can't be deployed because there is already a deployed strategy with ticker {strategy.ticker}."})


def stop_strategy(request, pk):
    strategy = get_object_or_404(Portfolio, pk=pk)
    strategy.deployed = False
    strategy.save()

    return render(request, 'portfolio/portfolio-stop-strategy.html',
                  {'message': f'Strategy for ticker {strategy.ticker} is stopped!'})


def remove_strategy(request, pk):
    strategy = get_object_or_404(Portfolio, pk=pk)
    strategy.delete()

    return render(request, 'portfolio/portfolio-remove-strategy.html',
                  {'message': f'Strategy for ticker {strategy.ticker} has been removed!'})


@require_POST
def update_historical_data(request):
    get_historical_data.delay()
    messages.info(request, 'Scheduled for update')
    return render(request, 'tws_connection/connection.html')
