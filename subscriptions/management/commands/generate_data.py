from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscriptions.models import Feature, SubscriptionPlan, UserSubscription
from faker import Faker
import random
from datetime import timedelta


fake = Faker()


class Command(BaseCommand):
    help = 'Generate randomized subscription data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10000,
            help='Number of users to generate (default: 10000)'
        )
        parser.add_argument(
            '--subscriptions',
            type=int,
            default=500000,
            help='Number of subscriptions to generate (default: 500000)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100000,
            help='Batch size for bulk operations (default: 100000)'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_subscriptions = options['subscriptions']
        batch_size = options['batch_size']

        self.stdout.write(self.style.SUCCESS('Starting data generation...'))

        # Step 1: Create Features
        self.stdout.write('Creating features...')
        features_data = [
            {'name': 'SMS Notifications', 'description': 'Receive SMS notifications for important updates'},
            {'name': 'Priority Support', 'description': '24/7 priority customer support'},
            {'name': 'Advanced Analytics', 'description': 'Access to advanced analytics dashboard'},
            {'name': 'API Access', 'description': 'Full API access for integrations'},
            {'name': 'Custom Branding', 'description': 'Add your own branding and logo'},
            {'name': 'Multi-User Access', 'description': 'Allow multiple users on one account'},
            {'name': 'Data Export', 'description': 'Export your data in various formats'},
            {'name': 'Unlimited Storage', 'description': 'Unlimited cloud storage'},
            {'name': 'Advanced Security', 'description': 'Enhanced security features'},
            {'name': 'White Label', 'description': 'Complete white label solution'},
        ]

        features = []
        for data in features_data:
            feature, created = Feature.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            features.append(feature)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(features)} features created'))

        # Step 2: Create Subscription Plans
        self.stdout.write('Creating subscription plans...')
        plans_data = [
            {'name': 'Basic Monthly', 'price': 9.99, 'billing_cycle': 'monthly', 'features': features[:2]},
            {'name': 'Pro Monthly', 'price': 29.99, 'billing_cycle': 'monthly', 'features': features[:5]},
            {'name': 'Enterprise Monthly', 'price': 99.99, 'billing_cycle': 'monthly', 'features': features},
            {'name': 'Basic Yearly', 'price': 99.99, 'billing_cycle': 'yearly', 'features': features[:2]},
            {'name': 'Pro Yearly', 'price': 299.99, 'billing_cycle': 'yearly', 'features': features[:5]},
            {'name': 'Enterprise Yearly', 'price': 999.99, 'billing_cycle': 'yearly', 'features': features},
        ]

        plans = []
        for data in plans_data:
            plan_features = data.pop('features')
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                plan.features.set(plan_features)
            plans.append(plan)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(plans)} subscription plans created'))

        # Step 3: Generate Users
        self.stdout.write(f'Generating {num_users} users in batches of {batch_size}...')

        existing_users = User.objects.count()
        if existing_users >= num_users:
            self.stdout.write(self.style.WARNING(f'Already have {existing_users} users, skipping user generation'))
            users = list(User.objects.all()[:num_users])
        else:
            users_to_create = []
            for i in range(num_users):
                users_to_create.append(User(
                    username=f'user{i}_{fake.user_name()}',
                    email=f'user{i}@example.com',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_active=True
                ))

                if len(users_to_create) >= batch_size:
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    self.stdout.write(f'  Created {len(users_to_create)} users...')
                    users_to_create = []

            if users_to_create:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                self.stdout.write(f'  Created {len(users_to_create)} users...')

            users = list(User.objects.all())
            self.stdout.write(self.style.SUCCESS(f'✓ {len(users)} users generated'))

        # Step 4: Generate User Subscriptions
        self.stdout.write(f'Generating {num_subscriptions} subscriptions in batches of {batch_size}...')

        subscriptions_to_create = []

        statuses = ['active', 'cancelled', 'suspended']
        status_weights = [0.7, 0.2, 0.1]  # 70% active, 20% cancelled, 10% suspended

        for i in range(num_subscriptions):
            user = random.choice(users)
            plan = random.choice(plans)

            start_date = fake.date_between(start_date='-2y', end_date='today')
            end_date = start_date + timedelta(days=random.randint(30, 730))

            # Select status based on weights
            status = random.choices(statuses, weights=status_weights)[0]

            subscriptions_to_create.append(UserSubscription(
                user=user,
                plan=plan,
                plan_cost=plan.price + random.uniform(-5, 20),
                start_date=start_date,
                end_date=end_date,
                status=status
            ))

            if len(subscriptions_to_create) >= batch_size:
                UserSubscription.objects.bulk_create(subscriptions_to_create)
                self.stdout.write(f'  Created {i + 1}/{num_subscriptions} subscriptions...')
                subscriptions_to_create = []

        if subscriptions_to_create:
            UserSubscription.objects.bulk_create(subscriptions_to_create)

        self.stdout.write(self.style.SUCCESS(f'✓ {num_subscriptions} subscriptions generated'))

        self.stdout.write(self.style.SUCCESS('\nData generation completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total plans: {SubscriptionPlan.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total subscriptions: {UserSubscription.objects.count()}'))
