from django.core.management.base import BaseCommand
from training.models import MuscleGroup, Muscle, Exercise
from django.db import transaction


class Command(BaseCommand):
    help = 'Populates the database with initial muscle groups, muscles, and exercises.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        data = {
            "Chest": {
                "Pectoralis Major (Upper)": [
                    {"name": "Incline Dumbbell Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=sU14i6-B570"},
                    {"name": "Incline Barbell Press", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=jWJ8B2c-l1U"},
                    {"name": "Low-to-High Cable Flyes", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=M57b1I03K7Q"},
                ],
                "Pectoralis Major (Middle)": [
                    {"name": "Barbell Bench Press", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=fJmcb_hJ8J4"},
                    {"name": "Dumbbell Bench Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=XLJc0v6V1i0"},
                    {"name": "Pec Deck Flyes", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=kQeI7iK-Mh4"},
                ],
                "Pectoralis Major (Lower)": [
                    {"name": "Decline Dumbbell Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=0kF_MugFz40"},
                    {"name": "Decline Barbell Press", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=Cm-A7XF-R34"},
                    {"name": "High-to-Low Cable Flyes", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=e_F4w9D0r4A"},
                ],
                "Pectoralis Minor": [
                    {"name": "Dips (Chest Version)", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=HRqTqMsqpSg"},
                    {"name": "Push-ups (Scapular Protraction Focus)", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=j2-A5o_6d08"},
                    {"name": "Scapular Push-ups", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=c5Y413Fq8E0"},
                ],
            },
            "Back": {
                "Latissimus Dorsi": [
                    {"name": "Pull-ups", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=eGo4dqkC5_Y"},
                    {"name": "Lat Pulldowns", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=rqnQG_s70pI"},
                    {"name": "Barbell Rows", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=gT8oK1fK72I"},
                ],
                "Trapezius (Upper)": [
                    {"name": "Dumbbell Shrugs", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=l4q0Lh2221Q"},
                    {"name": "Barbell Shrugs", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=077Qk5_13h8"},
                    {"name": "Upright Rows", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=FjIu0Z31k74"},
                ],
                "Trapezius (Middle)": [
                    {"name": "Face Pulls", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=rep-qVOkqgk"},
                    {"name": "Seated Cable Rows", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=rC7N1o-v39A"},
                    {"name": "Reverse Pec Deck Flyes (Traps focus)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=b4wSgL_m35o"},
                ],
                "Trapezius (Lower)": [
                    {"name": "Y-Raises", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=P_J_P2V7c0w"}, # Placeholder, need a proper Y-raise video
                    {"name": "Superman", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=z6m6jWf3R34"},
                    {"name": "Scapular Pull-downs", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=gH5Jz5-tE3c"}, # Placeholder
                ],
                "Rhomboids": [
                    {"name": "Bent-Over Dumbbell Rows", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=pYjec9B0Crs"},
                    {"name": "Single-Arm Dumbbell Rows", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=roS8uL1Nwsg"},
                    {"name": "Cable Face Pulls", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=rep-qVOkqgk"},
                ],
                "Erector Spinae": [
                    {"name": "Deadlifts", "sets": 3, "repetitions": 6, "video_link": "https://www.youtube.com/watch?v=ytQo2K5zQ78"},
                    {"name": "Hyperextensions (Back Extensions)", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=ph3pddpKzzw"},
                    {"name": "Good Mornings", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=M99b2X_F1E8"},
                ],
            },
            "Shoulders": {
                "Anterior Deltoid": [
                    {"name": "Overhead Press (Barbell)", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=E_IuP6I-Bqs"},
                    {"name": "Dumbbell Front Raises", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=Y_D_d8c4K_w"},
                    {"name": "Arnold Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=F3QYJ4M6XqU"},
                ],
                "Lateral Deltoid": [
                    {"name": "Dumbbell Lateral Raises", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=3pyy6_e4K2Y"},
                    {"name": "Cable Lateral Raises", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=2zYQ7hI91t8"},
                    {"name": "Machine Lateral Raises", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=P_J_P2V7c0w"},
                ],
                "Posterior Deltoid": [
                    {"name": "Reverse Pec Deck Flyes", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=b4wSgL_m35o"},
                    {"name": "Bent-Over Dumbbell Reverse Flyes", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=rep-qVOkqgk"},
                    {"name": "Face Pulls", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=rep-qVOkqgk"},
                ],
            },
            "Arms": {
                "Biceps Brachii": [
                    {"name": "Barbell Curls", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=kwG2ipFRgfo"},
                    {"name": "Dumbbell Curls (Alternating)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=ykJmrZ5s0dg"},
                    {"name": "Hammer Curls", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=zC3ocq_oO8E"},
                ],
                "Brachialis": [
                    {"name": "Reverse Curls (Barbell)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=y-qB_g0yYk8"},
                    {"name": "Hammer Curls (Strict)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=zC3ocq_oO8E"},
                    {"name": "Concentration Curls", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=0AUGkch3txc"},
                ],
                "Triceps Brachii (Long Head)": [
                    {"name": "Overhead Dumbbell Extension", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=d_Kz_jI5X04"},
                    {"name": "Close-Grip Bench Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=cXg44_4L3Y8"},
                    {"name": "Lying Triceps Extension (Skullcrushers)", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=d_Kz_jI5X04"},
                ],
                "Triceps Brachii (Lateral Head)": [
                    {"name": "Triceps Pushdowns (Rope)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=2-dhv-6A42E"},
                    {"name": "Dips (Triceps Version)", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=HRqTqMsqpSg"},
                    {"name": "Close-Grip Push-ups", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=JfD5XoB1lK0"},
                ],
                "Triceps Brachii (Medial Head)": [
                    {"name": "Reverse Grip Pushdowns", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=0h2Q0_I3Nl4"},
                    {"name": "Dumbbell Triceps Kickbacks", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=GjY-lC3p-kQ"},
                    {"name": "Single Arm Overhead Extension (Cable)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=2-dhv-6A42E"}, # Placeholder
                ],
                "Forearm Flexors": [
                    {"name": "Wrist Curls (Barbell)", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=l42c9N3pQe4"},
                    {"name": "Reverse Wrist Curls (Barbell)", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=2SgP_K8iN_A"},
                    {"name": "Farmer's Walk", "sets": 3, "repetitions": 30, "video_link": "https://www.youtube.com/watch?v=vV3rA3u5Y68"},
                ],
                "Forearm Extensors": [
                    {"name": "Reverse Wrist Curls", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=2SgP_K8iN_A"},
                    {"name": "Plate Pinches", "sets": 3, "repetitions": 30, "video_link": "https://www.youtube.com/watch?v=b4wSgL_m35o"}, # Placeholder
                    {"name": "Zottman Curls", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=r0wV9pY6Gts"},
                ],
            },
            "Legs": {
                "Quadriceps": [
                    {"name": "Barbell Squats", "sets": 3, "repetitions": 8, "video_link": "https://www.youtube.com/watch?v=ultWZbFYM1M"},
                    {"name": "Leg Press", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=IZxyjW7MPJQ"},
                    {"name": "Leg Extensions", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=YyvKeQcWc-g"},
                ],
                "Hamstrings": [
                    {"name": "Romanian Deadlifts (RDL)", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=jcT1x3Q3R3k"},
                    {"name": "Leg Curls (Lying)", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=NGbJ7zB1q6E"},
                    {"name": "Glute-Ham Raise", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=zJgBvj40t7U"},
                ],
                "Gluteus Maximus": [
                    {"name": "Barbell Hip Thrusts", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=SE8X4N495eU"},
                    {"name": "Glute Bridges", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=Yp69jZf4H6g"},
                    {"name": "Cable Pull-Throughs", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=fA4U3X24zS8"},
                ],
                "Gluteus Medius/Minimus": [
                    {"name": "Banded Lateral Walks", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=2K2_Z0Z0Y5U"},
                    {"name": "Clamshells", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=z2Cg1d1vU0A"},
                    {"name": "Single-Leg Romanian Deadlifts", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=b1L9z9q41_g"},
                ],
                "Gastrocnemius": [
                    {"name": "Standing Calf Raises", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=rMhnn746K1I"},
                    {"name": "Calf Press (Leg Press Machine)", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=ymR7XFp_7mQ"},
                    {"name": "Jump Rope", "sets": 3, "repetitions": 60, "video_link": "https://www.youtube.com/watch?v=X0YjJt1v40g"}, # Placeholder
                ],
                "Soleus": [
                    {"name": "Seated Calf Raises", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=GAQvQ-y0q_4"},
                    {"name": "Donkey Calf Raises", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=H6Uo3x6yIrg"},
                    {"name": "Calf Raises with Bent Knee", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=X0YjJt1v40g"}, # Placeholder
                ],
            },
            "Core": {
                "Rectus Abdominis": [
                    {"name": "Crunches", "sets": 3, "repetitions": 20, "video_link": "https://www.youtube.com/watch?v=Xyd_rsZ4aQc"},
                    {"name": "Leg Raises", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=jb2BP9Xqj6k"},
                    {"name": "Ab Rollouts", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=Jm00J3aWpY8"},
                ],
                "Obliques (Internal & External)": [
                    {"name": "Russian Twists", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=DJQGX2yMato"},
                    {"name": "Side Planks", "sets": 3, "repetitions": 30, "video_link": "https://www.youtube.com/watch?v=0QNHq28eM4M"},
                    {"name": "Cable Wood Chops", "sets": 3, "repetitions": 12, "video_link": "https://www.youtube.com/watch?v=lEwD6L6kC64"},
                ],
                "Transverse Abdominis": [
                    {"name": "Plank", "sets": 3, "repetitions": 60, "video_link": "https://www.youtube.com/watch?v=pL2gOPj_CIM"},
                    {"name": "Abdominal Vacuum Pose", "sets": 3, "repetitions": 10, "video_link": "https://www.youtube.com/watch?v=o6f2X4D_b7c"},
                    {"name": "Bird Dog", "sets": 3, "repetitions": 15, "video_link": "https://www.youtube.com/watch?v=N4t_W0N4sB0"},
                ],
            }
        }

        with transaction.atomic():
            for mg_name, muscles_data in data.items():
                muscle_group, created = MuscleGroup.objects.get_or_create(name=mg_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created MuscleGroup: {muscle_group.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'MuscleGroup already exists: {muscle_group.name}'))

                for m_name, exercises_data in muscles_data.items():
                    muscle, created = Muscle.objects.get_or_create(name=m_name, group=muscle_group)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created Muscle: {muscle.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Muscle already exists: {muscle.name}'))

                    for exercise_data in exercises_data:
                        exercise, created = Exercise.objects.get_or_create(
                            name=exercise_data['name'],
                            defaults={
                                'sets': exercise_data['sets'],
                                'repetitions': exercise_data['repetitions'],
                                'video_link': exercise_data['video_link'],
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Exercise: {exercise.name}'))
                        else:
                            # Update if exists, in case sets/reps/link changed
                            for key, value in exercise_data.items():
                                setattr(exercise, key, value)
                            exercise.save()
                            self.stdout.write(self.style.WARNING(f'Exercise already exists, updated: {exercise.name}'))
                        
                        # Add muscle to exercise M2M relationship
                        if muscle not in exercise.muscles.all():
                            exercise.muscles.add(muscle)
                            self.stdout.write(self.style.SUCCESS(f'Added {muscle.name} to {exercise.name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'{muscle.name} already linked to {exercise.name}'))


        self.stdout.write(self.style.SUCCESS('Data population complete!'))
