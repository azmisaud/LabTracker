// $(document).ready(function() {
//     // Fetch semesters based on course selection
//     $('#course').change(function() {
//         var course = $(this).val();
//         $.ajax({
//             url: '/faculty/get-semesters/',
//             data: { course: course },
//             success: function(data) {
//                 $('#semester').empty();
//                 $('#semester').append('<option value="">Select Semester</option>');
//                 data.forEach(function(semester) {
//                     $('#semester').append('<option value="'+ semester +'">'+ semester +'</option>');
//                 });
//             }
//         });
//     });
//
//     // Fetch faculty numbers based on semester selection
//     $('#semester').change(function() {
//         var course = $('#course').val();
//         var semester = $(this).val();
//
//         $.ajax({
//             url: '/faculty/get-faculty-numbers/',
//             data: { course: course, semester: semester },
//             success: function(data) {
//                 $('#faculty_number').empty();
//                 $('#faculty_number').append('<option value="">Select Faculty Number</option>');
//                 data.forEach(function(faculty_number){
//                     $('#faculty_number').append('<option value="'+ faculty_number +'">'+ faculty_number +'</option>');
//                 });
//             }
//         });
//     });
//
//     // Fetch student details on button click
//     $('#check_button').click(function() {
//         var faculty_number = $('#faculty_number').val();
//         $.ajax({
//             url: '/faculty/fetch-student-details/',
//             data: { faculty_number: faculty_number },
//             success: function(data) {
//                 $('#name_display').text(data.name);
//                 $('#enrollment_number').text(data.enrollment_number);
//                 $('#faculty_number_display').text(data.faculty_number);
//                 $('#course_display').text(data.course);
//                 $('#semester_display').text(data.semester);
//                 $('#problems_solved_overall').text(data.problem_solved_overall);
//
//                 var weekly_progress='<table><thead><tr><th>Week</th><th>Solved</th><th>Problems</th><th>Commit Date</th><th>Status</th></tr></thead><tbody>';
//                 // Create table rows for weekly progress
//                 data.available_weeks.forEach(function(week,index) {
//                     var totalProblems=data.total_problems[index];
//                     var problemsSolved=data.problems_solved_weekly[index];
//                     var lastCommitTime=data.last_commit_times[index];
//                     var status=data.statuses[index];
//
//                     var lastCommitText = (typeof lastCommitTime === 'string') ? lastCommitTime : (lastCommitTime.last_commit_time || 'Not Committed');
//
//                     var lastCommitDate;
//                     if (lastCommitText!== 'Not Committed'){
//                         lastCommitDate=lastCommitText.split('T')[0];
//                     } else {
//                         lastCommitDate='Not Committed';
//                     }
//                     weekly_progress += '<tr><td>' +week+ '</td><td>' + problemsSolved + '</td><td>' + totalProblems + '</td><td>' + lastCommitDate + '</td><td>' + status + '</td></tr>';
//                 });
//
//                 weekly_progress += '</tbody></table>';
//                 $('#weekly_progress').html(weekly_progress);
//
//                 // Show the student details section and the check another button
//                 $('.form-header').hide();
//                 $('.form-section').hide();
//                 $('.form-container').addClass('expanded-width');
//                 $('.student-details').show();
//                 $('#check_another').show();
//             }
//         });
//     });
//
//     // Reset form for checking another student
//     $('#check_another').click(function() {
//         $('#course').val('');
//         $('#semester').empty();
//         $('#faculty_number').empty();
//         $('#enrollment_number').text('');
//         $('#faculty_number_display').text('');
//         $('#problems_solved_overall').text('');
//         $('#weekly_progress').html('');
//
//         // Hide the student details section and the check another button
//         $('.form-section').show();
//         $('.form-header').show();
//         $('.student-details').hide();
//         $('#check_another').hide();
//         $('.form-container').removeClass('expanded-width');
//
//     });
//
//     $('#download_pdf').click(function() {
//         const { jsPDF } = window.jspdf;
//
//         var doc = new jsPDF();
//
//         doc.setFontSize(18);
//         doc.text("Student Details",14,20);
//         doc.setFontSize(12);
//
//         doc.setTextColor(0,51,102);
//         doc.text("Name : " +$('#name_display').text(),14,30);
//
//         doc.setTextColor(0,0,0);
//
//         doc.setTextColor(64,64,64);
//         doc.text("Enrollment Number : " +$('#enrollment_number').text(),14,40);
//
//         doc.setTextColor(0,0,0);
//
//         doc.setTextColor(0,77,64);
//         doc.text("Faculty Number : " +$('#faculty_number_display').text(),14,50);
//
//         doc.setTextColor(0,0,0);
//
//         doc.text("Course : " +$('#course_display').text(),14,60);
//         doc.text("Semester : " +$('#semester_display').text(),14,70)
//         doc.text("Problems Solved Overall : " +$('#problems_solved_overall').text(),14,80);
//
//         var tableColumn=["Week", "Solved","Total","Commit Date","Status"];
//         var tableRows=[]
//
//         $('#weekly_progress tbody tr').each(function(index,row) {
//             var cols=$(row).find('td');
//             tableRows.push([
//                 $(cols[0]).text(),
//                 $(cols[1]).text(),
//                 $(cols[2]).text(),
//                 $(cols[3]).text(),
//                 $(cols[4]).text()
//             ]);
//         });
//
//         doc.autoTable({
//             head: [tableColumn],
//             body: tableRows,
//             startY: 90
//         })
//         var faculty_number=$('#faculty_number_display').text().trim();
//         doc.save(faculty_number+'.pdf');
//     });
// });

// $(document).ready(function() {
//     // Fetch semesters based on course selection
//     $('#course').change(function() {
//         var course = $(this).val();
//         $.ajax({
//             url: '/faculty/get-semesters/',
//             data: { course: course },
//             success: function(data) {
//                 $('#semester').empty();
//                 $('#semester').append('<option value="">Select Semester</option>');
//                 data.forEach(function(semester) {
//                     $('#semester').append('<option value="'+ semester +'">'+ semester +'</option>');
//                 });
//             }
//         });
//     });
//
//     // Fetch faculty numbers based on semester selection
//     $('#semester').change(function() {
//         var course = $('#course').val();
//         var semester = $(this).val();
//
//         $.ajax({
//             url: '/faculty/get-faculty-numbers/',
//             data: { course: course, semester: semester },
//             success: function(data) {
//                 $('#faculty_number').empty();
//                 $('#faculty_number').append('<option value="">Select Faculty Number</option>');
//                 data.forEach(function(faculty_number){
//                     $('#faculty_number').append('<option value="'+ faculty_number +'">'+ faculty_number +'</option>');
//                 });
//             }
//         });
//     });
//
//     // Fetch student details on button click
//     $('#check_button').click(function() {
//         var faculty_number = $('#faculty_number').val();
//         if (!faculty_number) {
//             alert('Please select a faculty number');
//             return;
//         }
//
//         $.ajax({
//             url: '/faculty/fetch-student-details/',
//             data: { faculty_number: faculty_number },
//             success: function(data) {
//                 // Update student details
//                 $('#name_display').text(data.name || 'N/A');
//                 $('#enrollment_number').text(data.enrollment_number || 'N/A');
//                 $('#faculty_number_display').text(data.faculty_number || 'N/A');
//                 $('#course_display').text(data.course || 'N/A');
//                 $('#semester_display').text(data.semester || 'N/A');
//                 $('#problems_solved_overall').text(data.problem_solved_overall || '0');
//
//                 // Clear existing table rows
//                 $('#weekly_progress tbody').empty();
//
//                 // Create table rows for weekly progress
//                 if (data.available_weeks && data.available_weeks.length > 0) {
//                     data.available_weeks.forEach(function(week, index) {
//                         var totalProblems = data.total_problems[index] || 0;
//                         var problemsSolved = data.problems_solved_weekly[index] || 0;
//                         var lastCommitTime = data.last_commit_times[index];
//                         var status = data.statuses[index] || 'Not Started';
//
//                         var lastCommitText = (typeof lastCommitTime === 'string') ? lastCommitTime : (lastCommitTime?.last_commit_time || 'Not Committed');
//                         var lastCommitDate = lastCommitText !== 'Not Committed' ? lastCommitText.split('T')[0] : 'Not Committed';
//
//                         var row = `
//                             <tr class="hover:bg-gray-50">
//                                 <td class="px-4 py-2 text-sm text-gray-900">${week}</td>
//                                 <td class="px-4 py-2 text-sm text-gray-900">${problemsSolved}</td>
//                                 <td class="px-4 py-2 text-sm text-gray-900">${totalProblems}</td>
//                                 <td class="px-4 py-2 text-sm text-gray-900">${lastCommitDate}</td>
//                                 <td class="px-4 py-2 text-sm">
//                                     <span class="px-2 py-1 rounded-full text-xs font-medium ${
//                                         status === 'Completed' ? 'bg-green-100 text-green-800' :
//                                         status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
//                                         'bg-gray-100 text-gray-800'
//                                     }">${status}</span>
//                                 </td>
//                             </tr>
//                         `;
//                         $('#weekly_progress tbody').append(row);
//                     });
//                 } else {
//                     $('#weekly_progress tbody').append(`
//                         <tr>
//                             <td colspan="5" class="px-4 py-2 text-sm text-gray-500 text-center">No weekly progress data available</td>
//                         </tr>
//                     `);
//                 }
//
//                 // Hide the form section and show the student details
//                 $('.space-y-4').hide(); // Hide the form section
//
//                 // Show student details section with proper layout
//                 $('#student_details')
//                     .removeClass('hidden')
//                     .addClass('block')
//                     .css({
//                         'display': 'block',
//                         'margin-top': '2rem'
//                     });
//
//                 // Ensure table is visible
//                 $('#weekly_progress')
//                     .css({
//                         'display': 'table',
//                         'width': '100%',
//                         'margin-top': '1rem'
//                     });
//
//                 // Show download button
//                 $('#download_pdf')
//                     .removeClass('hidden')
//                     .addClass('block')
//                     .css({
//                         'display': 'block',
//                         'margin-top': '1rem'
//                     });
//
//                 // Show check another button
//                 $('#check_another')
//                     .removeClass('hidden')
//                     .addClass('block')
//                     .css({
//                         'display': 'block',
//                         'margin-top': '1rem'
//                     });
//             },
//             error: function(xhr, status, error) {
//                 alert('Error fetching student details. Please try again.');
//                 console.error('Error:', error);
//             }
//         });
//     });
//
//     // Reset form for checking another student
//     $('#check_another').click(function() {
//         // Reset form fields
//         $('#course').val('');
//         $('#semester').empty().append('<option value="">Select Semester</option>');
//         $('#faculty_number').empty().append('<option value="">Select Faculty Number</option>');
//
//         // Clear student details
//         $('#name_display, #enrollment_number, #faculty_number_display, #course_display, #semester_display, #problems_solved_overall').text('');
//         $('#weekly_progress tbody').empty();
//
//         // Show form, hide details
//         $('.space-y-4').show(); // Show the form section
//         $('#student_details').removeClass('block').addClass('hidden');
//         $('#check_another').removeClass('block').addClass('hidden');
//     });
//
//     // PDF Download functionality
//     $('#download_pdf').click(function() {
//         const { jsPDF } = window.jspdf;
//         var doc = new jsPDF();
//
//         // Title
//         doc.setFontSize(18);
//         doc.text("Student Details", 14, 20);
//         doc.setFontSize(12);
//
//         // Student Information
//         doc.setTextColor(0, 51, 102);
//         doc.text("Name: " + $('#name_display').text(), 14, 30);
//
//         doc.setTextColor(64, 64, 64);
//         doc.text("Enrollment Number: " + $('#enrollment_number').text(), 14, 40);
//
//         doc.setTextColor(0, 77, 64);
//         doc.text("Faculty Number: " + $('#faculty_number_display').text(), 14, 50);
//
//         doc.setTextColor(0, 0, 0);
//         doc.text("Course: " + $('#course_display').text(), 14, 60);
//         doc.text("Semester: " + $('#semester_display').text(), 14, 70);
//         doc.text("Problems Solved Overall: " + $('#problems_solved_overall').text(), 14, 80);
//
//         // Table data
//         var tableColumn = ["Week", "Solved", "Total", "Commit Date", "Status"];
//         var tableRows = [];
//
//         $('#weekly_progress tbody tr').each(function() {
//             var cols = $(this).find('td');
//             tableRows.push([
//                 $(cols[0]).text(),
//                 $(cols[1]).text(),
//                 $(cols[2]).text(),
//                 $(cols[3]).text(),
//                 $(cols[4]).text().trim()
//             ]);
//         });
//
//         // Generate table
//         doc.autoTable({
//             head: [tableColumn],
//             body: tableRows,
//             startY: 90,
//             theme: 'grid',
//             styles: {
//                 fontSize: 8,
//                 cellPadding: 2
//             },
//             headStyles: {
//                 fillColor: [107, 0, 2],
//                 textColor: 255
//             }
//         });
//
//         // Save PDF
//         var faculty_number = $('#faculty_number_display').text().trim();
//         doc.save(faculty_number + '.pdf');
//     });
// });

$(document).ready(function() {
    // Fetch semesters based on course selection
    $('#course').change(function() {
        var course = $(this).val();
        $.ajax({
            url: '/faculty/get-semesters/',
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
            url: '/faculty/get-faculty-numbers/',
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
        if (!faculty_number) {
            alert('Please select a faculty number');
            return;
        }

        $.ajax({
            url: '/faculty/fetch-student-details/',
            data: { faculty_number: faculty_number },
            success: function(data) {
                // Update student details
                $('#name_display').text(data.name || 'N/A');
                $('#enrollment_number').text(data.enrollment_number || 'N/A');
                $('#faculty_number_display').text(data.faculty_number || 'N/A');
                $('#course_display').text(data.course || 'N/A');
                $('#semester_display').text(data.semester || 'N/A');
                $('#problems_solved_overall').text(data.problem_solved_overall || '0');

                // Clear existing table rows
                $('#weekly_progress tbody').empty();

                // Create table rows for weekly progress
                if (data.available_weeks && data.available_weeks.length > 0) {
                    data.available_weeks.forEach(function(week, index) {
                        var totalProblems = data.total_problems[index] || 0;
                        var problemsSolved = data.problems_solved_weekly[index] || 0;
                        var lastCommitTime = data.last_commit_times[index];
                        var status = data.statuses[index] || 'Not Started';

                        var lastCommitText = (typeof lastCommitTime === 'string') ? lastCommitTime : (lastCommitTime?.last_commit_time || 'Not Committed');
                        var lastCommitDate = lastCommitText !== 'Not Committed' ? lastCommitText.split('T')[0] : 'Not Committed';

                        var row = `
                            <tr class="hover:bg-gray-50">
                                <td class="px-4 py-2 text-sm text-gray-900">${week}</td>
                                <td class="px-4 py-2 text-sm text-gray-900">${problemsSolved}</td>
                                <td class="px-4 py-2 text-sm text-gray-900">${totalProblems}</td>
                                <td class="px-4 py-2 text-sm text-gray-900">${lastCommitDate}</td>
                                <td class="px-4 py-2 text-sm">
                                    <span class="px-2 py-1 rounded-full text-xs font-medium ${
                                        status === 'Completed' ? 'bg-green-100 text-green-800' :
                                        status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-gray-100 text-gray-800'
                                    }">${status}</span>
                                </td>
                            </tr>
                        `;
                        $('#weekly_progress tbody').append(row);
                    });
                } else {
                    $('#weekly_progress tbody').append(`
                        <tr>
                            <td colspan="5" class="px-4 py-2 text-sm text-gray-500 text-center">No weekly progress data available</td>
                        </tr>
                    `);
                }

                // Hide the form section and show the student details
                $('.space-y-4').hide(); // Hide the form section
                $('h2:contains("Check Student Details")').hide(); // Hide the main heading

                // Show student details section
                $('#student_details')
                    .removeClass('hidden')
                    .show();

                // Ensure table is visible and properly styled
                $('#weekly_progress')
                    .show()
                    .css({
                        'width': '100%',
                        'margin-top': '1rem'
                    });

                // Show download button
                $('#download_pdf')
                    .show();

                // Show check another button
                $('#check_another')
                    .removeClass('hidden')
                    .show();
            },
            error: function(xhr, status, error) {
                alert('Error fetching student details. Please try again.');
                console.error('Error:', error);
            }
        });
    });

    // Reset form for checking another student
    $('#check_another').click(function() {
        // Reset form fields
        $('#course').val('');
        $('#semester').empty().append('<option value="">Select Semester</option>');
        $('#faculty_number').empty().append('<option value="">Select Faculty Number</option>');

        // Clear student details
        $('#name_display, #enrollment_number, #faculty_number_display, #course_display, #semester_display, #problems_solved_overall').text('');
        $('#weekly_progress tbody').empty();

        // Show form and main heading, hide details
        $('.space-y-4').show(); // Show the form section
        $('h2:contains("Check Student Details")').show(); // Show the main heading
        $('#student_details').removeClass('block').addClass('hidden');
        $('#check_another').removeClass('block').addClass('hidden');
    });

    // PDF Download functionality
    $('#download_pdf').click(function() {
        const { jsPDF } = window.jspdf;
        var doc = new jsPDF();

        // Title
        doc.setFontSize(18);
        doc.text("Student Details", 14, 20);
        doc.setFontSize(12);

        // Student Information
        doc.setTextColor(0, 51, 102);
        doc.text("Name: " + $('#name_display').text(), 14, 30);

        doc.setTextColor(64, 64, 64);
        doc.text("Enrollment Number: " + $('#enrollment_number').text(), 14, 40);

        doc.setTextColor(0, 77, 64);
        doc.text("Faculty Number: " + $('#faculty_number_display').text(), 14, 50);

        doc.setTextColor(0, 0, 0);
        doc.text("Course: " + $('#course_display').text(), 14, 60);
        doc.text("Semester: " + $('#semester_display').text(), 14, 70);
        doc.text("Problems Solved Overall: " + $('#problems_solved_overall').text(), 14, 80);

        // Table data
        var tableColumn = ["Week", "Solved", "Total", "Commit Date", "Status"];
        var tableRows = [];

        $('#weekly_progress tbody tr').each(function() {
            var cols = $(this).find('td');
            tableRows.push([
                $(cols[0]).text(),
                $(cols[1]).text(),
                $(cols[2]).text(),
                $(cols[3]).text(),
                $(cols[4]).text().trim()
            ]);
        });

        // Generate table
        doc.autoTable({
            head: [tableColumn],
            body: tableRows,
            startY: 90,
            theme: 'grid',
            styles: {
                fontSize: 8,
                cellPadding: 2
            },
            headStyles: {
                fillColor: [107, 0, 2],
                textColor: 255
            }
        });

        // Save PDF
        var faculty_number = $('#faculty_number_display').text().trim();
        doc.save(faculty_number + '.pdf');
    });
});

// var classData=[];
// var course='';
// var semester='';
//
// $(document).ready(function() {
//     $('#course').change(function() {
//         course=$(this).val();
//         $.ajax({
//             url: '/faculty/get-semesters/',
//             data: { course : course },
//             success: function(data) {
//                 $('#semester').empty();
//                 $('#semester').append('<option value="">Select Semester</option>');
//                 data.forEach(function(semester) {
//                     $('#semester').append('<option value="'+semester+'">'+semester+'</option>');
//                 });
//             }
//         });
//     });
//
//     $('#semester').change(function() {
//         course=$('#course').val();
//         semester=$(this).val();
//
//         $.ajax({
//             url: '/faculty/get-weeks/',
//             data: { course : course , semester: semester},
//             success: function (data) {
//                 $('#week').empty();
//                 $('#week').append('<option value="">Select Week</option>');
//                 data.forEach(function(week) {
//                     $('#week').append('<option value="'+ week +'">'+ week +'</option>');
//                 });
//             }
//         });
//     });
//
//     $('#check_button').click(function() {
//         course=$('#course').val();
//         semester=$('#semester').val();
//         week=$('#week').val();
//
//         var reportTitle = (course && semester && week) ? course + " Sem " + semester + " Week " + week +" Report" : "Class Weekly Report";
//         $('#report-title').text(reportTitle);
//
//         $.ajax({
//             url: '/faculty/fetch-whole-class-weekly/',
//             data: { course : course, semester: semester, week: week},
//             success: function(data) {
//                 classData=data;
//                 let classReportHtml = `
//                     <thead>
//                         <tr>
//                             <th colspan="3" class="px-6 py-3 text-center text-sm font-medium text-[rgb(107,0,2)] bg-gray-50">Student Information</th>
//                             <th colspan="3" class="px-6 py-3 text-center text-sm font-medium text-[rgb(107,0,2)] bg-gray-50">Week ${week}</th>
//                         </tr>
//                         <tr>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Enrollment Number</th>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Faculty Number</th>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Name</th>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Last Commit Date</th>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Problems Solved</th>
//                             <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider sticky top-0 bg-gray-50">Status</th>
//                         </tr>
//                     </thead>
//                     <tbody class="bg-white divide-y divide-gray-200">
//                 `;
//
//                 data.forEach(function(student) {
//                     const statusClass = student.status === 'Completed' ? 'bg-green-100 text-green-800' :
//                                       student.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
//                                       'bg-red-100 text-red-800';
//
//                     const lastCommitDate = (student.last_commit_time !== 'No Commits')
//                         ? formatDate(student.last_commit_time.split('T')[0])
//                         : 'No Commits';
//
//                     classReportHtml += `
//                         <tr class="hover:bg-gray-50 transition-colors duration-150">
//                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${student.enrollment_number}</td>
//                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${student.faculty_number}</td>
//                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${student.full_name}</td>
//                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${lastCommitDate}</td>
//                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${student.problems_solved}/${student.total_problems}</td>
//                             <td class="px-6 py-4 whitespace-nowrap">
//                                 <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
//                                     ${student.status}
//                                 </span>
//                             </td>
//                         </tr>
//                     `;
//                 });
//
//                 classReportHtml += '</tbody>';
//                 $('#student_table').html(classReportHtml);
//
//                 // Hide form section and heading
//                 $('.space-y-4').hide();
//                 $('h2:contains("Check Whole Class Weekly")').hide();
//
//                 // Show student details section
//                 $('#all-student-details').removeClass('hidden').show();
//
//                 // Expand container width with transition
//                 $('#main-container').css('max-width', '1200px');
//
//                 // Log activity
//                 $.ajax({
//                     url: '/faculty/log_activity/',
//                     type: 'POST',
//                     data: {
//                         action: 'Viewed Weekly Class Report',
//                         course: course,
//                         semester: semester,
//                         week: week,
//                         csrfmiddlewaretoken: '{{ csrf_token }}'
//                     }
//                 });
//             }
//         });
//     });
//
//     $('#download_excel').click(function() {
//         downloadExcel(classData);
//
//         $.ajax({
//             url: '/faculty/log_activity/',
//             type: 'POST',
//             data: {
//                 action: 'Downloaded Weekly Class Report',
//                 course: course,
//                 semester: semester,
//                 week: week,
//                 csrfmiddlewaretoken: '{{ csrf_token }}'
//             }
//         });
//     });
//
//     $('#check_other').click(function () {
//         // Hide student details
//         $('#all-student-details').hide();
//
//         // Show form and heading
//         $('.space-y-4').show();
//         $('h2:contains("Check Whole Class Weekly")').show();
//
//         // Reset container width with transition
//         $('#main-container').css('max-width', '600px');
//
//         // Reset form fields
//         $('#course').val('');
//         $('#semester').empty().append('<option value="">Select Semester</option>');
//         $('#week').empty().append('<option value="">Select Week</option>');
//     });
//
//     async function downloadExcel(classData){
//         week=$('#week').val();
//         const ExcelJS=window.ExcelJS;
//
//         const workbook=new ExcelJS.Workbook();
//         const worksheet=workbook.addWorksheet('Class Report');
//
//         const columns= [
//             {header: 'Enrollment Number', key: 'enrollment_number',width: 25},
//             {header: 'Faculty Number', key: 'faculty_number',width: 24},
//             {header: 'Name', key:'name', width: 20},
//             {header: `Week ${week}`, key: 'week_number',width: 12},
//             {header: `Week ${week} Problems Solved`,key: 'problems',width: 10},
//             {header: 'Week ${week} status',key:'status',width: 8}
//         ];
//
//         worksheet.columns=columns;
//
//         worksheet.addRow(['','','','Commit Date','Solved','Status']);
//
//         worksheet.getRow(1).font={ bold: true, size:14};
//         worksheet.getRow(1).alignment={ horizontal: 'center', vertical: 'middle'};
//         worksheet.getRow(1).height=30;
//         worksheet.getRow(2).alignment={horizontal: 'center'};
//
//         classData.forEach(student => {
//
//             var lastCommitDate = (student.last_commit_time !== 'No Commits')
//                         ? formatDate(student.last_commit_time.split('T')[0])
//                         : 'No Commits';
//
//             let row = {
//                 enrollment_number: student.enrollment_number,
//                 faculty_number: student.faculty_number,
//                 name: student.full_name,
//                 week_number: lastCommitDate,
//                 problems: `${student.problems_solved}/${student.total_problems}`,
//                 status: student.status
//             };
//             const dataRow=worksheet.addRow(row);
//             dataRow.alignment={horizontal: 'center'};
//         });
//
//         worksheet.mergeCells(1,4,1,6);
//
//         workbook.xlsx.writeBuffer().then(buffer => {
//             const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
//             const url = URL.createObjectURL(blob);
//             const a = document.createElement('a');
//             a.href = url;
//             a.download = `${course}Sem${semester}Week${week}.xlsx`;
//             document.body.appendChild(a);
//             a.click();
//             document.body.removeChild(a);
//         });
//     }
//     function formatDate(dateString) {
//         var parts=dateString.split('-');
//         return parts[2]+'-'+parts[1]+'-'+parts[0];
//     }
// })