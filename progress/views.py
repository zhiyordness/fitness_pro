from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from progress.forms import RecordCreateForm
from progress.models import ProgresTracking



class ProgressOverviewView(ListView):
    model = ProgresTracking
    template_name = 'progress/progress-overview.html'
    context_object_name = 'last_record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_record'] = ProgresTracking.objects.all().order_by('-date').first()
        return context


class RecordCreateView(CreateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-create.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, 'Record has been created successfully!')
        return super().form_valid(form)


class RecordEditView(UpdateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-edit.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, 'Record has been updated successfully!')
        return super().form_valid(form)


class RecordDetailsView(ListView):
    model = ProgresTracking
    template_name = 'progress/record/record-details.html'
    context_object_name = 'record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['record'] = ProgresTracking.objects.get(pk=self.kwargs['pk'])
        return context


class RecordListView(ListView):
    model = ProgresTracking
    template_name = 'progress/record/records-list.html'
    context_object_name = 'record'
    paginate_by = 1
    ordering = ['-day']


class RecordDeleteView(DeleteView):
    model = ProgresTracking
    template_name = 'progress/record/record-delete.html'
    context_object_name = 'record'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, 'Record has been deleted successfully!')
        return super().form_valid(form)
