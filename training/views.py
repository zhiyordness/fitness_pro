import logging

import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import IntegerField, When, Case
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView
from choices import WeekDaysChoices, WorkoutSessionStatus
from common.logging.audit import AuditLogger
from common.mixins import StaffRequiredMixin
from training.forms import TrainingDayCreateForm, ExerciseCreateForm, TrainingDayExerciseForm, WorkoutSetEditForm
from training.models import TrainingDay, Exercise, MuscleGroup, TrainingDayExercise, WorkoutSession, WorkoutSet
from training.services import TrainingDayService, WorkoutSessionService, WorkoutStatisticsService, PersonalRecordService
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


logger = logging.getLogger(__name__)

from django.utils import timezone


class TrainingDayListView(LoginRequiredMixin, ListView):
    model = TrainingDay
    template_name = 'training/training_day/training-days-list.html'
    context_object_name = 'training_splits'

    def get_queryset(self):
        order_days = [
            When(day=WeekDaysChoices.MONDAY, then=1),
            When(day=WeekDaysChoices.TUESDAY, then=2),
            When(day=WeekDaysChoices.WEDNESDAY, then=3),
            When(day=WeekDaysChoices.THURSDAY, then=4),
            When(day=WeekDaysChoices.FRIDAY, then=5),
            When(day=WeekDaysChoices.SATURDAY, then=6),
            When(day=WeekDaysChoices.SUNDAY, then=7),
        ]

        return TrainingDay.objects.filter(
            owner=self.request.user
        ).annotate(
            days_order=Case(*order_days, output_field=IntegerField())
        ).order_by(
            'days_order'
        ).prefetch_related(
            'muscle_groups',
            'training_day_exercises__exercise__muscles__group'
        ).select_related(
            'owner'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today_name = timezone.now().strftime('%A')

        training_splits = context['training_splits']

        active_workout_days = set(
            WorkoutSession.objects.filter(
                owner=self.request.user,
                status=WorkoutSessionStatus.STARTED,
            )
            .values_list(
                'training_day_id',
                flat=True,
            )
        )

        for split in training_splits:
            split.has_active_workout = (
                    split.pk in active_workout_days
            )

        active_day = None

        for split in training_splits:
            if split.day == today_name:
                active_day = split.day
                break

        if not active_day and training_splits:
            active_day = training_splits[0].day

        context['active_day'] = active_day

        # print(context['today_name'])

        return context



class TrainingDayDetailsView(LoginRequiredMixin, DetailView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-details.html'
    context_object_name = 'training_day'

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return TrainingDay.objects.filter(
            owner=self.request.user
        ).prefetch_related(
            'muscle_groups',
            'training_day_exercises__exercise__muscles__group',
        ).select_related(
            'owner'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_day = self.object

        context['muscle_groups'] = training_day.muscle_groups.all()
        context['training_day_exercises'] = (
            training_day.training_day_exercises.select_related(
                'exercise'
            ).prefetch_related(
                'exercise__muscles'
            ).order_by('order')
        )

        context['has_active_workout'] = (
                WorkoutSessionService
                .get_active_workout_session(
                    user=self.request.user,
                    training_day=training_day,
                )
                is not None
        )

        context['exercises_by_muscle'] = (
            TrainingDayService.build_exercises_by_muscle(
                training_day
            )
        )

        return context


class TrainingDayCreateView(LoginRequiredMixin, CreateView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-create.html'


    def form_valid(self, form):
        training_day = form.save(commit=False)
        training_day.owner = self.request.user
        training_day.save()

        self.object = training_day

        selected_exercise_ids = self.request.POST.get(
            'selected_exercises',
            '',
        )

        if selected_exercise_ids:
            exercise_id_list = [
                int(exercise_id.strip())
                for exercise_id in selected_exercise_ids.split(',')
                if exercise_id.strip()
            ]

            TrainingDayService.configure_training_day(
                training_day=training_day,
                exercise_id_list=exercise_id_list,
            )

        AuditLogger.training_day_created(
            user=self.request.user,
            training_day=training_day,
        )

        messages.success(self.request, _('The training day has been created successfully!'))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['muscle_groups'] = MuscleGroup.objects.all()

        muscle_groups = MuscleGroup.objects.prefetch_related('muscles__exercises').all()

        context['muscle_data_json'] = (
            TrainingDayService.build_muscle_data(muscle_groups)
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs


class TrainingDayEditView(LoginRequiredMixin, UpdateView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-edit.html'
    context_object_name = 'training_day'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_day = self.object

        context['muscle_groups'] = MuscleGroup.objects.all()

        muscle_groups = MuscleGroup.objects.prefetch_related('muscles__exercises').all()

        context['muscle_data_json'] = (
            TrainingDayService.build_muscle_data(muscle_groups)
        )

        selected_exercises = [
            item.exercise
            for item in training_day.training_day_exercises.select_related(
                'exercise'
            )
        ]

        context['selected_exercises_json'] = (
            TrainingDayService.build_selected_exercises(
                selected_exercises, muscle_groups
            )
        )

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        training_day = self.object

        selected_exercise_ids = self.request.POST.get(
            'selected_exercises',
            '',
        )

        TrainingDayService.clear_training_day(
            training_day=training_day,
        )

        if selected_exercise_ids:
            exercise_id_list = [
                int(exercise_id_str.strip())
                for exercise_id_str in selected_exercise_ids.split(',')
                if exercise_id_str.strip()
            ]

            TrainingDayService.configure_training_day(
                training_day=training_day,
                exercise_id_list=exercise_id_list,
            )

        AuditLogger.training_day_updated(
            user=self.request.user,
            training_day=training_day,
        )

        messages.success(
            self.request,
            _('The training day has been updated successfully!')
        )

        return response

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return TrainingDay.objects.filter(owner=self.request.user).prefetch_related(
            'muscle_groups',
            'training_day_exercises__exercise__muscles__group'
        ).select_related('owner')


class TrainingDayDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingDay
    success_url = reverse_lazy('trainings:list')
    template_name = 'training/training_day/training-day-delete.html'

    def delete(self, request, *args, **kwargs):
        training_day = self.get_object()

        training_day_id = training_day.pk
        training_day_name = training_day.day
        training_day_description = training_day.description

        response = super().delete(request, *args, **kwargs)

        AuditLogger.training_day_deleted(
            user=request.user,
            training_day_id=training_day_id,
            day_name=training_day_name,
            description=training_day_description,
        )

        messages.success(
            request,
            _("Split has been deleted successfully!")
        )

        return response

    def get_queryset(self):
        return TrainingDay.objects.filter(owner=self.request.user).prefetch_related(
            'muscle_groups',
            'training_day_exercises__exercise__muscles__group'
        ).select_related('owner')



class ExerciseListView(ListView):
    model = Exercise
    template_name = 'training/exercise/exercises-list.html'
    context_object_name = 'exercises'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query) | queryset.filter(muscles__name__icontains=query)
        return queryset.distinct().prefetch_related('muscles').order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ExerciseCreateView(StaffRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/training_day/training-day-add-exercise.html'
    success_url = reverse_lazy('trainings:list')

    def form_valid(self, form):
        response = super().form_valid(form)

        AuditLogger.exercise_created(
            user=self.request.user,
            exercise=self.object,
        )

        messages.success(
            self.request,
            _("Exercise has been created successfully!")
        )

        return response


class ExerciseEditView(StaffRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/exercise/exercise_edit.html'

    def form_valid(self, form):

        response = super().form_valid(form)

        AuditLogger.exercise_updated(
            user=self.request.user,
            exercise=self.object,
        )

        messages.success(self.request, _('Exercise has been updated successfully!'))

        return response

    def get_success_url(self):
        return reverse_lazy('trainings:exercise-details', kwargs={'pk': self.object.pk})


class ExerciseDeleteView(StaffRequiredMixin, DeleteView):
    model = Exercise
    success_url = reverse_lazy('trainings:exercise-list')
    template_name = 'training/exercise/exercise-delete.html'

    def delete(self, request, *args, **kwargs):
        exercise = self.get_object()

        exercise_id = exercise.pk
        exercise_name = exercise.name
        exercise_sets = exercise.sets
        exercise_repetitions = exercise.repetitions

        response = super().delete(request, *args, **kwargs)

        AuditLogger.exercise_deleted(
            user=request.user,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            exercise_sets=exercise_sets,
            exercise_repetitions=exercise_repetitions,
        )

        messages.success(
            request,
            _("Exercise has been deleted successfully!")
        )

        return response


class ExerciseDetailsView(DetailView):
    model = Exercise
    template_name = 'training/exercise/exercise_details.html'
    context_object_name = 'exercise'


class TrainingDayExerciseEditView(
    LoginRequiredMixin,
    UpdateView,
):
    model = TrainingDayExercise

    form_class = TrainingDayExerciseForm

    template_name = (
        'training/training_day/training-day-exercise-edit.html'
    )

    context_object_name = 'training_day_exercise'

    def get_queryset(self):
        return TrainingDayExercise.objects.filter(
            training_day__owner=self.request.user
        ).select_related(
            'training_day',
            'exercise',
        )

    def form_valid(self, form):

        response = super().form_valid(form)

        AuditLogger.training_day_exercise_updated(
            user=self.request.user,
            training_day_exercise=self.object,
        )

        messages.success(
            self.request,
            _('Exercise configuration updated successfully!')
        )

        return response

    def get_success_url(self):
        return reverse_lazy(
            'trainings:details',
            kwargs={
                'pk': self.object.training_day.pk
            }
        )

class TrainingDayExerciseMoveUpView(LoginRequiredMixin, View):

    def get(self, request, pk):

        training_day_exercise = get_object_or_404(
            TrainingDayExercise,
            pk=pk,
            training_day__owner=request.user,
        )

        previous_training_day_exercise = (
            TrainingDayExercise.objects.filter(
                training_day=training_day_exercise.training_day,
                order__lt=training_day_exercise.order,
            )
            .order_by('-order')
            .first()
        )

        if previous_training_day_exercise:
            TrainingDayService.swap_exercise_order(
                training_day_exercise,
                previous_training_day_exercise,
            )
            AuditLogger.training_day_exercise_moved_up(
                user=request.user,
                training_day_exercise=training_day_exercise,
            )

        training_day = training_day_exercise.training_day

        return redirect('trainings:details', pk=training_day.pk,)


class TrainingDayExerciseMoveDownView(LoginRequiredMixin, View,):

    def get(self, request, pk):

        training_day_exercise = get_object_or_404(
            TrainingDayExercise,
            pk=pk,
            training_day__owner=request.user,
        )

        next_training_day_exercise = (
            TrainingDayExercise.objects.filter(
                training_day=training_day_exercise.training_day,
                order__gt=training_day_exercise.order,
            )
            .order_by('order')
            .first()
        )

        if next_training_day_exercise:
            TrainingDayService.swap_exercise_order(
                training_day_exercise,
                next_training_day_exercise,
            )
            AuditLogger.training_day_exercise_moved_down(
                user=request.user,
                training_day_exercise=training_day_exercise,
            )

        return redirect('trainings:details', pk=training_day_exercise.training_day.pk,)


class WorkoutStartView(LoginRequiredMixin, View):

    def post(
            self,
            request,
            pk,
            *args,
            **kwargs,
    ):
        training_day = get_object_or_404(
            TrainingDay,
            pk=pk,
            owner=request.user,
        )

        workout_session = (
            WorkoutSessionService.start_workout(
                user=request.user,
                training_day=training_day,
            )
        )

        AuditLogger.workout_started(
            user=request.user,
            workout_session=workout_session,
        )

        return redirect(
            'trainings:workout-session-details',
            pk=workout_session.pk,
        )



class WorkoutSessionDetailsView(LoginRequiredMixin, DetailView):
    model = WorkoutSession

    template_name = (
        'training/workout_session/workout-session-details.html'
    )

    context_object_name = 'workout_session'

    def get_queryset(self):
        return (
            WorkoutSession.objects.filter(
                owner=self.request.user,
            )
            .select_related(
                'training_day',
            )
            .prefetch_related(
                'exercise_sessions__training_day_exercise__exercise',
                'exercise_sessions__sets',
            )
        )


class WorkoutSetCompleteView(LoginRequiredMixin, View):

    def post(
            self,
            request,
            pk,
            *args,
            **kwargs,
    ):
        workout_set = get_object_or_404(
            WorkoutSet.objects.select_related(
                'exercise_session__workout_session',
                'exercise_session__training_day_exercise__exercise'
            ),
            pk=pk,
            exercise_session__workout_session__owner=request.user,
        )

        workout_set.is_completed = True
        workout_set.save(
            update_fields=['is_completed']
        )

        PersonalRecordService.update_personal_record(
            workout_set
        )

        workout_session = workout_set.exercise_session.workout_session

        WorkoutSessionService.check_and_finish_workout(
            workout_session
        )

        AuditLogger.workout_set_completed(
            user=request.user,
            workout_set=workout_set,
        )

        return redirect(
            'trainings:workout-session-details',
            pk=workout_session.pk,
        )


class WorkoutSetEditView(LoginRequiredMixin, UpdateView):
    model = WorkoutSet

    form_class = WorkoutSetEditForm

    template_name = (
        'training/workout_session/workout-set-edit.html'
    )

    def get_queryset(self):
        return WorkoutSet.objects.filter(
            exercise_session__workout_session__owner=
            self.request.user
        )

    def get_success_url(self):
        return reverse_lazy(
            'trainings:workout-session-details',
            kwargs={
                'pk': (
                    self.object
                    .exercise_session
                    .workout_session
                    .pk
                )
            }
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        logger.info(
            "Workout set updated.",
            extra={
                "user_id": self.request.user.pk,
                "workout_set_id": self.object.pk,
            },
        )

        return response


class WorkoutSessionFinishView(LoginRequiredMixin, View):

    def post(
            self,
            request,
            pk,
            *args,
            **kwargs,
    ):
        workout_session = get_object_or_404(
            WorkoutSession,
            pk=pk,
            owner=request.user,
        )

        has_completed_sets = (
            WorkoutSessionService.has_completed_sets(
                workout_session
            )
        )

        if not has_completed_sets:
            messages.warning(
                request,
                (
                    'You have not completed any sets. '
                    'Please complete at least one set '
                    'or cancel the workout.'
                )
            )
            return redirect(
                'trainings:workout-session-details',
                pk=workout_session.pk,
            )

        workout_session.status = (
            WorkoutSessionStatus.COMPLETED
        )

        workout_session.finished_at = (
            timezone.now()
        )

        workout_session.save(
            update_fields=[
                'status',
                'finished_at',
            ]
        )

        AuditLogger.workout_finished(
            user=request.user,
            workout_session=workout_session,
        )

        messages.success(
            request,
            _("Workout session finished successfully!")
        )

        return redirect(
            'trainings:list',
        )


class WorkoutSessionCancelView(
    LoginRequiredMixin,
    View,
):

    def post(
            self,
            request,
            pk,
            *args,
            **kwargs,
    ):
        workout_session = get_object_or_404(
            WorkoutSession,
            pk=pk,
            owner=request.user,
            status=WorkoutSessionStatus.STARTED,
        )

        workout_session.status = (
            WorkoutSessionStatus.CANCELLED
        )

        workout_session.save(
            update_fields=[
                'status',
            ]
        )

        AuditLogger.workout_cancelled(
            user=request.user,
            workout_session=workout_session,
        )

        messages.info(
            request,
            'Workout session cancelled.'
        )

        return redirect(
            'trainings:list',
        )


class WorkoutHistoryView(ListView):
    model = WorkoutSession

    template_name = 'training/history/workout-history.html'

    context_object_name = 'workout_sessions'

    def get_queryset(self):
        return WorkoutSession.objects.filter(
            owner=self.request.user,
            status=WorkoutSessionStatus.COMPLETED,
        ).order_by('-started_at')


class WorkoutHistoryDetailsView(LoginRequiredMixin, DetailView):
    model = WorkoutSession

    template_name = (
        'training/history/workout-history-details.html'
    )

    context_object_name = 'workout_session'

    def get_queryset(self):
        return (
            WorkoutSession.objects.filter(
                owner=self.request.user,
                status=WorkoutSessionStatus.COMPLETED,
            )
            .select_related(
                'training_day',
            )
            .prefetch_related(
                'exercise_sessions__training_day_exercise__exercise',
                'exercise_sessions__sets',
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        context['statistics'] = (
            WorkoutStatisticsService
            .get_workout_statistics(
                self.object
            )
        )

        return context

