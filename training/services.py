import json

class TrainingDayService:

    @staticmethod
    def build_muscle_data(muscle_groups):

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
                        'repetitions': exercise.repetitions,
                    }
        return json.dumps(muscle_data)

    @staticmethod
    def build_selected_exercises(selected_exercises, muscle_groups):
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
        return json.dumps(enhanced_exercises)

    @staticmethod
    def build_exercises_by_muscle(training_day):
        exercises_by_muscle = {}

        for training_day_exercise in (
                training_day.training_day_exercises.all()
        ):
            exercise = training_day_exercise.exercise

            for muscle in exercise.muscles.all():

                if muscle.name not in exercises_by_muscle:
                    exercises_by_muscle[muscle.name] = []

                exercises_by_muscle[muscle.name].append(
                    training_day_exercise
                )

        return exercises_by_muscle

    @staticmethod
    def swap_exercise_order(current_exercise, target_exercise,):
        current_order = current_exercise.order

        current_exercise.order = target_exercise.order
        target_exercise.order = current_order

        current_exercise.save()
        target_exercise.save()