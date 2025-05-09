from django.contrib import admin
from .models import Student
from django.http import HttpResponse
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Student model.

    This class customizes how the Student model is displayed and managed
    within the Django admin interface. The list display shows key fields,
    and search functionality is provided for specific fields.
    """

    # Defines which fields will be displayed in the admin list view
    list_display = ('id', 'username', 'enrollment_number', 'faculty_number',
                    'course', 'semester', 'repo_name', 'date_of_birth')

    # Adds search functionality for the specified fields in the admin interface
    search_fields = ('username', 'email', 'enrollment_number')

    # Add filtering by course and semester
    list_filter = ('course', 'semester')

    # Sorting based on faculty_number
    ordering = ('faculty_number',)

    # Custom actions
    actions = ['export_to_csv', 'export_to_pdf']

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and not request.POST.getlist('_selected_action'):
            post=request.POST.copy()
            post.setlist('_selected_action', self.get_queryset(request).values_list('pk',flat=True))
            request._set_post(post)
        return super().changelist_view(request, extra_context)
    # Export to CSV
    def export_to_csv(self, request, queryset):
        if queryset is None:
            queryset=self.get_queryset(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=students.csv'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Enrollment Number', 'Faculty Number', 'Course', 'Semester', 'Repository', 'Date of Birth'])

        for student in queryset.order_by('faculty_number'):
            writer.writerow([student.id, student.username, student.enrollment_number,
                             student.faculty_number, student.course, student.semester,
                             student.repo_name, student.date_of_birth])

        return response

    export_to_csv.short_description = "Export selected students to CSV"

    # Define custom greenish teal color

    # Export to PDF with custom design
    def export_to_pdf(self, request, queryset):
        greenish_teal = colors.Color(red=32 / 255.0, green=178 / 255.0, blue=170 / 255.0)

        if queryset is None:
            queryset = self.get_queryset(request)

        # Filtered course and semester information
        courses = queryset.values_list('course', flat=True).distinct()
        semesters = queryset.values_list('semester', flat=True).distinct()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=students.pdf'

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Title and Header Design
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.maroon)
        p.drawString(50, 770, "Student List")

        p.setFont("Helvetica", 12)
        course_str = ", ".join([str(course) for course in courses])
        semester_str = ", ".join([str(sem) for sem in semesters])
        p.drawString(50, 755, f"Filtered by Course: {course_str} and Semester: {semester_str}")

        # Table Headers and Data
        data = [["ID", "Username", "Enrollment Number", "Faculty Number", "Course", "Semester"]]
        for student in queryset.order_by('faculty_number'):
            data.append([
                student.id,
                student.username,
                student.enrollment_number,
                student.faculty_number,
                student.course,
                student.semester,
            ])

        # Define Table Styles
        table = Table(data, colWidths=[0.5 * inch, 1 * inch, 2 * inch, 1.5 * inch, 1 * inch, 1 * inch])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), greenish_teal),  # Header row custom greenish teal color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Rows background
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        # Apply styles and draw the table
        table.setStyle(style)
        table.wrapOn(p, 50, 600)
        table.drawOn(p, 50, 700)  # Adjust the y-position to start right after the header

        p.save()
        buffer.seek(0)
        response.write(buffer.read())
        buffer.close()

        return response
