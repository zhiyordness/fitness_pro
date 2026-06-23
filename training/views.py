import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import IntegerField, When, Case
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView
from choices import WeekDaysChoices, WorkoutSessionStatus
from common.mixins import StaffRequiredMixin
from training.forms import TrainingDayCreateForm, ExerciseCreateForm, TrainingDayExerciseForm, WorkoutSetEditForm
from training.models import TrainingDay, Exercise, MuscleGroup, TrainingDayExercise, WorkoutSession, WorkoutSet
from training.services import TrainingDayService, WorkoutSessionService, WorkoutStatisticsService, PersonalRecordService
from django.utils.translation import gettext_lazy as _
from django.utils import timezone



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
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()

        exercise_ids = self.request.POST.get('selected_exercises', '')

        if exercise_ids:
            exercise_id_list = [
                int(id.strip())
                for id in exercise_ids.split(',')
                if id.strip()
            ]

            for order, exercise_id in enumerate(
                    exercise_id_list,
                    start=1,
            ):
                exercise = Exercise.objects.get(
                    pk=exercise_id
                )

                TrainingDayExercise.objects.create(
                    training_day=self.object,
                    exercise=exercise,
                    custom_sets=exercise.sets,
                    custom_repetitions=exercise.repetitions,
                    order=order,
                )

            muscle_groups = MuscleGroup.objects.filter(
                muscles__exercises__id__in=exercise_id_list
            ).distinct()

            self.object.muscle_groups.set(muscle_groups)

        messages.success(self.request, _('The training day has been created successfully!'))
        return super().form_valid(form)

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

        exercise_ids = self.request.POST.get(
            'selected_exercises',
            '',
        )

        if exercise_ids:
            exercise_id_list = [
                int(id.strip())
                for id in exercise_ids.split(',')
                if id.strip()
            ]

            TrainingDayExercise.objects.filter(
                training_day=self.object
            ).delete()

            for order, exercise_id in enumerate(
                    exercise_id_list,
                    start=1,
            ):
                exercise = Exercise.objects.get(
                    pk=exercise_id
                )

                TrainingDayExercise.objects.create(
                    training_day=self.object,
                    exercise=exercise,
                    custom_sets=exercise.sets,
                    custom_repetitions=exercise.repetitions,
                    order=order,
                )

            muscle_groups = MuscleGroup.objects.filter(
                muscles__exercises__id__in=exercise_id_list
            ).distinct()

            self.object.muscle_groups.set(
                muscle_groups
            )

        else:
            TrainingDayExercise.objects.filter(
                training_day=self.object
            ).delete()

            self.object.muscle_groups.clear()

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
        messages.success(self.request, _('Split has been deleted successfully!'))
        return super().delete(request, *args, **kwargs)

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
        messages.success(self.request, _('Exercise has been created successfully!'))
        return super().form_valid(form)


class ExerciseEditView(StaffRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/exercise/exercise_edit.html'

    def form_valid(self, form):
        messages.success(self.request, _('Exercise has been updated successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trainings:exercise-details', kwargs={'pk': self.object.pk})


class ExerciseDeleteView(StaffRequiredMixin, DeleteView):
    model = Exercise
    success_url = reverse_lazy('trainings:exercise-list')
    template_name = 'training/exercise/exercise-delete.html'

    def delete(self, form, *args, **kwargs):
        messages.success(self.request, _('Exercise has been deleted successfully!'))
        return super().delete(form, *args, **kwargs)


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
        messages.success(
            self.request,
            _('Exercise configuration updated successfully!')
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'trainings:details',
            kwargs={
                'pk': self.object.training_day.pk
            }
        )

class TrainingDayExerciseMoveUpView(LoginRequiredMixin, View):

    def get(self, request, pk):

        exercise = get_object_or_404(
            TrainingDayExercise,
            pk=pk,
            training_day__owner=request.user,
        )

        previous_exercise = (
            TrainingDayExercise.objects.filter(
                training_day=exercise.training_day,
                order__lt=exercise.order,
            )
            .order_by('-order')
            .first()
        )

        if previous_exercise:
            TrainingDayService.swap_exercise_order(
                exercise,
                previous_exercise,
            )

        return redirect('trainings:details', pk=exercise.training_day.pk,)


class TrainingDayExerciseMoveDownView(LoginRequiredMixin, View,):

    def get(self, request, pk):

        exercise = get_object_or_404(
            TrainingDayExercise,
            pk=pk,
            training_day__owner=request.user,
        )

        next_exercise = (
            TrainingDayExercise.objects.filter(
                training_day=exercise.training_day,
                order__gt=exercise.order,
            )
            .order_by('order')
            .first()
        )

        if next_exercise:
            TrainingDayService.swap_exercise_order(
                exercise,
                next_exercise,
            )

        return redirect('trainings:details', pk=exercise.training_day.pk,)


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

        WorkoutSessionService.check_and_finish_workout(
            workout_set
            .exercise_session
            .workout_session
        )

        return redirect(
            'trainings:workout-session-details',
            pk=(
                workout_set
                .exercise_session
                .workout_session
                .pk
            ),
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

