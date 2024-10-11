var classData=[];
var course='';
var semester='';

$(document).ready(function() {
    $('#course').change(function() {
        course=$(this).val();
        $.ajax({
            url: '/faculty/get-semesters/',
            data: { course : course },
            success: function(data) {
                $('#semester').empty();
                $('#semester').append('<option value="">Select Semester</option>');
                data.forEach(function(semester) {
                    $('#semester').append('<option value="'+semester+'">'+semester+'</option>');
                });
            }
        });
    });

    $('#semester').change(function() {
        course=$('#course').val();
        semester=$(this).val();

        $.ajax({
            url: '/faculty/get-weeks/',
            data: { course : course , semester: semester},
            success: function (data) {
                $('#week').empty();
                $('#week').append('<option value="">Select Week</option>');
                data.forEach(function(week) {
                    $('#week').append('<option value="'+ week +'">'+ week +'</option>');
                });
            }
        });
    });

    $('#check_button').click(function() {
        course=$('#course').val();
        semester=$('#semester').val();
        week=$('#week').val();

        var reportTitle = (course && semester && week) ? course + " Sem " + semester + " Week " + week +" Report" : "Class Weekly Report";
        $('#report-title').text(reportTitle);

        $.ajax({
            url: '/faculty/fetch-whole-class-weekly/',
            data: { course : course, semester: semester, week: week},
            success: function(data) {
                classData=data;
                var classReportHtml='<table><thead><tr><th>Enrollment Number</th><th>Faculty Number</th><th>Name</th>';

                classReportHtml+='<th colspan="3">Week '+ week + '</th>';

                classReportHtml+='</tr><tr>'

                classReportHtml+='<th></th><th></th><th></th>'
                classReportHtml+='<th>Last Commit Date</th><th>Problems Solved</th><th>Status</th>'

                classReportHtml+='</tr></thead></tbody>';

                data.forEach(function(student) {
                    classReportHtml+='<tr>';
                    classReportHtml+='<td>'+student.enrollment_number +'</td>';
                    classReportHtml+='<td>'+student.faculty_number +'</td>';
                    classReportHtml+='<td>'+student.full_name + '</td>'

                    var lastCommitDate = (student.last_commit_time !== 'No Commits')
                        ? formatDate(student.last_commit_time.split('T')[0])
                        : 'No Commits';

                    classReportHtml+='<td>' + lastCommitDate +'</td>';
                    classReportHtml+='<td>' + student.problems_solved+"/" + student.total_problems + '</td>';
                    classReportHtml+='<td>' + student.status + '</td>';
                });

                classReportHtml+='</tbody></table>';

                $('#student_table').html(classReportHtml);

                $('.form-section').hide();
                $('.form-header').hide();
                $('.form-container').addClass('expanded-width');
                $('.all-student-details').show();

                $.ajax({
                    url: '/faculty/log_activity/',
                    type: 'POST',
                    data: {
                        action: 'Viewed Weekly Class Report',
                        course: course,
                        semester: semester,
                        week: week,
                        csrfmiddlewaretoken: '{{ csrf_token }}'
                    }
                });
            }
        });
    });

    $('#download_excel').click(function() {
        downloadExcel(classData);

        $.ajax({
            url: '/faculty/log_activity/',
            type: 'POST',
            data: {
                action: 'Downloaded Weekly Class Report',
                course: course,
                semester: semester,
                week: week,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            }
        });
    });

    $('#check_other').click(function () {
        $('.all-student-details').hide();
        $('.form-section').show();
        $('.form-header').show();
        $('#course').val('');
        $('#semester').empty().append('<option value="">Select Semester</option>');
        $('#week').empty().append('<option value="">Select Week</option>')
        $('.form-container').removeClass('expanded-width');
    });

    async function downloadExcel(classData){
        week=$('#week').val();
        const ExcelJS=window.ExcelJS;

        const workbook=new ExcelJS.Workbook();
        const worksheet=workbook.addWorksheet('Class Report');

        const columns= [
            {header: 'Enrollment Number', key: 'enrollment_number',width: 25},
            {header: 'Faculty Number', key: 'faculty_number',width: 24},
            {header: 'Name', key:'name', width: 20},
            {header: `Week ${week}`, key: 'week_number',width: 12},
            {header: `Week ${week} Problems Solved`,key: 'problems',width: 10},
            {header: 'Week ${week} status',key:'status',width: 8}
        ];

        worksheet.columns=columns;

        worksheet.addRow(['','','','Commit Date','Solved','Status']);

        worksheet.getRow(1).font={ bold: true, size:14};
        worksheet.getRow(1).alignment={ horizontal: 'center', vertical: 'middle'};
        worksheet.getRow(1).height=30;
        worksheet.getRow(2).alignment={horizontal: 'center'};

        classData.forEach(student => {

            var lastCommitDate = (student.last_commit_time !== 'No Commits')
                        ? formatDate(student.last_commit_time.split('T')[0])
                        : 'No Commits';

            let row = {
                enrollment_number: student.enrollment_number,
                faculty_number: student.faculty_number,
                name: student.full_name,
                week_number: lastCommitDate,
                problems: `${student.problems_solved}/${student.total_problems}`,
                status: student.status
            };
            const dataRow=worksheet.addRow(row);
            dataRow.alignment={horizontal: 'center'};
        });

        worksheet.mergeCells(1,4,1,6);

        workbook.xlsx.writeBuffer().then(buffer => {
            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${course}Sem${semester}Week${week}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }
    function formatDate(dateString) {
        var parts=dateString.split('-');
        return parts[2]+'-'+parts[1]+'-'+parts[0];
    }
})