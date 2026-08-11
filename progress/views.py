import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.utils.translation import gettext_lazy as _

from common.logging.audit import AuditLogger
from progress.forms import RecordCreateForm
from progress.models import ProgresTracking
from progress.services import ProgressAnalyticsService

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
        context['analytics'] = (ProgressAnalyticsService.get_progress_summary(
                self.request.user
            )
        )
        return context


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-create.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        form.instance.owner = self.request.user

        response = super().form_valid(form)

        AuditLogger.progress_record_created(
            user=self.request.user,
            record=self.object,
        )

        profile = self.request.user.profile

        if profile and not profile.starting_weight:
            profile.starting_weight = self.object.weight
            profile.save(update_fields=['starting_weight'])

        ProgressAnalyticsService.invalidate_cache(self.request.user)

        messages.success(self.request, _('Record has been created successfully!'))
        return response


class RecordEditView(UpdateView):
    model = ProgresTracking
    form_class = RecordCreateForm
    template_name = 'progress/record/record-edit.html'
    success_url = reverse_lazy('progress:overview')

    def form_valid(self, form):
        response = super().form_valid(form)

        ProgressAnalyticsService.invalidate_cache(self.request.user)

        AuditLogger.progress_record_updated(
            user=self.request.user,
            record=self.object,
        )

        messages.success(
            self.request,
            _('Record has been updated successfully!')
        )

        return response

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


    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user).order_by('-date')


class RecordDeleteView(DeleteView):
    model = ProgresTracking
    template_name = 'progress/record/record-delete.html'
    context_object_name = 'record'
    success_url = reverse_lazy('progress:overview')

    def delete(self, request, *args, **kwargs):
        record = self.get_object()

        record_id = record.pk
        record_weight = record.weight
        record_date = record.date
        record_day = record.day

        response = super().delete(request, *args, **kwargs)

        ProgressAnalyticsService.invalidate_cache(self.request.user)

        AuditLogger.progress_record_deleted(
            user=request.user,
            record_id=record_id,
            day=record_day,
            date=record_date,
            weight=record_weight,
        )

        messages.success(
            request,
            _("Record has been deleted successfully!")
        )

        return response

    def get_queryset(self):
        return ProgresTracking.objects.filter(owner=self.request.user)


