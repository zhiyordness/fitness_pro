from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from training.forms import SplitCreateForm
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

def split_details(request: HttpRequest, pk:int) -> HttpResponse:
    training_split = TrainingDay.objects.get(pk=pk)

    if not training_split:
        return redirect('training:split-create')

    context = {
        'training_split': training_split,
    }

    return render(request, 'training/training-details.html', context)




def split_create(request: HttpRequest) -> HttpResponse:
    form = SplitCreateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('training:details')

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


def split_delete(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-delete.html')





def exercise_add(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-add-exercise.html')


def exercise_edit(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-edit.html')


def exercise_delete(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-delete.html')


def exercise_details(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-details.html')