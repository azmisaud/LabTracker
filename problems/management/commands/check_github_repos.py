import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from problems.models import ProblemCompletion, Problem, WeekCommit
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    """
    Custom management command to check students' GitHub repositories for problem completion statuses,
    update their completion information, and track the last commit for each week.
    """

    help = 'Check GitHub repositories for problem completion status'

    def handle(self, *args, **kwargs):
        """
        Main method that processes all student records in batches, fetches repository content,
        and updates the problem completion and commit statuses.

        It processes students in batches to prevent exceeding API rate limits, sleeping for
        an hour between each batch if necessary.
        """
        User = get_user_model()
        token = settings.GITHUB_TOKEN
        headers = {"Authorization": f"token {token}"}

        students = list(User.objects.filter(is_superuser=False, is_staff=False))
        batch_size = 150  # Defines how many students are processed in a batch.

        # Process students in batches to avoid hitting API limits.
        for i in range(0, len(students), batch_size):
            batch = students[i:i+batch_size]

            for student in batch:
                self.process_students(student, headers)

            self.stdout.write(self.style.SUCCESS(f"Processed batch {i}, students : {len(batch)}"))

            # Sleep for an hour between batches to respect API rate limits.
            if i + batch_size < len(students):
                self.stdout.write(self.style.WARNING("Sleeping for 1 hour..."))
                time.sleep(3600)

    def process_students(self, student, headers):
        """
        Processes individual student records by fetching their repository contents from GitHub,
        filtering the problems for their course and semester, and updating their problem completion status.

        :param student: Student object containing the student's details (e.g., username, course, etc.)
        :param headers: GitHub API headers including the authorization token.
        """
        repo_name = student.repo_name
        url = f"https://api.github.com/repos/{student.username}/{repo_name}/contents/"
        problems = Problem.objects.filter(course=student.course, semester=student.semester)

        try:
            # Fetch repository contents from GitHub API.
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return

            response.raise_for_status()
            repo_contents = response.json()

            # Filter out directories for weeks in the repository.
            week_dirs = {content['name']: content['url'] for content in repo_contents if
                         content['type'] == 'dir' and content['name'].startswith('Week')}

            # Cache to avoid redundant API calls for week contents and commit statuses.
            week_content_cache = {}
            commit_cache = {}

            # Group problems by their week.
            problems_by_week = {}
            for problem in problems:
                week_number = problem.week
                if week_number not in problems_by_week:
                    problems_by_week[week_number] = []
                problems_by_week[week_number].append(problem)

            # Process each week's problems and update their statuses.
            for week_number, week_problems in problems_by_week.items():
                week_dir_name = f"Week{week_number}"
                if week_dir_name not in week_dirs:
                    continue

                # Fetch week directory contents from GitHub if not already cached.
                if week_dir_name not in week_content_cache:
                    week_url = week_dirs[week_dir_name]
                    week_response = requests.get(week_url, headers=headers)
                    week_response.raise_for_status()
                    week_content_cache[week_dir_name] = week_response.json()

                week_contents = week_content_cache[week_dir_name]

                for problem in week_problems:
                    self.check_problem_status(student, problem, week_contents)

                # Update or create the commit record for the week.
                if week_dir_name not in commit_cache:
                    commit_cache[week_dir_name] = self.update_or_create_week_commit(
                        student, week_number, repo_name, week_dir_name, headers)

        except requests.exceptions.RequestException as e:
            self.stdout.write(f"Error checking repository for {student.username}: {e}")

    def check_problem_status(self, student, problem, week_contents):
        """
        Checks if a student's solution or output image for a problem is present in their GitHub repository.
        Updates the problem completion status accordingly.

        :param student: Student object containing the student's details.
        :param problem: Problem object representing the specific problem to check.
        :param week_contents: The contents of the GitHub repository's week directory.
        """
        file_extensions = ['.cpp', '.java', '.py', '.c', '.js', '.rb', '.go', '.swift']
        image_extensions = ['.jpg', '.jpeg', '.png']
        formatted_problem_number = problem.problemNumber.replace(" ", "")

        completion = ProblemCompletion.objects.filter(student=student, problem=problem).first()

        problem_completed = False
        solution_url = None
        output_image_url = None

        # Check if the solution file exists in the repository.
        for extension in file_extensions:
            problem_file_name = f"{formatted_problem_number}{extension}"
            matching_file = next((file for file in week_contents if file['name'] == problem_file_name), None)
            if matching_file:
                problem_completed = True
                solution_url = matching_file['download_url']

        # Check if the output image exists in the repository.
        for extension in image_extensions:
            image_file_name = f"{formatted_problem_number}{extension}"
            matching_image = next((file for file in week_contents if file['name'] == image_file_name), None)
            if matching_image:
                output_image_url = matching_image['download_url']

        # Create or update the problem completion record.
        if not completion:
            ProblemCompletion.objects.create(
                student=student,
                problem=problem,
                is_completed=problem_completed,
                solution_url=solution_url,
                output_image_url=output_image_url
            )
        else:
            if (completion.is_completed != problem_completed or
                completion.solution_url != solution_url or
                completion.output_image_url != output_image_url):
                completion.is_completed = problem_completed
                completion.solution_url = solution_url
                completion.output_image_url = output_image_url
                completion.save()

    def update_or_create_week_commit(self, student, week_number, repo_name, week_dir_name, headers):
        """
        Fetches the latest commit for a specific week's directory in the student's GitHub repository
        and updates the `WeekCommit` record with the last commit time and hash.

        :param student: Student object.
        :param week_number: The number of the week to fetch the commit for.
        :param repo_name: The GitHub repository name.
        :param week_dir_name: The name of the week directory.
        :param headers: The GitHub API request headers.
        :return: Boolean indicating whether the operation succeeded or failed.
        """
        url = f"https://api.github.com/repos/{student.username}/{repo_name}/commits?path={week_dir_name}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            commits = response.json()
            if commits:
                last_commit = commits[0]
                last_commit_time = parse_datetime(last_commit['commit']['committer']['date'])
                last_commit_hash = last_commit['sha']

                week_commit, created = WeekCommit.objects.get_or_create(
                    student=student,
                    week_number=week_number,
                    defaults={'last_commit_time': last_commit_time, 'last_commit_hash': last_commit_hash}
                )

                if not created:
                    if (week_commit.last_commit_time != last_commit_time or
                            week_commit.last_commit_hash != last_commit_hash):
                        week_commit.last_commit_time = last_commit_time
                        week_commit.last_commit_hash = last_commit_hash
                        week_commit.save()

            return True

        except requests.exceptions.RequestException as e:
            return False
