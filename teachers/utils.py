from django.conf import settings
from problems.models import ProblemCompletion, Problem, WeekCommit
from django.utils.dateparse import parse_datetime
import requests
from students.models import Student

def update_student_data(course, semester):
    """
    Updates the progress of students for a given course and semester by checking their problem completions
    and GitHub commits. It connects to the students' GitHub repositories, checks the files for each week's
    problems, and updates the database accordingly.

    Parameters:
    - course (str): The course the students are enrolled in.
    - semester (str): The semester of the students.

    This function uses the GitHub API to fetch repository contents and checks for specific files related
    to problems in the course. It verifies whether each student has completed their problems and updates
    the `ProblemCompletion` and `WeekCommit` models.

    External Dependencies:
    - Uses the `GITHUB_TOKEN2` from Django settings for GitHub API authentication.

    Example usage:
    ```
    update_student_data('CS101', 'Fall2024')
    ```
    """
    problems = Problem.objects.filter(course=course, semester=semester)
    students = Student.objects.filter(course=course, semester=semester)
    token = settings.GITHUB_TOKEN2

    headers = {"Authorization": f"token {token}"}

    for student in students:
        if student.is_superuser:
            continue

        repo_name = student.repo_name
        url = f"https://api.github.com/repos/{student.username}/{repo_name}/contents/"
        print(student.repo_name)
        try:
            response = requests.get(url, headers=headers)
            print(response.status_code)
            if response.status_code == 404:
                continue

            response.raise_for_status()
            repo_contents = response.json()
            week_dirs = {content['name']: content['url'] for content in repo_contents
                         if content['type'] == 'dir' and content['name'].startswith('Week')}

            week_content_cache = {}
            commit_cache = {}

            problems_by_week = {}

            # Organize problems by week
            for problem in problems:
                week_number = problem.week
                if week_number not in problems_by_week:
                    problems_by_week[week_number] = []
                problems_by_week[week_number].append(problem)

            # Iterate over each week and check if the problem files exist in the repository
            for week_number, week_problems in problems_by_week.items():
                week_dir_name = f"Week{week_number}"
                if week_dir_name not in week_dirs:
                    continue

                if week_dir_name not in week_content_cache:
                    week_url = week_dirs[week_dir_name]
                    week_response = requests.get(week_url, headers=headers)
                    week_response.raise_for_status()
                    week_content_cache[week_dir_name] = week_response.json()

                week_contents = week_content_cache[week_dir_name]

                for problem in week_problems:
                    check_problem(student, problem, week_contents)

                # Update commit information for the week
                if week_dir_name not in commit_cache:
                    commit_cache[week_dir_name] = update_week(
                        student, week_number, repo_name, week_dir_name, headers
                    )

        except requests.exceptions.RequestException as e:
            continue

def check_problem(student, problem, week_contents):
    """
    Checks whether a specific problem file exists in the student's repository for a given week.

    Parameters:
    - student (Student): The student whose repository is being checked.
    - problem (Problem): The problem being verified.
    - week_contents (list): The list of files and directories in the student's repository for the specific week.

    This function checks if a problem file with one of the allowed extensions (like .cpp, .py, etc.)
    exists in the student's GitHub repository for the specified week. It also checks for associated
    output image files. The results are recorded in the `ProblemCompletion` model.

    File extensions checked:
    - Source code: ['.cpp', '.java', '.py', '.c', '.js', '.rb', '.go', '.swift']
    - Image files: ['.jpg', '.jpeg', '.png']

    Example usage:
    ```
    check_problem(student, problem, week_contents)
    ```
    """
    file_extensions = ['.cpp', '.java', '.py', '.c', '.js', '.rb', '.go', '.swift']
    image_extensions = ['.jpg', '.jpeg', '.png']
    formatted_problem_number = problem.problemNumber.replace(" ", "")

    completion = ProblemCompletion.objects.filter(student=student, problem=problem).first()

    problem_completed = False
    solution_url = None
    output_image_url = None

    # Check for solution files
    for extension in file_extensions:
        problem_file_name = f"{formatted_problem_number}{extension}"
        matching_file = next((file for file in week_contents if file['name'] == problem_file_name), None)
        if matching_file:
            problem_completed = True
            solution_url = matching_file['download_url']

    # Check for output image files
    for extension in image_extensions:
        image_file_name = f"{formatted_problem_number}{extension}"
        matching_image = next((file for file in week_contents if file['name'] == image_file_name), None)
        if matching_image:
            output_image_url = matching_image['download_url']

    # Update or create ProblemCompletion object
    if not completion:
        completion = ProblemCompletion.objects.create(
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

def update_week(student, week_number, repo_name, week_dir_name, headers):
    """
    Updates the commit information for a specific week by retrieving the latest commit from the student's
    GitHub repository for that week's directory.

    Parameters:
    - student (Student): The student whose repository is being checked.
    - week_number (int): The week number being checked.
    - repo_name (str): The name of the student's GitHub repository.
    - week_dir_name (str): The name of the directory for the specific week in the repository.
    - headers (dict): The authorization headers for the GitHub API request.

    This function queries the GitHub API for the commit history of a specific directory (representing a week).
    It stores the latest commit's timestamp and hash in the `WeekCommit` model.

    Example usage:
    ```
    update_week(student, 3, 'repo_name', 'Week3', headers)
    ```
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
