import logging

logger = logging.getLogger(__name__)


class AuditLogger:

    @staticmethod
    def _log(message, **extra):
        logger.info(
            message,
            extra=extra,
        )

    # ==========================
    # Meal
    # ==========================

    @staticmethod
    def meal_created(user, meal):
        AuditLogger._log(
            "Meal created.",
            user_id=user.pk,
            meal_id=meal.pk,
            meal_name=meal.name,
            day_id=meal.day.pk,
        )

    @staticmethod
    def meal_updated(user, meal):
        AuditLogger._log(
            "Meal updated.",
            user_id=user.pk,
            meal_id=meal.pk,
            meal_name=meal.name,
            day_id=meal.day.pk,
        )

    @staticmethod
    def meal_deleted(user, meal_id, meal_name, day_id):
        AuditLogger._log(
            "Meal deleted.",
            user_id=user.pk,
            meal_id=meal_id,
            meal_name=meal_name,
            day_id=day_id,
        )

    @staticmethod
    def meal_completed(user, meal):
        AuditLogger._log(
            "Meal completed.",
            user_id=user.pk,
            meal_id=meal.pk,
            meal_name=meal.name,
            day_id=meal.day.pk,
        )

    @staticmethod
    def meal_missed(user, meal):
        AuditLogger._log(
            "Meal missed.",
            user_id=user.pk,
            meal_id=meal.pk,
            meal_name=meal.name,
            day_id=meal.day.pk,
        )

    @staticmethod
    def meal_reset_to_planned(user, meal):
        AuditLogger._log(
            "Meal reset to planned.",
            user_id=user.pk,
            meal_id=meal.pk,
            meal_name=meal.name,
            day_id=meal.day.pk,
        )

    # ==========================
    # Nutrition Day
    # ==========================

    @staticmethod
    def day_created(user, day):
        AuditLogger._log(
            "Nutrition day created.",
            user_id=user.pk,
            day_id=day.pk,
            day_name=day.name,
        )

    @staticmethod
    def day_updated(user, day):
        AuditLogger._log(
            "Nutrition day updated.",
            user_id=user.pk,
            day_id=day.pk,
            day_name=day.name,
        )

    @staticmethod
    def day_deleted(user, day_id, day_name):
        AuditLogger._log(
            "Nutrition day deleted.",
            user_id=user.pk,
            day_id=day_id,
            day_name=day_name,
        )

    # ==========================
    # Food Database
    # ==========================

    @staticmethod
    def food_created(user, food):
        AuditLogger._log(
            "Food database item created.",
            user_id=user.pk,
            food_id=food.pk,
            food_name=food.name,
        )

    @staticmethod
    def food_updated(user, food):
        AuditLogger._log(
            "Food database item updated.",
            user_id=user.pk,
            food_id=food.pk,
            food_name=food.name,
        )

    @staticmethod
    def food_deleted(user, food_id, food_name):
        AuditLogger._log(
            "Food database item deleted.",
            user_id=user.pk,
            food_id=food_id,
            food_name=food_name,
        )

    # ==========================
    # Nutrition Target
    # ==========================

    @staticmethod
    def nutrition_target_updated(user, target):
        AuditLogger._log(
            "Nutrition target updated.",
            user_id=user.pk,
            target_id=target.pk,
            calories=target.calories,
            protein=target.protein,
            carbohydrates=target.carbohydrates,
            fat=target.fat,
        )

    # ==========================
    # Training Day
    # ==========================

    @staticmethod
    def training_day_created(user, training_day):
        AuditLogger._log(
            "Training day created.",
            user_id=user.pk,
            training_day_id=training_day.pk,
            day_name=training_day.day,
            description=training_day.description,
        )

    @staticmethod
    def training_day_updated(user, training_day):
        AuditLogger._log(
            "Training day updated.",
            user_id=user.pk,
            training_day_id=training_day.pk,
            day_name=training_day.day,
            description=training_day.description,
        )

    @staticmethod
    def training_day_deleted(user, training_day_id, day_name, description):
        AuditLogger._log(
            "Training day deleted.",
            user_id=user.pk,
            training_day_id=training_day_id,
            day_name=day_name,
            description=description,
        )

    # ==========================
    # Exercise
    # ==========================

    @staticmethod
    def exercise_created(user, exercise):
        AuditLogger._log(
            "Exercise created.",
            user_id=user.pk,
            exercise_id=exercise.pk,
            exercise_name=exercise.name,
            sets=exercise.sets,
            repetitions=exercise.repetitions,
        )

    @staticmethod
    def exercise_updated(user, exercise):
        AuditLogger._log(
            "Exercise updated.",
            user_id=user.pk,
            exercise_id=exercise.pk,
            exercise_name=exercise.name,
            sets=exercise.sets,
            repetitions=exercise.repetitions,
        )

    @staticmethod
    def exercise_deleted(user, exercise_id, exercise_name, exercise_sets, exercise_repetitions):
        AuditLogger._log(
            "Exercise deleted.",
            user_id=user.pk,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            sets=exercise_sets,
            repetitions=exercise_repetitions,
        )

    # ==========================
    # Training Day Exercise
    # ==========================

    @staticmethod
    def training_day_exercise_updated(user, training_day_exercise):
        AuditLogger._log(
            "Training day exercise configuration updated.",
            user_id=user.pk,
            training_day_exercise_id=training_day_exercise.pk,
            training_day_id=training_day_exercise.training_day.pk,
            exercise_id=training_day_exercise.exercise.pk,
            exercise_name=training_day_exercise.exercise.name,
            custom_sets=training_day_exercise.custom_sets,
            custom_repetitions=training_day_exercise.custom_repetitions,
        )

    @staticmethod
    def training_day_exercise_moved_up(user, training_day_exercise):
        AuditLogger._log(
            "Training day exercise moved up.",
            user_id=user.pk,
            training_day_exercise_id=training_day_exercise.pk,
            training_day_id=training_day_exercise.training_day.pk,
            exercise_id=training_day_exercise.exercise.pk,
            exercise_name=training_day_exercise.exercise.name,
        )

    @staticmethod
    def training_day_exercise_moved_down(user, training_day_exercise):
        AuditLogger._log(
            "Training day exercise moved down.",
            user_id=user.pk,
            training_day_exercise_id=training_day_exercise.pk,
            training_day_id=training_day_exercise.training_day.pk,
            exercise_id=training_day_exercise.exercise.pk,
            exercise_name=training_day_exercise.exercise.name,
        )

    # ==========================
    # Workout Session
    # ==========================

    @staticmethod
    def workout_started(user, workout_session):
        AuditLogger._log(
            "Workout session started.",
            user_id=user.pk,
            workout_session_id=workout_session.pk,
            training_day_id=workout_session.training_day.pk,
            day_name=workout_session.training_day.day,
            started_at=workout_session.started_at,
            status=workout_session.status,
        )

    @staticmethod
    def workout_finished(user, workout_session):
        AuditLogger._log(
            "Workout session finished.",
            user_id=user.pk,
            workout_session_id=workout_session.pk,
            training_day_id=workout_session.training_day.pk,
            day_name=workout_session.training_day.day,
            started_at=workout_session.started_at,
            finished_at=workout_session.finished_at,
            status=workout_session.status,
        )

    @staticmethod
    def workout_cancelled(user, workout_session):
        AuditLogger._log(
            "Workout session cancelled.",
            user_id=user.pk,
            workout_session_id=workout_session.pk,
            training_day_id=workout_session.training_day.pk,
            day_name=workout_session.training_day.day,
            started_at=workout_session.started_at,
            status=workout_session.status,

        )

    # ==========================
    # Workout Set
    # ==========================

    @staticmethod
    def workout_set_completed(user, workout_set):
        AuditLogger._log(
            "Workout set completed.",
            user_id=user.pk,
            workout_set_id=workout_set.pk,
            workout_session_id=workout_set.exercise_session.workout_session.pk,
            exercise_id=workout_set.exercise_session.training_day_exercise.exercise.pk,
            exercise_name=workout_set.exercise_session.training_day_exercise.exercise.name,
            set_number=workout_set.set_number,
            weight=workout_set.weight,
            repetitions=workout_set.repetitions,
        )

    @staticmethod
    def workout_set_updated(user, workout_set):
        AuditLogger._log(
            "Workout set updated.",
            user_id=user.pk,
            workout_set_id=workout_set.pk,
            workout_session_id=workout_set.exercise_session.workout_session.pk,
            exercise_id=workout_set.exercise_session.training_day_exercise.exercise.pk,
            exercise_name=workout_set.exercise_session.training_day_exercise.exercise.name,
            set_number=workout_set.set_number,
            weight=workout_set.weight,
            repetitions=workout_set.repetitions,
        )


# ==========================
# Progress
# ==========================

    @staticmethod
    def progress_record_created(user, record):
        AuditLogger._log(
            "Progress record created.",
            user_id=user.pk,
            record_id=record.pk,
            day=record.day,
            date=record.date,
            weight=record.weight,
            chest=record.chest,
            shoulders=record.shoulders,
            waist=record.waist,
            biceps=record.biceps,
            neck=record.neck,
            butt=record.butt,
            tight=record.tight,
            calf=record.calf,
        )

    @staticmethod
    def progress_record_updated(user, record):
        AuditLogger._log(
            "Progress record updated.",
            user_id=user.pk,
            record_id=record.pk,
            day=record.day,
            date=record.date,
            weight=record.weight,
            chest=record.chest,
            shoulders=record.shoulders,
            waist=record.waist,
            biceps=record.biceps,
            neck=record.neck,
            butt=record.butt,
            tight=record.tight,
            calf=record.calf,
        )

    @staticmethod
    def progress_record_deleted(
        user,
        record_id,
        day,
        date,
        weight,
    ):
        AuditLogger._log(
            "Progress record deleted.",
            user_id=user.pk,
            record_id=record_id,
            day=day,
            date=date,
            weight=weight,
        )

# ====================
# Cache Service
# ====================

    @staticmethod
    def cache_timeout(cache_key):
        logger.error(
            "Cache timeout while waiting for '%s'.",
            cache_key,
        )
