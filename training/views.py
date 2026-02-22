import json
import re

from django.contrib import messages
from django.db.models import IntegerField, When, Case
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView

from choices import WeekDaysChoices
from training.forms import TrainingDayCreateForm, ExerciseCreateForm
from training.models import TrainingDay, Exercise, MuscleGroup


# Create your views here.
class TrainingDayListView(ListView):
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
        return TrainingDay.objects.annotate(
            days_order=Case(*order_days, output_field=IntegerField())
        ).order_by('days_order').prefetch_related(
            'muscle_groups',
            'exercises'
        ).all()



class TrainingDayDetailsView(DetailView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-details.html'
    context_object_name = 'training_day'

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_day = self.object

        context['muscle_groups'] = training_day.muscle_groups.all()
        context['exercises'] = training_day.exercises.all()

        return context


class TrainingDayCreateView(CreateView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-create.html'


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        muscle_group_ids = self.request.POST.getlist('muscle_groups')
        if muscle_group_ids:
            self.object.muscle_groups.set(muscle_group_ids)

        exercise_ids = self.request.POST.get('selected_exercises', '')
        if exercise_ids:
            exercise_id_list = [int(id.strip()) for id in exercise_ids.split(',') if id.strip()]
            if exercise_id_list:
                self.object.exercises.set(exercise_id_list)

        messages.success(self.request, 'The training day has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['muscle_groups'] = MuscleGroup.objects.all()

        muscle_groups = MuscleGroup.objects.prefetch_related('muscles__exercises').all()

        muscle_data = {}
        for group in muscle_groups:
            muscle_data[group.id] = {
                'id': group.id,
                'name': group.name,
                'muscles': {}
            }
            for muscle in group.muscles.all():
                muscle_data[group.id]['muscles'][muscle.id] = {
                    'id': muscle.id,
                    'name': muscle.name,
                    'exercises': {}
                }
                for exercise in muscle.exercises.all():
                    muscle_data[group.id]['muscles'][muscle.id]['exercises'][exercise.id] = {
                        'id': exercise.id,
                        'name': exercise.name,
                        'sets': exercise.sets,
                        'repetitions': exercise.repetitions
                    }

        context['muscle_data_json'] = json.dumps(muscle_data)
        return context


class TrainingDayEditView(UpdateView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training_day/training-day-edit.html'
    context_object_name = 'training_day'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_day = self.object
        context['muscle_groups'] = MuscleGroup.objects.all()
        context['selected_muscle_groups'] = list(training_day.muscle_groups.values_list('id', flat=True))

        muscle_groups = MuscleGroup.objects.prefetch_related('muscles__exercises').all()
        muscle_data = {}

        for group in muscle_groups:
            muscle_data[group.id] = {
                'id': group.id,
                'name': group.name,
                'muscles': {}
            }
            for muscle in group.muscles.all():
                muscle_data[group.id]['muscles'][muscle.id] = {
                    'id': muscle.id,
                    'name': muscle.name,
                    'exercises': {}
                }
                for exercise in muscle.exercises.all():
                    muscle_data[group.id]['muscles'][muscle.id]['exercises'][exercise.id] = {
                        'id': exercise.id,
                        'name': exercise.name,
                        'sets': exercise.sets,
                        'repetitions': exercise.repetitions
                    }
        context['muscle_data_json'] = json.dumps(muscle_data)

        selected_exercises = training_day.exercises.select_related().all()

        enhanced_exercises = []
        for exercise in selected_exercises:
            for group in muscle_groups:
                for muscle in group.muscles.all():
                    if exercise in muscle.exercises.all():
                        enhanced_exercises.append({
                            'id': exercise.id,
                            'name': exercise.name,
                            'sets': exercise.sets,
                            'repetitions': exercise.repetitions,
                            'muscle_name': muscle.name,
                            'group_name': group.name
                        })
                        break
                else:
                    continue
                break
        context['selected_exercises_json'] = json.dumps(enhanced_exercises)

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        muscle_group_ids = self.request.POST.getlist('muscle_groups')
        if muscle_group_ids:
            self.object.muscle_groups.set(muscle_group_ids)

        exercise_ids = self.request.POST.get('selected_exercises', '')
        if exercise_ids:
            exercise_id_list = [int(id.strip()) for id in exercise_ids.split(',') if id.strip()]
            if exercise_id_list:
                self.object.exercises.set(exercise_id_list)
        else:
            self.object.exercises.clear()

        messages.success(self.request, f'The training day has been updated successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('trainings:details', kwargs={'pk': self.object.pk})



class TrainingDayDeleteView(DeleteView):
    model = TrainingDay
    success_url = reverse_lazy('trainings:list')
    template_name = 'training/training_day/training-day-delete.html'

    def delete(self, form, *args, **kwargs):
        messages.success(self.request, 'Split has been deleted successfully!')
        return super().delete(form, *args, **kwargs)


class ExerciseListView(ListView):
    model = Exercise
    template_name = 'training/exercise/exercises-list.html'
    context_object_name = 'exercises'
    paginate_by = 9

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


class ExerciseCreateView(CreateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/training_day/training-day-add-exercise.html'
    success_url = reverse_lazy('trainings:list')

    def form_valid(self, form):
        messages.success(self.request, 'Exercise has been created successfully!')
        return super().form_valid(form)


class ExerciseEditView(UpdateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/exercise/exercise_edit.html'

    def form_valid(self, form):
        messages.success(self.request, 'Exercise has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trainings:exercise-details', kwargs={'pk': self.object.pk})


class ExerciseDeleteView(DeleteView):
    model = Exercise
    success_url = reverse_lazy('trainings:exercise-list')
    template_name = 'training/exercise/exercise-delete.html'

    def delete(self, form, *args, **kwargs):
        messages.success(self.request, 'Exercise has been deleted successfully!')
        return super().delete(form, *args, **kwargs)


class ExerciseDetailsView(DetailView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/exercise/exercise_details.html'
    context_object_name = 'exercise'

    def get_success_url(self):
        return reverse_lazy('trainings:exercise-details', kwargs={'pk': self.object.pk})