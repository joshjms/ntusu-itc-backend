from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from markdown2 import markdown
from docs.forms import MarkdownForm
from docs.utils import list_entries, get_entry, save_entry


class HomePageView(TemplateView):
    template_name = 'docs/home.html'


class ListView(TemplateView):
    template_name = 'docs/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['entries'] = list_entries()
        return context


class CreateView(FormView):
    template_name = 'docs/edit.html'
    form_class = MarkdownForm

    def form_valid(self, form):
        self.title = form.cleaned_data['title']
        content = form.cleaned_data['content']
        save_entry(self.title, content)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('docs:detail', args=(self.title,))


class DetailView(TemplateView):
    template_name = 'docs/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = (markdown(get_entry(kwargs['title'])) if
            get_entry(kwargs['title']) else None)
        return context


class EditView(CreateView):
    def get_initial(self):
        return {
            'title': self.kwargs['title'],
            'content': get_entry(self.kwargs['title'])
        }
