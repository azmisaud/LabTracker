from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.defaulttags import comment
from django.views.decorators.http import require_GET, require_POST
from LabTrackerAMU.decorators import instructor_required
from instructor.forms import InstructorLoginForm, InstructorChangePasswordForm
from instructor.models import Instructor, SelectedStudent
from problems.models import ProblemCompletion
from students.models import Student

def instructor_login(request):
    form=InstructorLoginForm()

    if request.method=='POST':
        form=InstructorLoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']

            instructor=authenticate(request,username=username,password=password)

            if instructor is not None and isinstance(instructor,Instructor):
                login(request,instructor)
                if instructor.is_first_login:
                    return redirect('instructor_change_password')
                else:
                    return redirect('instructor_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request,'instructor/instructor_login.html',{'form':form}  )

@instructor_required
def instructor_change_password(request):
    instructor=request.user
    if request.method=='POST':
        form=InstructorChangePasswordForm(user=instructor,data=request.POST)
        if form.is_valid():
            form.save()
            instructor.is_first_login=False
            instructor.save()
            messages.success(request, 'Your password has been changed. Login again to continue.')
            return redirect('instructor_login')
    else:
        form=InstructorChangePasswordForm(user=instructor)

    return render(request,'instructor/instructor_change_password.html',{'form':form})

# @require_GET
# @instructor_required
# def get_semesters_instructor(request):
#     course=request.GET.get('course')
#     semester= (
#         Student.objects.filter(course=course)
#         .values_list('semester', flat=True)
#         .distinct()
#         .order_by('semester')
#     )
#
#     return JsonResponse(list(semester),safe=False)
#
# @require_GET
# @instructor_required
# def get_students_for_mentorship(request):
#     course=request.GET.get('course')
#     semester=request.GET.get('semester')
#     instructor=request.user
#
#     selected_students=SelectedStudent.objects.filter(
#         instructor=instructor,
#     ).values_list('student', flat=True)
#
#     students=Student.objects.filter(course=course,semester=semester).order_by('faculty_number')
#
#     student_data=[]
#     for student in students:
#         student_data.append({
#             'id': student.id,
#             'name' : f"{student.first_name} {student.last_name}",
#             'faculty_number': student.faculty_number,
#             'is_selected':student.id in selected_students
#         })
#
#     return JsonResponse({'students':student_data})
#
# @require_POST
# @instructor_required
# def save_selected_students(request):
#     students=request.POST.getlist('students')
#     course=request.POST.get('course')
#     semester=request.POST.get('semester')
#
#     if len(students) <=12:
#         for student_id in students:
#             student=get_object_or_404(Student,id=student_id)
#             SelectedStudent.objects.create(instructor=request.user,student=student)
#
#         return JsonResponse({'status':'success'})
#     else:
#         return JsonResponse({'status':'error','message':'You can select a maximum of 12 students.'})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Student, SelectedStudent

@require_GET
@instructor_required
def get_semesters_instructor(request):
    course = request.GET.get('course')
    semester = (
        Student.objects.filter(course=course)
        .values_list('semester', flat=True)
        .distinct()
        .order_by('semester')
    )
    return JsonResponse(list(semester), safe=False)

@require_GET
@instructor_required
def get_students_for_mentorship(request):
    course = request.GET.get('course')
    semester = request.GET.get('semester')
    instructor = request.user

    selected_ids = list(
        SelectedStudent.objects.filter(instructor=instructor).values_list('student_id', flat=True)
    )

    all_students = list(
        Student.objects.filter(course=course, semester=semester).order_by('faculty_number')
    )

    # Sort selected students first
    sorted_students = sorted(all_students, key=lambda s: (s.id not in selected_ids, s.faculty_number))

    data = [{
        'id': s.id,
        'name': f"{s.first_name} {s.last_name}",
        'faculty_number': s.faculty_number,
        'is_selected': s.id in selected_ids
    } for s in sorted_students]

    return JsonResponse({'students': data})

@require_POST
@instructor_required
def save_selected_students(request):
    student_ids = request.POST.getlist('students[]')
    course=request.POST.get('course')
    semester=request.POST.get('semester')

    instructor = request.user

    if not course or not semester:
        return JsonResponse({'status': 'error', 'message': 'Course and semester are required'})

    new_ids = set(map(int, student_ids))

    current_ids=set(
        SelectedStudent.objects.filter(
            instructor=instructor,
            student__course=course,
            student__semester=semester
        ).values_list('student_id',flat=True)
    )

    if new_ids==current_ids:
        return JsonResponse({'status': 'success', 'message': 'No changes made'})

    if len(new_ids)>12:
        return JsonResponse({'status': 'error', 'message': 'You can select a max of 12 students'})

    to_delete=current_ids-new_ids
    SelectedStudent.objects.filter(
        instructor=instructor,
        student_id__in=to_delete,
        student__course=course,
        student__semester=semester
    ).delete()

    to_add=new_ids-current_ids
    students_to_add=Student.objects.filter(id__in=to_add,course=course,semester=semester)
    for student in students_to_add:
        SelectedStudent.objects.create(instructor=instructor,student=student)

    return JsonResponse({'status': 'success'})

@instructor_required
def select_students(request):
    return render(request, 'instructor/instructor_select_students.html')

from problems.tasks import fetch_ai_analysis_async
from collections import defaultdict, OrderedDict
@instructor_required
def instructor_dashboard(request):
   instructor=request.user
   course = request.GET.get('course')
   semester=request.GET.get('semester')
   student_id=request.GET.get('student_id')

   selected_students_qs=SelectedStudent.objects.filter(instructor=instructor).select_related('student')

   grouped_students=defaultdict(list)
   for s in selected_students_qs:
       key=f"{s.student.course} - Sem {s.student.semester}"
       grouped_students[key].append(s.student)
   sorted_grouped=OrderedDict(sorted(grouped_students.items()))

   if student_id:
       students=[get_object_or_404(Student, id=student_id)]
   elif course and semester:
       students=[s.student for s in selected_students_qs if s.student.course==course and s.student.semester==semester]
   else:
       students=[s.student for s in selected_students_qs]

   latest_submission=[]
   for student in students:
       submissions=(
           ProblemCompletion.objects
           .filter(student=student,is_completed=True)
           .select_related('problem')
           .order_by('-problem__week', '-problem__problemNumber')
       )
       for submission in submissions:
           if not submission.ai_analysis:
               fetch_ai_analysis_async(submission)

           latest_submission.append(submission)

   paginator=Paginator(latest_submission, 10)
   page_number=request.GET.get('page',1)
   try:
       page_obj = paginator.page(page_number)
   except PageNotAnInteger:
       page_obj = paginator.page(1)
   except EmptyPage:
       page_obj = paginator.page(paginator.num_pages)

   return render(request, 'instructor/instructor_dashboard.html', {
       'instructor':instructor,
       'grouped_students': sorted_grouped,
       'selected_course': course,
       'selected_semester': semester,
       'page_obj':page_obj
   })

@instructor_required
@require_POST
def submit_feedback(request,submission_id):
    instructor=request.user
    submission=get_object_or_404(
        ProblemCompletion.objects.select_related('student'),
        id=submission_id
    )

    is_selected=SelectedStudent.objects.filter(
        instructor=instructor,
        student=submission.student
    ).exists()

    if not is_selected:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    action=request.POST.get('action')
    comment_by_instructor=request.POST.get('comment')

    submission.instructor_comment=comment_by_instructor

    if action=="wrong":
        submission.is_completed=False
        submission.solution_url=None
        submission.output_image_url=None
        submission.ai_analysis=None

    submission.save()
    return JsonResponse({"success": True})

@instructor_required
def instructor_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('instructor_login')
