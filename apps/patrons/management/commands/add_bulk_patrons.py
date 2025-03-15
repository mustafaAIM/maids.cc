import json
import random
import string
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.patrons.models import Patron

class Command(BaseCommand):
    help = 'Add 100,000 patrons to the database'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100000, help='Number of patrons to create')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for bulk creation')

    def handle(self, *args, **options):
        count = options['count']
        batch_size = options['batch_size']
        
        self.stdout.write(self.style.SUCCESS(f'Starting creation of {count} patrons'))
        
        first_names = ['John', 'Jane', 'Michael', 'Sara', 'David', 'Emma', 'James', 
                      'Emily', 'Robert', 'Maria', 'William', 'Sophia', 'Joseph', 
                      'Olivia', 'Thomas', 'Ava', 'Charles', 'Isabella', 'Daniel', 
                      'Mia', 'Matthew', 'Abigail', 'Anthony', 'Elizabeth', 'Mustafa']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 
                     'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 
                     'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 
                     'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 
                     'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'Alhaiba']
        
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
                  'example.com', 'mail.com', 'protonmail.com', 'icloud.com']
        
        start_time = time.time()
        patrons_created = 0
        failed_patrons = []
        
        for i in range(0, count, batch_size):
            batch_end = min(i + batch_size, count)
            batch_count = batch_end - i
            
            self.stdout.write(f'Creating patrons {i+1} to {batch_end}...')
            
            patrons_to_create = []
            for j in range(batch_count):
                index = i + j
                
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                member_id = f"P{100000 + index}"
                email_username = f"{first_name.lower()}.{last_name.lower()}.{index}"
                email = f"{email_username}@{random.choice(domains)}"
                
                try:
                    patron = Patron(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        member_id=member_id,
                        phone_number=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} Street"
                    )
                    patrons_to_create.append(patron)
                except Exception as e:
                    failed_patrons.append({
                        "index": index,
                        "data": {
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "member_id": member_id
                        },
                        "error": str(e)
                    })
            
            # Bulk create the batch using a transaction
            try:
                with transaction.atomic():
                    Patron.objects.bulk_create(patrons_to_create)
                patrons_created += len(patrons_to_create)
                
                # Show progress
                elapsed_time = time.time() - start_time
                avg_time_per_patron = elapsed_time / patrons_created if patrons_created > 0 else 0
                estimated_time_left = avg_time_per_patron * (count - patrons_created)
                
                self.stdout.write(self.style.SUCCESS(
                    f'Created {patrons_created}/{count} patrons, '
                    f'{elapsed_time:.2f}s elapsed, '
                    f'~{estimated_time_left:.2f}s remaining'
                ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating batch: {str(e)}'))
                # Save individual patrons to avoid losing the entire batch
                for patron in patrons_to_create:
                    try:
                        patron.save()
                        patrons_created += 1
                    except Exception as individual_error:
                        failed_patrons.append({
                            "data": {
                                "first_name": patron.first_name,
                                "last_name": patron.last_name,
                                "email": patron.email,
                                "member_id": patron.member_id
                            },
                            "error": str(individual_error)
                        })
        
        # Report results
        total_time = time.time() - start_time
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {patrons_created} patrons in {total_time:.2f} seconds.'
        ))
        
        if failed_patrons:
            with open('failed_patrons.json', 'w') as f:
                json.dump(failed_patrons, f, indent=2)
            self.stdout.write(self.style.WARNING(
                f'Failed to create {len(failed_patrons)} patrons. See failed_patrons.json for details.'
            ))
