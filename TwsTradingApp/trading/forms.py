from django import forms

from TwsTradingApp.trading.models import Strategy, Feedback


class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'parameter1', 'parameter2', 'parameter3', 'symbol']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.HiddenInput()

        if self.instance.name == 'LOXBARS':
            pass
        elif self.instance.name == 'PREVRANGE':
            self.fields['parameter3'].widget = forms.HiddenInput()
        elif self.instance.name == 'MATREND':
            self.fields['parameter2'].widget = forms.HiddenInput()
            self.fields['parameter3'].widget = forms.HiddenInput()


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']








