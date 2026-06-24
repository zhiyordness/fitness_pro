import json
from datetime import timedelta

from django.db.models import Sum, ExpressionWrapper, F, DecimalField, Avg, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from choices import WorkoutSessionStatus, WorkoutDayStatus
from training.models import WorkoutSession, WorkoutExerciseSession, WorkoutSet, PersonalRecord, TrainingDay


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


class WorkoutSessionService:

    @staticmethod
    def start_workout(
            user,
            training_day,
    ):
        active_session = (
            WorkoutSessionService
            .get_active_workout_session(
                user=user,
                training_day=training_day,
            )
        )

        if active_session:
            return active_session

        workout_session = WorkoutSession.objects.create(
            owner=user,
            training_day=training_day,
        )

        training_day_exercises = (
            training_day.training_day_exercises.all()
        )

        for training_day_exercise in training_day_exercises:

            exercise_session = (
                WorkoutExerciseSession.objects.create(
                    workout_session=workout_session,
                    training_day_exercise=training_day_exercise,
                    order=training_day_exercise.order,
                )
            )

            for set_number in range(
                    1,
                    training_day_exercise.custom_sets + 1
            ):
                WorkoutSet.objects.create(
                    exercise_session=exercise_session,
                    set_number=set_number,
                    repetitions=(
                        training_day_exercise
                        .custom_repetitions
                    ),
                    weight=0,
                )

        return workout_session

    @staticmethod
    def has_completed_sets(
            workout_session,
    ):
        return WorkoutSet.objects.filter(
            exercise_session__workout_session=workout_session,
            is_completed=True,
        ).exists()

    @staticmethod
    def get_active_workout_session(
            user,
            training_day,
    ):
        return (
            WorkoutSession.objects.filter(
                owner=user,
                training_day=training_day,
                status=WorkoutSessionStatus.STARTED,
            )
            .order_by('-started_at')
            .first()
        )

    @staticmethod
    def check_and_finish_workout(
            workout_session,
    ):
        total_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=
            workout_session,
        ).count()

        completed_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=
            workout_session,
            is_completed=True,
        ).count()

        if total_sets > 0 and total_sets == completed_sets:

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



class WorkoutStatisticsService:

    @staticmethod
    def get_workout_statistics(
            workout_session,
    ):
        exercise_count = (
            workout_session
            .exercise_sessions
            .count()
        )

        total_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=
            workout_session
        ).count()


        completed_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=
            workout_session,
            is_completed=True,
        ).count()

        completion_rate = 0

        if total_sets:
            completion_rate = round(
                completed_sets / total_sets * 100,
                2,
            )

        duration = None

        if workout_session.finished_at:
            duration_delta = (
                    workout_session.finished_at
                    -
                    workout_session.started_at
            )

            total_seconds = int(
                duration_delta.total_seconds()
            )

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours:
                duration = (f'{hours}:{minutes:02d}:{seconds:02d}')
            else:
                duration = (f'{minutes}:{seconds:02d}')

        return {
            'exercise_count': exercise_count,
            'total_sets': total_sets,
            'completed_sets': completed_sets,
            'completion_rate': completion_rate,
            'duration': duration,
        }


class PersonalRecordService:

    @staticmethod
    def update_personal_record(
            workout_set,
    ):
        exercise = (
            workout_set
            .exercise_session
            .training_day_exercise
            .exercise
        )

        owner = (
            workout_set
            .exercise_session
            .workout_session
            .owner
        )

        personal_record = (
            PersonalRecord.objects.filter(
                owner=owner,
                exercise=exercise,
            )
            .first()
        )

        if personal_record is None:

            PersonalRecord.objects.create(
                owner=owner,
                exercise=exercise,
                workout_set=workout_set,
                weight=workout_set.weight,
                repetitions=workout_set.repetitions,
                achieved_at=timezone.now(),
            )

            return

        if workout_set.weight > personal_record.weight:

            personal_record.workout_set = workout_set
            personal_record.weight = workout_set.weight
            personal_record.repetitions = (
                workout_set.repetitions
            )
            personal_record.achieved_at = (
                timezone.now()
            )

            personal_record.save(
                update_fields=[
                    'workout_set',
                    'weight',
                    'repetitions',
                    'achieved_at',
                ]
            )


class TrainingAnalyticsService:

    @staticmethod
    def get_training_overview(user):

        completed_workouts = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.COMPLETED,
            )
        )

        total_workouts = (
            completed_workouts.count()
        )

        total_sets = (
            WorkoutSet.objects.filter(
                exercise_session__workout_session__owner=user,
                is_completed=True,
            ).count()
        )

        total_repetitions = (
            WorkoutSet.objects.filter(
                exercise_session__workout_session__owner=user,
                is_completed=True,
            ).aggregate(
                total=Coalesce(
                    Sum('repetitions'),
                    0,
                )
            )['total']
        )

        total_volume = 0

        completed_sets = (
            WorkoutSet.objects.filter(
                exercise_session__workout_session__owner=user,
                is_completed=True,
            )
        )

        for workout_set in completed_sets:
            total_volume += (
                workout_set.weight *
                workout_set.repetitions
            )

        workout_durations = []

        for workout in completed_workouts:
            if workout.finished_at:

                duration = (
                    workout.finished_at -
                    workout.started_at
                )

                workout_durations.append(
                    duration.total_seconds()
                )

        average_duration = 0

        if workout_durations:
            average_duration = (
                sum(workout_durations)
                /
                len(workout_durations)
            )

        return {
            'total_workouts': total_workouts,
            'total_sets': total_sets,
            'total_repetitions': total_repetitions,
            'total_volume': total_volume,
            'average_duration_seconds': (
                average_duration
            ),
        }


class ExerciseAnalyticsService:

    @staticmethod
    def get_exercise_overview(
            user,
            exercise,
    ):
        completed_sets = (
            WorkoutSet.objects.filter(
                exercise_session__training_day_exercise__exercise=
                exercise,
                exercise_session__workout_session__owner=user,
                is_completed=True,
            )
        )

        total_sets = completed_sets.count()

        total_repetitions = (
            completed_sets.aggregate(
                total=Sum(
                    'repetitions'
                )
            )['total']
            or 0
        )

        total_volume = (
            completed_sets.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F('weight') * F('repetitions'),
                        output_field=DecimalField(),
                    )
                )
            )['total']
            or 0
        )

        average_weight = (
                completed_sets.aggregate(
                    avg=Avg(
                        'weight',
                        filter=Q(
                            weight__gt=0,
                        ),
                    )
                )['avg']
                or 0
        )

        average_repetitions = (
            completed_sets.aggregate(
                avg=Avg('repetitions')
            )['avg']
            or 0
        )

        times_performed = (
            WorkoutExerciseSession.objects.filter(
                training_day_exercise__exercise=exercise,
                workout_session__owner=user,
                workout_session__status=(
                    WorkoutSessionStatus.COMPLETED
                ),
            ).count()
        )

        return {
            'total_sets': total_sets,
            'total_repetitions': total_repetitions,
            'total_volume': total_volume,
            'average_weight': average_weight,
            'average_repetitions': average_repetitions,
            'times_performed': times_performed,
        }

class AdherenceAnalyticsService:

    @staticmethod
    def get_adherence_overview(user):
        completed_workouts = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.COMPLETED,
            ).count()
        )

        cancelled_workouts = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.CANCELLED,
            ).count()
        )

        total_attempts = (
                completed_workouts +
                cancelled_workouts
        )

        completion_rate = 0

        if total_attempts > 0:
            completion_rate = round(
                (
                        completed_workouts /
                        total_attempts
                ) * 100,
                2,
            )

        streak_data = (
            WorkoutStreakService
            .get_streak_overview(
                user
            )
        )

        return {
            'completed_workouts': completed_workouts,
            'cancelled_workouts': cancelled_workouts,
            'total_attempts': total_attempts,
            'completion_rate': completion_rate,

            'current_streak': (
                streak_data['current_streak']
            ),
            'longest_streak': (
                streak_data['longest_streak']
            ),
        }


class WorkoutStreakService:

    @staticmethod
    def get_training_days(user):
        return set(
            TrainingDay.objects.filter(
                owner=user,
            ).values_list(
                'day',
                flat=True,
            )
        )


    @staticmethod
    def get_streak_overview(user):

        expected_training_days = (
            WorkoutStreakService
            .get_expected_training_days(
                user
            )
        )

        current_streak = (
            WorkoutStreakService
            .calculate_current_streak(
                user,
                expected_training_days,
            )
        )

        longest_streak = (
            WorkoutStreakService
            .calculate_longest_streak(
                user,
                expected_training_days,
            )
        )

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
        }

    @staticmethod
    def get_day_status(
            user,
            target_date,
    ):

        weekday = (
            target_date.strftime(
                '%A'
            )
        )

        is_training_day = (
            TrainingDay.objects.filter(
                owner=user,
                day=weekday,
            ).exists()
        )

        if not is_training_day:
            return (
                WorkoutDayStatus.REST
            )

        completed_exists = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.COMPLETED,
                started_at__date=target_date,
            ).exists()
        )

        if completed_exists:
            return (
                WorkoutDayStatus.SUCCESS
            )

        started_exists = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.STARTED,
                started_at__date=target_date,
            ).exists()
        )

        today = (
            timezone.localdate()
        )

        if target_date == today:

            if started_exists:
                return (
                    WorkoutDayStatus.ACTIVE
                )

            return (
                WorkoutDayStatus.PENDING
            )

        return (
            WorkoutDayStatus.FAILED
        )

    @staticmethod
    def debug_today_status(user):

        today = timezone.localdate()

        return (
            WorkoutStreakService
            .get_day_status(
                user,
                today,
            )
        )


    @staticmethod
    def get_first_completed_date(user):

        first_workout = (
            WorkoutSession.objects.filter(
                owner=user,
                status=WorkoutSessionStatus.COMPLETED,
            )
            .order_by(
                'started_at'
            )
            .first()
        )

        if not first_workout:
            return None

        return first_workout.started_at.date()

    @staticmethod
    def get_expected_training_days(
            user,
    ):
        first_date = (
            WorkoutStreakService
            .get_first_completed_date(user)
        )

        if not first_date:
            return []

        training_days = (
            WorkoutStreakService
            .get_training_days(user)
        )

        current_date = first_date

        today = timezone.localdate()

        expected_days = []

        while current_date <= today:

            weekday_name = (
                current_date.strftime('%A')
            )

            if weekday_name in training_days:
                expected_days.append(
                    (
                        current_date,
                        weekday_name,
                    )
                )

            current_date += timedelta(days=1)

        return expected_days

    @staticmethod
    def calculate_longest_streak(
            user,
            expected_training_days,
    ):

        current_run = 0
        longest_run = 0

        for training_date, _ in (
                expected_training_days
        ):

            status = (
                WorkoutStreakService
                .get_day_status(
                    user,
                    training_date,
                )
            )

            if (
                    status ==
                    WorkoutDayStatus.SUCCESS
            ):

                current_run += 1

                longest_run = max(
                    longest_run,
                    current_run,
                )

            elif (
                    status ==
                    WorkoutDayStatus.FAILED
            ):

                current_run = 0

            elif status in (
                    WorkoutDayStatus.PENDING,
                    WorkoutDayStatus.ACTIVE,
                    WorkoutDayStatus.REST,
            ):

                continue

        return longest_run

    @staticmethod
    def calculate_current_streak(
            user,
            expected_training_days,
    ):

        current_streak = 0

        for training_date, _ in reversed(
                expected_training_days
        ):

            status = (
                WorkoutStreakService
                .get_day_status(
                    user,
                    training_date,
                )
            )

            if (
                    status ==
                    WorkoutDayStatus.SUCCESS
            ):

                current_streak += 1

            elif status in (
                    WorkoutDayStatus.PENDING,
                    WorkoutDayStatus.ACTIVE,
                    WorkoutDayStatus.REST,
            ):

                continue

            elif (
                    status ==
                    WorkoutDayStatus.FAILED
            ):

                break

        return current_streak


