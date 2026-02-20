from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from progress.forms import RecordCreateForm
from progress.models import ProgresTracking




def progress_overview(request: HttpRequest) -> HttpResponse:
    last_record = ProgresTracking.objects.all().order_by('-date').first()

    context = {
        'last_record': last_record,
    }

    return render(request, 'progress/progress-overview.html', context)



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


def record_details(request: HttpRequest, pk: int) -> HttpResponse:
    record = ProgresTracking.objects.get(pk=pk)

    context = {
        'record': record,
    }

    return render(request, 'progress/record/record-details.html', context)

class RecordListView(ListView):
    model = ProgresTracking
    template_name = 'progress/record/records-list.html'
    context_object_name = 'record'
    paginate_by = 1
    ordering = ['-day']

# def records_list(request: HttpRequest) -> HttpResponse:
#     all_records = ProgresTracking.objects.all().order_by('-day')
#
#     context = {
#         'object_list': all_records,
#     }
#
#     return render(request, 'progress/record/records-list.html', context)


class RecordDeleteView(DeleteView):
    model = ProgresTracking
    template_name = 'progress/record/record-delete.html'
    context_object_name = 'record'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, 'Record has been deleted successfully!')
        return super().form_valid(form)