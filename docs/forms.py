from django import forms


class MarkdownForm(forms.Form):
    title = forms.CharField(label="Title", max_length=50)
    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Enter markdown here...',
        'rows': 30,
        'style': 'width: 90%;'
    }))

    def clean_title(self):
        return self.cleaned_data['title'].lower()
