import re

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, CreateView

from training.forms import SplitCreateForm, ExerciseCreateForm
from training.models import TrainingDay, Exercise


# Create your views here.

def split_list(request: HttpRequest) -> HttpResponse:
    training_splits = TrainingDay.objects.prefetch_related('training_muscles__group_of_muscles').all()
    muscle_groups = Exercise.objects.prefetch_related('muscles_group').all()

    context = {
        'training_splits': training_splits,
        'muscle_groups': muscle_groups,
    }

    return render(request, 'training/split/split-list.html', context)

def split_details(request: HttpRequest, pk:int | None) -> HttpResponse:
    training_split = TrainingDay.objects.get(pk=pk)

    context = {
        'training_split': training_split,
    }

    return render(request, 'training/training-details.html', context)




def split_create(request: HttpRequest) -> HttpResponse:
    form = SplitCreateForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('training:split-list')

    context = {
        'form': form,
    }

    return render(request, 'training/split/split-create.html', context)


def split_edit(request: HttpRequest, pk:int) -> HttpResponse:
    split = TrainingDay.objects.get(pk=pk)
    form = SplitCreateForm(request.POST or None, instance=split)

    if request.method == 'POST' and form.is_valid():
        instance = form.save()
        return redirect('training:details', pk=instance.pk)

    context = {
        'form': form,
        'split': split,
    }

    return render(request, 'training/split/split-edit.html', context)


# def split_delete(request: HttpRequest) -> HttpResponse:
#     return render(request, 'training/split/../templates/training/trainingday_confirm_delete.html')

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

def exercise_edit(request: HttpRequest, pk:int) -> HttpResponse:
    exercise = Exercise.objects.get(pk=pk)
    form = ExerciseCreateForm(request.POST or None, request.FILES or None, instance=exercise)

    if request.method == 'POST' and form.is_valid():
        instance = form.save()
        return redirect('training:exercise-details', pk=instance.pk)

    context = {
        'form': form,
        'exercise': exercise,
    }

    return render(request, 'training/exercise/exercise_edit.html', context)


class ExerciseDeleteView(DeleteView):
    model = Exercise
    success_url = reverse_lazy('training:split-list')

    def form_valid(self, form):
        messages.success(self.request, 'Exercise has been deleted successfully!')
        return super().form_valid(form)


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


def exercise_details(request: HttpRequest, pk:int) -> HttpResponse:
    exercise = Exercise.objects.prefetch_related('muscles_group', 'type_of_muscle', 'secondary_muscles', 'split',).get(pk = pk)
    form = ExerciseCreateForm(request.POST or None, instance=exercise)



    if form.is_valid():
        instance = form.save()
        return redirect('training:exercise-details', pk=instance.pk)

    context = {
        'exercise': exercise,
        'form': form,
    }

    return render(request, 'training/exercise/exercise_details.html', context)



