from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from django.views.decorators.csrf import csrf_exempt
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL  # No WD_ROW_HEIGHT exists
from docx.enum.text import WD_ALIGN_PARAGRAPH
from LabTrackerAMU import settings
from LabTrackerAMU.decorators import student_required
from teachers.models import WeekLastDate
from .forms import StudentSignUpForm
from problems.models import Problem, ProblemCompletion, WeekCommit
from django.http import HttpResponse, JsonResponse
from docx import Document
from io import BytesIO
from docx.shared import Pt, Inches, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import requests
import json
from .models import Student



def student_signup(request):
    """
    Handles the student sign-up view.

    - If the request method is POST, it processes the submitted form.
      If the form is valid, the user is saved and the page is redirected to the 'student_signup' view.
    - If the form is invalid, the form is re-rendered with validation errors.
    - If the request method is GET, an empty form is displayed for user input.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the student sign-up page with either an empty form or form with errors.
    """
    # Handle form submission if the request is a POST
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # Save the user and create the student account
            user = form.save()
            # Redirect to the same page (or another) upon successful sign-up
            return redirect('student_signup')
        else:
            # If the form is invalid, re-render the page with form errors
            return render(request, 'students/signup.html', {'form': form})

    # For GET requests, create an empty form
    else:
        form = StudentSignUpForm()

    # Render the sign-up template with the form
    return render(request, 'students/signup.html', {'form': form})


def student_login(request):
    """
    Handle the login process for students using Django's AuthenticationForm.

    This view function checks if the incoming request is a POST request (i.e., the login form has been submitted).
    If the form submission is valid, it authenticates and logs in the user. If the request method is not POST,
    the function renders a blank login form.

    Args:
        request: HttpRequest object that contains metadata about the request.

    Returns:
        HttpResponseRedirect: Redirects to the 'student_dashboard' page upon successful login.
        HttpResponse: Renders the login page with the AuthenticationForm if GET request or invalid POST data.

    Flow:
    - If the request method is POST:
        - Instantiate the AuthenticationForm with the POST data.
        - Validate the form. If valid:
            - Get the user object.
            - Authenticate and log in the user.
            - Redirect the logged-in user to the 'student_dashboard' page.
    - If the request method is GET:
        - Instantiate an empty AuthenticationForm and render the login page.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('student_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'students/login.html', {'form': form})


def student_logout(request):
    """
    Logs out the current student and redirects them to the login page.

    This view function is responsible for logging out the currently authenticated student
    by calling Django's built-in `logout` function, which clears the session data.
    Once logged out, the user is redirected to the student login page.

    Args:
        request (HttpRequest): The incoming HTTP request object that triggers the logout.

    Returns:
        HttpResponseRedirect: A redirect to the 'student_login' view after the student is logged out.

    Example Usage:
        A student clicking the "logout" button will trigger this view. Upon execution:
        - The student will be logged out, clearing their session and authentication data.
        - The student will be redirected to the login page where they can log in again.

    Notes:
        - This function uses Django's `logout` function to handle the actual session clearing and user logout.
        - No special permissions are required to access this view since it is typically triggered by authenticated users.
    """

    # Call Django's built-in logout function to clear the user's session and authentication data
    logout(request)

    # Redirect the user to the student login page after logout
    return redirect('student_login')


@student_required
def student_dashboard(request):
    """
    Handles the student dashboard view. Provides an overview of the student's progress
    by retrieving problems assigned to their course and semester, their completion status,
    weekly commits, and deadlines. The overall progress is calculated as well as weekly
    progress.

    Parameters:
    request (HttpRequest): The HTTP request object which contains the logged-in student.

    Returns:
    HttpResponse: The rendered 'students/dashboard.html' template with the student's progress data.
    """

    # Retrieve the logged-in student and their course and semester information
    student = request.user
    course = student.course
    semester = student.semester

    # Fetch problems for the student's course and semester, ordered by week and problem number
    problems = Problem.objects.filter(course=course, semester=semester).order_by('week', 'problemNumber')

    # Fetch the student's completion records for the filtered problems
    problem_completions = ProblemCompletion.objects.filter(student=student, problem__in=problems).order_by('problem')

    # Fetch WeekCommit entries for the student, ordered by week number
    week_commits = WeekCommit.objects.filter(student=student).order_by('week_number')

    # Convert week commit data into a dictionary for easy access by week number
    week_commit_data = {week_commit.week_number: week_commit for week_commit in week_commits}

    # Fetch deadlines (last dates) for each week of the student's course and semester
    week_last_dates = WeekLastDate.objects.filter(course=course, semester=semester)

    # Store week deadlines in a dictionary for quick lookup by week number
    week_last_date_data = {week_last.week: week_last.last_date for week_last in week_last_dates}

    # Initialize dictionaries to track weekly and overall progress
    weekly_progress = {}
    overall_progress = {'total': len(problems), 'completed': 0}

    # List to store the completion status of each problem for rendering purposes
    completion_list = []

    # Loop through each problem and calculate the student's progress
    for prob in problems:
        week = prob.week

        # Initialize weekly progress if it hasn't been done for the current week
        if week not in weekly_progress:
            weekly_progress[week] = {
                'total': 0,
                'completed': 0,
                'last_commit_time': None,
                'last_commit_hash': None,
                'last_date': week_last_date_data.get(week, 'No Deadline')  # Provide deadline if available
            }

        # Increment the total number of problems for the current week
        weekly_progress[week]['total'] += 1

        # Check if the current problem is completed by the student
        completion = problem_completions.filter(problem=prob).first()
        is_completed = completion and completion.is_completed

        # Append the completion status for the current problem
        completion_list.append({
            'problem_id': prob.id,
            'is_completed': is_completed
        })

        # If the problem is completed, update weekly and overall progress
        if is_completed:
            weekly_progress[week]['completed'] += 1
            overall_progress['completed'] += 1

        # If commit data is available for the week, update the last commit information
        if week in week_commit_data:
            week_commit = week_commit_data[week]
            weekly_progress[week]['last_commit_time'] = week_commit.last_commit_time
            weekly_progress[week]['last_commit_hash'] = week_commit.last_commit_hash

    # Calculate the overall completion percentage (avoid division by zero)
    overall_progress['percentage'] = (
        (overall_progress['completed'] / overall_progress['total']) * 100
        if overall_progress['total'] > 0
        else 0
    )

    # Prepare the context for rendering the template
    context = {
        'student': student,
        'weekly_progress': weekly_progress,  # Progress for each week
        'overall_progress': overall_progress,  # Overall progress across all weeks
        'problems': problems,  # List of problems for the course
        'completion_list': completion_list,  # Completion status for each problem
    }

    # Render and return the student dashboard template with the context data
    return render(request, 'students/dashboard.html', context)


@student_required
def generate_problem_doc(request):
    """
    Generates a downloadable Word document containing a structured list of problems for a student based on their course and semester.

    The document includes:
    - A title with the student's enrollment and faculty numbers in the footer.
    - A table listing the problems, organized by week and problem number, along with their descriptions and optional images.
    - Proper formatting for margins, alignment, and fonts.

    Functionality:
    1. Fetches all problems associated with the student's course and semester.
    2. Creates a Word document using python-docx.
    3. Sets margins and customizes the table layout.
    4. Merges table cells where appropriate for weeks with multiple problems.
    5. Handles images by inserting them in the corresponding table cell.
    6. Generates and returns the document as a downloadable file.

    Args:
        request: The HTTP request object. Expects the user to be logged in as a student.

    Returns:
        HttpResponse: A downloadable Word document (.docx) containing the problem list.
    """
    student = request.user
    course = student.course
    semester = student.semester

    # Fetch problems associated with the student's course and semester
    problems = Problem.objects.filter(course=course, semester=semester).order_by('week', 'problemNumber')

    # Initialize a Word document
    doc = Document()

    # Set margins
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # Add footer with student details
    footer = section.footer
    left_paragraph = footer.add_paragraph()
    left_paragraph.text = f"{student.enrollment_number}         {student.first_name}   {student.last_name}             {student.faculty_number}"
    left_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add document title
    title = doc.add_paragraph()
    title_run = title.add_run('INDEX')
    title_run.bold = True
    title_run.font.size = Pt(24)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Create table with a predefined layout
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Set column widths
    total_width = Cm(18).pt * 20
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), str(int(total_width)))
    tblW.set(qn('w:type'), 'dxa')
    tblPr.append(tblW)

    column_widths = [Cm(0.5), Cm(0.5), Cm(14), Cm(0.5), Cm(2.5)]

    # Apply column widths to the header row
    for row in table.rows:
        for idx, width in enumerate(column_widths):
            row.cells[idx].width = width

    # Set header row content
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'W\nE\nE\nK'
    hdr_cells[1].text = 'P\nR\nO\nB\nL\nE\nM'
    hdr_cells[2].text = 'PROBLEMS WITH DESCRIPTION'
    hdr_cells[3].text = 'P\nA\nG\nE'
    hdr_cells[4].text = 'SIGNATURE OF TEACHER WITH DATE'

    # Style the header row
    for cell in hdr_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(14)

    # Organize problems by week
    problems_by_week = {}
    for problem in problems:
        if problem.week not in problems_by_week:
            problems_by_week[problem.week] = []
        problems_by_week[problem.week].append(problem)

    # Add rows for each problem
    current_row_index = 1
    for week, problems_in_week in problems_by_week.items():
        num_problems = len(problems_in_week)

        for idx, problem in enumerate(problems_in_week):
            row_cells = table.add_row().cells
            row_cells[1].text = problem.problemNumber.replace('Problem ', '') + '#'
            row_cells[1].paragraphs[0].runs[0].bold = True
            row_cells[1].paragraphs[0].runs[0].font.size = Pt(11)
            row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[1].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            # Add problem description
            description_cell = row_cells[2]
            description_cell.text = problem.description
            for paragraph in description_cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Comic Sans MS'
                    run.font.size = Pt(11)
            description_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            description_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            # Add problem image (with production URL handling)
            if problem.image:
                image_url = request.build_absolute_uri(problem.image.url)
                image_path = f"{settings.MEDIA_ROOT}/{image_url.split('/')[-1]}"
                docx_image = row_cells[2].add_paragraph().add_run().add_picture(image_path, width=Cm(7))

            row_cells[3].text = ""
            row_cells[4].text = ""

        # Merge cells for weeks with multiple problems
        if num_problems > 1:
            week_cell = table.cell(current_row_index, 0)
            week_cell.merge(table.cell(current_row_index + num_problems - 1, 0))
            week_cell.text = str(week)
            week_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            week_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            week_cell.paragraphs[0].runs[0].bold = True
            week_cell.paragraphs[0].runs[0].font.size = Pt(14)

            signature_cell = table.cell(current_row_index, 4)
            signature_cell.merge(table.cell(current_row_index + num_problems - 1, 4))
            signature_cell.text = ""
            signature_cell.paragraphs[0].alignment = WD_ALIGN_VERTICAL.CENTER
            signature_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        else:
            table.cell(current_row_index, 0).text = str(week)
            table.cell(current_row_index, 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            table.cell(current_row_index, 0).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            table.cell(current_row_index, 0).paragraphs[0].runs[0].bold = True
            table.cell(current_row_index, 0).paragraphs[0].runs[0].font.size = Pt(14)
            table.cell(current_row_index, 4).text = ""
            table.cell(current_row_index, 4).alignment = WD_ALIGN_PARAGRAPH.CENTER
            table.cell(current_row_index, 4).vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        current_row_index += num_problems

    # Save document to file stream
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    # Return the Word document as a downloadable file
    response = HttpResponse(file_stream,
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="index.docx"'

    return response

def fetch_url_content(url):
    """
    Fetches the content of a given URL using an HTTP GET request.

    Args:
        url (str): The URL from which to fetch the content.

    Returns:
        str: The content of the URL if the request is successful,
             or an error message if there is an issue with the request.

    Raises:
        None: All exceptions are caught and handled within the function.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return 'Error fetching URL'


def fetch_image(url):
    """
    Fetches an image from a given URL using an HTTP GET request.

    Args:
        url (str): The URL of the image to be fetched.

    Returns:
        BytesIO: A file-like object containing the image data, if the request is successful.
        None: If there is an issue with the request or if the image cannot be fetched.

    Raises:
        None: All exceptions are caught and handled within the function.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException:
        return None
