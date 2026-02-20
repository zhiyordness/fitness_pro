import json
import re

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, CreateView, ListView, UpdateView

from training.forms import TrainingDayCreateForm, ExerciseCreateForm
from training.models import TrainingDay, Exercise, MuscleGroup


# Create your views here.
class TrainingDayListView(ListView):
    model = TrainingDay
    template_name = 'training/split/split-list.html'
    context_object_name = 'training_splits'
    queryset = TrainingDay.objects.prefetch_related('muscle_groups', 'exercises').all()



class TrainingDayDetailsView(DetailView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/training-details.html'
    context_object_name = 'split'

    def get_success_url(self):
        return reverse_lazy('training:details', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_day = self.object

        exercises = training_day.exercises.prefetch_related('muscle_groups').all()
        context['exercises'] = exercises

        return context


class TrainingDayCreateView(CreateView):
    model = TrainingDay
    form_class = TrainingDayCreateForm
    template_name = 'training/split/split-create.html'

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
    template_name = 'training/split/split-edit.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        exercises = self.request.POST.getlist('exercises')
        if exercises:
            self.object.exercises.set(exercises)

        messages.success(self.request, f'The training day has been updated successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('training:details', kwargs={'pk': self.object.pk})


class SplitDeleteView(DeleteView):
    model = TrainingDay
    success_url = reverse_lazy('common:home')

    def form_valid(self, form):
        messages.success(self.request, 'Split has been deleted successfully!')
        return super().form_valid(form)


class ExerciseCreateView(CreateView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/split/split-add-exercise.html'
    success_url = reverse_lazy('training:split-list')

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
        return reverse_lazy('training:exercise-details', kwargs={'pk': self.object.pk})


class ExerciseDeleteView(DeleteView):
    model = Exercise
    success_url = reverse_lazy('training:split-list')

    def form_valid(self, form):
        messages.success(self.request, 'Exercise has been deleted successfully!')
        return super().form_valid(form)

    @staticmethod
    def extract_youtube_id(url):
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class ExerciseDetailsView(DetailView):
    model = Exercise
    form_class = ExerciseCreateForm
    template_name = 'training/exercise/exercise_details.html'
    context_object_name = 'exercise'

    def get_success_url(self):
        return reverse_lazy('training:exercise-details', kwargs={'pk': self.object.pk})
