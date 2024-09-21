import csv
from django.core.management.base import BaseCommand
from problems.models import Problem

class Command(BaseCommand):
    """
    A Django management command to import problems from a CSV file into the Problem model.

    This command reads a CSV file where each row represents a problem with the following fields:
    - 'course': The course the problem belongs to.
    - 'semester': The semester in which the problem is assigned.
    - 'week': The week number of the problem.
    - 'problem': A unique problem identifier.
    - 'description': A description of the problem.

    The command updates existing records if a matching problem (based on course, semester, week, and problem number)
    already exists, or creates new ones if they do not.

    Attributes:
        help (str): A brief description of the command to assist users.

    Methods:
        add_arguments: Adds the 'csv_file' argument to specify the path to the CSV file.
        handle: The main logic to process the CSV file and import/update problems in the database.

    Example Usage:
        To run this command:
        ```
        python manage.py import_problems <csv_file>
        ```

        Where `<csv_file>` is the path to the CSV file containing the problem data.
    """
    help = 'Import problems from CSV file'

    def add_arguments(self, parser):
        """
        Adds a command-line argument 'csv_file' to specify the CSV file path.

        Args:
            parser: The argument parser used to define command-line options and arguments.
        """
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        """
        Handles the core logic for reading the CSV file and importing problems into the database.

        Args:
            *args: Additional arguments.
            **kwargs: Dictionary of keyword arguments passed to the command (contains 'csv_file').

        Workflow:
        - Check if a valid CSV file is provided.
        - Open the file and read it using `csv.DictReader`.
        - For each row in the CSV file:
            - Convert 'semester' and 'week' to integers, handling invalid data by skipping the row.
            - Use `update_or_create` to either update an existing problem or create a new one.
        - Output the success message with the total count of problems imported.

        Exceptions:
            - FileNotFoundError: If the provided CSV file does not exist.
            - Any other exceptions will be caught and reported.

        Raises:
            ValueError: If 'semester' or 'week' contains invalid integer values.
        """
        csv_file = kwargs.get('csv_file')
        if not csv_file:
            self.stderr.write(self.style.ERROR('No CSV file provided'))
            return

        try:
            with open(csv_file, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    try:
                        semester = int(row['semester'])
                        week = int(row['week'])
                    except ValueError as e:
                        self.stderr.write(self.style.ERROR(f'Invalid semester or week: {e}'))
                        continue

                    Problem.objects.update_or_create(
                        course=row['course'],
                        semester=semester,
                        week=week,
                        problemNumber=row['problem'],
                        defaults={'description': row['description']}
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(Problem.objects.all())} problems'))
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(e))
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))
