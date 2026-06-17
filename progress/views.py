from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from progress.forms import RecordCreateForm
from progress.models import ProgresTracking
from django.utils.translation import gettext_lazy as _
UserModel = get_user_model()

class ProgressOverviewView(LoginRequiredMixin, ListView):
    model = ProgresTracking
    template_name = 'progress/progress-overview.html'
    context_object_name = 'last_record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_record'] = ProgresTracking.objects.filter(
            owner=self.request.user
        ).order_by('-date').first()
        return context


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-create.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        form.instance.owner = self.request.user

        response = super().form_valid(form)

        profile = self.request.user.profile

        if profile and not profile.starting_weight:
            profile.starting_weight = self.object.weight
            profile.save(update_fields=['starting_weight'])

        messages.success(self.request, _('Record has been created successfully!'))
        return response


class RecordEditView(UpdateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-edit.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, _('Record has been updated successfully!'))
        return super().form_valid(form)

    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user)


class RecordDetailsView(DetailView):
    model = ProgresTracking
    template_name = 'progress/record/record-details.html'
    context_object_name = 'record'

    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user)


class RecordListView(ListView):
    model = ProgresTracking
    template_name = 'progress/record/records-list.html'
    context_object_name = 'record'
    paginate_by = 8
    ordering = ['-day']

    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user).order_by('-date')


class RecordDeleteView(DeleteView):
    model = ProgresTracking
    template_name = 'progress/record/record-delete.html'
    context_object_name = 'record'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        messages.success(self.request, _('Record has been deleted successfully!'))
        return super().form_valid(form)

    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user)
