from decimal import Decimal

from progress.models import ProgresTracking


class ProgressAnalyticsService:

    @staticmethod
    def get_progress_summary(user):
        profile = user.profile

        records = (
            ProgresTracking.objects
            .filter(owner=user)
            .order_by('date')
        )

        records_count = records.count()

        latest_record = records.last()

        if (
            not profile.starting_weight
            or not profile.target_weight
            or not latest_record
        ):
            return None

        starting_weight = profile.starting_weight
        current_weight = latest_record.weight
        target_weight = profile.target_weight

        weight_change = (
            current_weight - starting_weight
        )

        remaining_to_goal = abs(
            current_weight - target_weight
        )

        total_goal_change = abs(
            starting_weight - target_weight
        )

        completed_change = abs(
            starting_weight - current_weight
        )

        progress_percentage = Decimal('0')

        if total_goal_change > 0:
            progress_percentage = (
                completed_change / total_goal_change
            ) * 100

        progress_percentage = min(
            progress_percentage,
            Decimal('100')
        )

        if abs(progress_percentage) < Decimal('0.01'):
            progress_percentage = Decimal('0')

        weekly_rate = None
        estimated_weeks = None

        if records_count >= 3:
            first_record = records.first()

            days_difference = (
                latest_record.date - first_record.date
            ).days

            if days_difference < 1:
                days_difference = 1

            weight_difference = (
                latest_record.weight - first_record.weight
            )

            weekly_rate = round((weight_difference / Decimal(days_difference)) * Decimal('7'), 2)

            if weekly_rate != 0:
                estimated_weeks = (
                    remaining_to_goal /
                    abs(weekly_rate)
                )

        return {
            'starting_weight': starting_weight,
            'current_weight': current_weight,
            'target_weight': target_weight,
            'weight_change': round(weight_change, 2),
            'progress_percentage': round(progress_percentage, 2),
            'remaining_to_goal': round(remaining_to_goal, 2),
            'weekly_rate': weekly_rate,
            'estimated_weeks': (round(estimated_weeks, 1) if estimated_weeks is not None else None),
            'prediction_available': records_count >= 3
        }
