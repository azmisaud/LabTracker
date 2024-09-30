$(document).ready(function() {
    // Fetch semesters based on course selection
    $('#course').change(function() {
        var course = $(this).val();
        $.ajax({
            url: '/teachers/get-semesters/',
            data: { course: course },
            success: function(data) {
                $('#semester').empty();
                $('#semester').append('<option value="">Select Semester</option>');
                data.forEach(function(semester) {
                    $('#semester').append('<option value="'+ semester +'">'+ semester +'</option>');
                });
            }
        });
    });

    // Fetch faculty numbers based on semester selection
    $('#semester').change(function() {
        var course = $('#course').val();
        var semester = $(this).val();

        $.ajax({
            url: '/teachers/get-faculty-numbers/',
            data: { course: course, semester: semester },
            success: function(data) {
                $('#faculty_number').empty();
                $('#faculty_number').append('<option value="">Select Faculty Number</option>');
                data.forEach(function(faculty_number){
                    $('#faculty_number').append('<option value="'+ faculty_number +'">'+ faculty_number +'</option>');
                });
            }
        });
    });

    // Fetch student details on button click
    $('#check_button').click(function() {
        var faculty_number = $('#faculty_number').val();
        $.ajax({
            url: '/teachers/fetch-student-details/',
            data: { faculty_number: faculty_number },
            success: function(data) {
                $('#name_display').text(data.name);
                $('#enrollment_number').text(data.enrollment_number);
                $('#faculty_number_display').text(data.faculty_number);
                $('#course_display').text(data.course);
                $('#semester_display').text(data.semester);
                $('#problems_solved_overall').text(data.problem_solved_overall);

                var weekly_progress='<table><thead><tr><th>Week</th><th>Solved</th><th>Problems</th><th>Commit Date</th><th>Status</th></tr></thead><tbody>';
                // Create table rows for weekly progress
                data.available_weeks.forEach(function(week,index) {
                    var totalProblems=data.total_problems[index];
                    var problemsSolved=data.problems_solved_weekly[index];
                    var lastCommitTime=data.last_commit_times[index];
                    var status=data.statuses[index];

                    var lastCommitText = (typeof lastCommitTime === 'string') ? lastCommitTime : (lastCommitTime.last_commit_time || 'Not Committed');

                    var lastCommitDate;
                    if (lastCommitText!== 'Not Committed'){
                        lastCommitDate=lastCommitText.split('T')[0];
                    } else {
                        lastCommitDate='Not Committed';
                    }
                    weekly_progress += '<tr><td>' +week+ '</td><td>' + problemsSolved + '</td><td>' + totalProblems + '</td><td>' + lastCommitDate + '</td><td>' + status + '</td></tr>';
                });

                weekly_progress += '</tbody></table>';
                $('#weekly_progress').html(weekly_progress);

                // Show the student details section and the check another button
                $('.form-header').hide();
                $('.form-section').hide();
                $('.form-container').addClass('expanded-width');
                $('.student-details').show();
                $('#check_another').show();
            }
        });
    });

    // Reset form for checking another student
    $('#check_another').click(function() {
        $('#course').val('');
        $('#semester').empty();
        $('#faculty_number').empty();
        $('#enrollment_number').text('');
        $('#faculty_number_display').text('');
        $('#problems_solved_overall').text('');
        $('#weekly_progress').html('');

        // Hide the student details section and the check another button
        $('.form-section').show();
        $('.form-header').show();
        $('.student-details').hide();
        $('#check_another').hide();
        $('.form-container').removeClass('expanded-width');

    });

    $('#download_pdf').click(function() {
        const { jsPDF } = window.jspdf;

        var doc = new jsPDF();

        doc.setFontSize(18);
        doc.text("Student Details",14,20);
        doc.setFontSize(12);

        doc.setTextColor(0,51,102);
        doc.text("Name : " +$('#name_display').text(),14,30);

        doc.setTextColor(0,0,0);

        doc.setTextColor(64,64,64);
        doc.text("Enrollment Number : " +$('#enrollment_number').text(),14,40);

        doc.setTextColor(0,0,0);

        doc.setTextColor(0,77,64);
        doc.text("Faculty Number : " +$('#faculty_number_display').text(),14,50);

        doc.setTextColor(0,0,0);

        doc.text("Course : " +$('#course_display').text(),14,60);
        doc.text("Semester : " +$('#semester_display').text(),14,70)
        doc.text("Problems Solved Overall : " +$('#problems_solved_overall').text(),14,80);

        var tableColumn=["Week", "Solved","Total","Commit Date","Status"];
        var tableRows=[]

        $('#weekly_progress tbody tr').each(function(index,row) {
            var cols=$(row).find('td');
            tableRows.push([
                $(cols[0]).text(),
                $(cols[1]).text(),
                $(cols[2]).text(),
                $(cols[3]).text(),
                $(cols[4]).text()
            ]);
        });

        doc.autoTable({
            head: [tableColumn],
            body: tableRows,
            startY: 90
        })
        var faculty_number=$('#faculty_number_display').text().trim();
        doc.save(faculty_number+'.pdf');
    });
});