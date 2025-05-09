// // var classData=[];
// // var course='';
// // var semester='';
// // $(document).ready(function () {
// //     // Fetch semesters based on course selection
// //     $('#course').change(function() {
// //         course = $(this).val();
// //         $.ajax({
// //             url: '/faculty/get-semesters/',
// //             data: { course: course },
// //             success: function(data) {
// //                 $('#semester').empty();
// //                 $('#semester').append('<option value="">Select Semester</option>');
// //                 data.forEach(function(semester) {
// //                     $('#semester').append('<option value="'+ semester +'">'+ semester +'</option>');
// //                 });
// //             }
// //         });
// //     });
// //
// //     $('#check_button').click(function() {
// //     course = $('#course').val();
// //     semester = $('#semester').val();
// //
// //     var reportTitle = (course && semester) ? course + " Sem " + semester + " Report" : "Class Report";
// //     $('#report-title').text(reportTitle);
// //
// //     $.ajax({
// //         url: '/faculty/fetch-whole-class/',  // Adjusted URL to fetch data for the whole class
// //         data: { course: course, semester: semester },
// //         success: function(data) {
// //             classData=data;
// //             var classReportHtml = '<table><thead><tr><th>Enrollment Number</th><th>Faculty Number</th><th>Name</th>';
// //
// //             if (classData.length > 0 && classData[0].weeks_data.length > 0){
// //                 classData[0].weeks_data.forEach(function (week) {
// //                     classReportHtml+='<th colspan="3"> Week ' +week.week +'</th>';
// //                 });
// //             }
// //             classReportHtml+='</tr><tr>';
// //             classReportHtml+='<th></th><th></th><th></th>';
// //
// //             if (classData.length>0 && classData[0].weeks_data.length>0){
// //                 classData[0].weeks_data.forEach(function(week) {
// //                     classReportHtml+='<th>Solved</th><th>Commit Date</th><th>Status</th>';
// //                 });
// //             }
// //             classReportHtml+='</tr></thead><tbody>';
// //
// //             data.forEach(function (student) {
// //                 classReportHtml+='<tr>';
// //                 classReportHtml+='<td>'+student.enrollment_number + '</td>';
// //                 classReportHtml+='<td>'+student.faculty_number +'</td>';
// //                 classReportHtml+='<td>'+student.name + '</td>';
// //
// //                 student.weeks_data.forEach(function (week) {
// //                     classReportHtml+='<td>'+week.problems_solved + '/' + week.total_problems + '</td>';
// //
// //                     var lastCommitDate=(week.last_commit_time !== 'No Commits')
// //                                                 ? formatDate(week.last_commit_time.split('T')[0])
// //                                                 : 'No Commits';
// //
// //                     classReportHtml+='<td>' + lastCommitDate + '</td>';
// //                     classReportHtml+='<td>' + week.commit_status + '</td>';
// //                 });
// //                 classReportHtml+='</tr>';
// //             });
// //
// //             classReportHtml += '</tbody></table>';
// //             $('#student_table').html(classReportHtml);
// //
// //             // Show the student details section and the check another button
// //             $('.form-section').hide();
// //             $('.form-header').hide();
// //             $('.form-container').addClass('expanded-width2');
// //             $('.all-student-details').show();
// //
// //             $.ajax({
// //                 url: '/faculty/log_activity/',
// //                 type: 'POST',
// //                 data: {
// //                     action: 'Viewed Class Report',
// //                     course: course,
// //                     semester: semester,
// //                     csrfmiddlewaretoken: '{{ csrf_token }}'
// //                 },
// //                 success: function (response) {
// //                     console.log('Activity logged successfully');
// //                 },
// //                 error: function (xhr, status, error) {
// //                     console.error('Error logging activity: ', error);
// //                 }
// //             });
// //         }
// //     });
// // });
// //
// //     $('#check_other').click(function () {
// //         $('.all-student-details').hide();
// //         $('.form-section').show();
// //         $('.form-header').show();
// //         $('#course').val('');
// //         $('#semester').empty().append('<option value="">Select Semester</option>');
// //         $('.form-container').removeClass('expanded-width2');
// //     });
// //
// //    $('#download_excel').click(function () {
// //        downloadExcel(classData);
// //
// //        $.ajax({
// //            url: '/faculty/log_activity/',
// //            type: 'POST',
// //            data: {
// //                action: 'Downloaded Class Report',
// //                course: $('#course').val(),
// //                semester: $('#semester').val(),
// //                csrfmiddlewaretoken: '{{ csrf_token }}'
// //            }
// //        });
// //    });
// //
// //     async function downloadExcel(classData) {
// //     const ExcelJS = window.ExcelJS; // Ensure `ExcelJS` is available globally
// //
// //     const workbook = new ExcelJS.Workbook();
// //     const worksheet = workbook.addWorksheet('Class Report');
// //
// //     // Define columns
// //     const columns = [
// //         { header: 'Enroll no.', key: 'enrollment_number', width: 12 },
// //         { header: 'Faculty no.', key: 'faculty_number', width: 14 },
// //         { header: 'Name' , key: 'name',width: 20}
// //     ];
// //
// //     if (classData.length>0 && classData[0].weeks_data.length>0){
// //         classData[0].weeks_data.forEach((weekData, index) => {
// //             columns.push({header: `Week ${weekData.week}`,key:`week_${weekData.week}_solved`,width:7});
// //             columns.push({header: `Week ${weekData.week} Commit Date`,key:`week_${weekData.week}_commit_date`,width:12});
// //             columns.push({header: `Week ${weekData.week} Status`,key:`week_${weekData.week}_status`,width:7});
// //         });
// //     }
// //
// //     worksheet.columns = columns;
// //
// //     worksheet.addRow(['','','',...Array.from({ length : classData[0].weeks_data.length }, () => ['Solved','Commit Date','Status']).flat()]);
// //
// //     worksheet.getRow(1).font = { bold: true, size:14};
// //     worksheet.getRow(1).alignment={ horizontal: 'center', vertical: 'middle'};
// //     worksheet.getRow(1).height = 30;
// //     worksheet.getRow(2).alignment={ horizontal: 'center'};
// //
// //     classData.forEach(student => {
// //         let row = {
// //             enrollment_number: student.enrollment_number,
// //             faculty_number: student.faculty_number,
// //             name: student.name
// //         };
// //
// //         student.weeks_data.forEach(week => {
// //             row[`week_${week.week}_solved`]=`${week.problems_solved}/${week.total_problems}`;
// //             row[`week_${week.week}_commit_date`]=week.last_commit_time !== 'No Commits'
// //                     ? formatDate(week.last_commit_time.split('T')[0])
// //                     : 'No Commits';
// //             row[`week_${week.week}_status`]=week.commit_status;
// //         });
// //
// //         const dataRow=worksheet.addRow(row);
// //         dataRow.alignment = {horizontal: 'center'};
// //     });
// //
// //     let startColumn=4;
// //     classData[0].weeks_data.forEach(() => {
// //         worksheet.mergeCells(1,startColumn,1,startColumn+2);
// //         startColumn+=3;
// //     });
// //
// //     // Write to file
// //     workbook.xlsx.writeBuffer().then(buffer => {
// //         const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
// //         const url = URL.createObjectURL(blob);
// //         const a = document.createElement('a');
// //         a.href = url;
// //         a.download = `${course}Sem${semester}.xlsx`;
// //         document.body.appendChild(a);
// //         a.click();
// //         document.body.removeChild(a);
// //     });
// // }
// //
// //
// //
// //     function formatDate(dateString) {
// //         var parts=dateString.split('-');
// //         return parts[2]+'-'+parts[1]+'-'+parts[0];
// //     }
// //
// // })
//
// var classData = [];
// var course = '';
// var semester = '';
//
// $(document).ready(function () {
//     // Fetch semesters based on course selection
//     $('#course').change(function() {
//         course = $(this).val();
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
//     $('#check_button').click(function() {
//         course = $('#course').val();
//         semester = $('#semester').val();
//
//         if (!course || !semester) {
//             alert('Please select both course and semester');
//             return;
//         }
//
//         var reportTitle = course + " Sem " + semester + " Report";
//         $('#report-title').text(reportTitle);
//
//         $.ajax({
//             url: '/faculty/fetch-whole-class/',
//             data: { course: course, semester: semester },
//             success: function(data) {
//                 classData = data;
//                 var classReportHtml = '<table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr>';
//
//                 // Add main headers
//                 classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Enrollment Number</th>';
//                 classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Faculty Number</th>';
//                 classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Name</th>';
//
//                 // Add week headers if data exists
//                 if (classData.length > 0 && classData[0].weeks_data.length > 0) {
//                     classData[0].weeks_data.forEach(function(week) {
//                         classReportHtml += '<th scope="col" colspan="3" class="px-6 py-3 text-center text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Week ' + week.week + '</th>';
//                     });
//                 }
//
//                 classReportHtml += '</tr><tr>';
//
//                 // Add subheaders for each week
//                 classReportHtml += '<th></th><th></th><th></th>';
//                 if (classData.length > 0 && classData[0].weeks_data.length > 0) {
//                     classData[0].weeks_data.forEach(function(week) {
//                         classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Solved</th>';
//                         classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Commit Date</th>';
//                         classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Status</th>';
//                     });
//                 }
//
//                 classReportHtml += '</tr></thead><tbody class="bg-white divide-y divide-gray-200">';
//
//                 // Add student data rows
//                 data.forEach(function(student) {
//                     classReportHtml += '<tr class="hover:bg-gray-50">';
//                     classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.enrollment_number + '</td>';
//                     classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.faculty_number + '</td>';
//                     classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.name + '</td>';
//
//                     student.weeks_data.forEach(function(week) {
//                         // Problems solved cell
//                         classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' +
//                             week.problems_solved + '/' + week.total_problems + '</td>';
//
//                         // Commit date cell
//                         var lastCommitDate = (week.last_commit_time !== 'No Commits')
//                             ? formatDate(week.last_commit_time.split('T')[0])
//                             : 'No Commits';
//                         classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + lastCommitDate + '</td>';
//
//                         // Status cell with conditional styling
//                         var statusClass = '';
//                         if (week.commit_status === 'On Time') {
//                             statusClass = 'text-green-600';
//                         } else if (week.commit_status === 'Late') {
//                             statusClass = 'text-red-600';
//                         } else {
//                             statusClass = 'text-gray-600';
//                         }
//                         classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm ' + statusClass + '">' +
//                             week.commit_status + '</td>';
//                     });
//
//                     classReportHtml += '</tr>';
//                 });
//
//                 classReportHtml += '</tbody></table>';
//                 $('#student_table').html(classReportHtml);
//
//                 // Show the student details section and adjust container width
//                 $('#main-container').addClass('max-w-[95%]');
//                 $('#all-student-details').removeClass('hidden');
//
//                 // Log activity
//                 $.ajax({
//                     url: '/faculty/log_activity/',
//                     type: 'POST',
//                     data: {
//                         action: 'Viewed Class Report',
//                         course: course,
//                         semester: semester,
//                         csrfmiddlewaretoken: '{{ csrf_token }}'
//                     },
//                     success: function(response) {
//                         console.log('Activity logged successfully');
//                     },
//                     error: function(xhr, status, error) {
//                         console.error('Error logging activity: ', error);
//                     }
//                 });
//             },
//             error: function(xhr, status, error) {
//                 console.error('Error fetching class data:', error);
//                 alert('Error fetching class data. Please try again.');
//             }
//         });
//     });
//
//     $('#check_other').click(function() {
//         $('#all-student-details').addClass('hidden');
//         $('#main-container').removeClass('max-w-[95%]');
//         $('#course').val('');
//         $('#semester').empty().append('<option value="">Select Semester</option>');
//     });
//
//     $('#download_excel').click(function() {
//         downloadExcel(classData);
//
//         $.ajax({
//             url: '/faculty/log_activity/',
//             type: 'POST',
//             data: {
//                 action: 'Downloaded Class Report',
//                 course: course,
//                 semester: semester,
//                 csrfmiddlewaretoken: '{{ csrf_token }}'
//             }
//         });
//     });
//
//     async function downloadExcel(classData) {
//         const ExcelJS = window.ExcelJS;
//         const workbook = new ExcelJS.Workbook();
//         const worksheet = workbook.addWorksheet('Class Report');
//
//         // Define columns
//         const columns = [
//             { header: 'Enroll no.', key: 'enrollment_number', width: 12 },
//             { header: 'Faculty no.', key: 'faculty_number', width: 14 },
//             { header: 'Name', key: 'name', width: 20 }
//         ];
//
//         if (classData.length > 0 && classData[0].weeks_data.length > 0) {
//             classData[0].weeks_data.forEach((weekData, index) => {
//                 columns.push({ header: `Week ${weekData.week}`, key: `week_${weekData.week}_solved`, width: 7 });
//                 columns.push({ header: `Week ${weekData.week} Commit Date`, key: `week_${weekData.week}_commit_date`, width: 12 });
//                 columns.push({ header: `Week ${weekData.week} Status`, key: `week_${weekData.week}_status`, width: 7 });
//             });
//         }
//
//         worksheet.columns = columns;
//
//         // Add subheaders
//         worksheet.addRow(['', '', '', ...Array.from({ length: classData[0].weeks_data.length }, () => ['Solved', 'Commit Date', 'Status']).flat()]);
//
//         // Style headers
//         worksheet.getRow(1).font = { bold: true, size: 14 };
//         worksheet.getRow(1).alignment = { horizontal: 'center', vertical: 'middle' };
//         worksheet.getRow(1).height = 30;
//         worksheet.getRow(2).alignment = { horizontal: 'center' };
//
//         // Add data rows
//         classData.forEach(student => {
//             let row = {
//                 enrollment_number: student.enrollment_number,
//                 faculty_number: student.faculty_number,
//                 name: student.name
//             };
//
//             student.weeks_data.forEach(week => {
//                 row[`week_${week.week}_solved`] = `${week.problems_solved}/${week.total_problems}`;
//                 row[`week_${week.week}_commit_date`] = week.last_commit_time !== 'No Commits'
//                     ? formatDate(week.last_commit_time.split('T')[0])
//                     : 'No Commits';
//                 row[`week_${week.week}_status`] = week.commit_status;
//             });
//
//             const dataRow = worksheet.addRow(row);
//             dataRow.alignment = { horizontal: 'center' };
//         });
//
//         // Merge week header cells
//         let startColumn = 4;
//         classData[0].weeks_data.forEach(() => {
//             worksheet.mergeCells(1, startColumn, 1, startColumn + 2);
//             startColumn += 3;
//         });
//
//         // Write to file
//         workbook.xlsx.writeBuffer().then(buffer => {
//             const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
//             const url = URL.createObjectURL(blob);
//             const a = document.createElement('a');
//             a.href = url;
//             a.download = `${course}Sem${semester}.xlsx`;
//             document.body.appendChild(a);
//             a.click();
//             document.body.removeChild(a);
//         });
//     }
//
//     function formatDate(dateString) {
//         var parts = dateString.split('-');
//         return parts[2] + '-' + parts[1] + '-' + parts[0];
//     }
// });

var classData = [];
var course = '';
var semester = '';

$(document).ready(function () {
    // Fetch semesters based on course selection
    $('#course').change(function() {
        course = $(this).val();
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

    $('#check_button').click(function() {
        course = $('#course').val();
        semester = $('#semester').val();

        if (!course || !semester) {
            alert('Please select both course and semester');
            return;
        }

        // Hide the form section
        $('.space-y-4').hide();
        $('h2').hide();

        var reportTitle = course + " Sem " + semester + " Report";
        $('#report-title').text(reportTitle);

        $.ajax({
            url: '/faculty/fetch-whole-class/',
            data: { course: course, semester: semester },
            success: function(data) {
                classData = data;
                var classReportHtml = '<table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr>';

                // Add main headers
                classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Enrollment Number</th>';
                classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Faculty Number</th>';
                classReportHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Name</th>';

                // Add week headers if data exists
                if (classData.length > 0 && classData[0].weeks_data.length > 0) {
                    classData[0].weeks_data.forEach(function(week) {
                        classReportHtml += '<th scope="col" colspan="3" class="px-6 py-3 text-center text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Week ' + week.week + '</th>';
                    });
                }

                classReportHtml += '</tr><tr>';

                // Add subheaders for each week
                classReportHtml += '<th></th><th></th><th></th>';
                if (classData.length > 0 && classData[0].weeks_data.length > 0) {
                    classData[0].weeks_data.forEach(function(week) {
                        classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Solved</th>';
                        classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Commit Date</th>';
                        classReportHtml += '<th class="px-6 py-3 text-left text-xs font-medium text-[rgb(107,0,2)] uppercase tracking-wider">Status</th>';
                    });
                }

                classReportHtml += '</tr></thead><tbody class="bg-white divide-y divide-gray-200">';

                // Add student data rows
                data.forEach(function(student) {
                    classReportHtml += '<tr class="hover:bg-gray-50">';
                    classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.enrollment_number + '</td>';
                    classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.faculty_number + '</td>';
                    classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + student.name + '</td>';

                    student.weeks_data.forEach(function(week) {
                        // Problems solved cell
                        classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' +
                            week.problems_solved + '/' + week.total_problems + '</td>';

                        // Commit date cell
                        var lastCommitDate = (week.last_commit_time !== 'No Commits')
                            ? formatDate(week.last_commit_time.split('T')[0])
                            : 'No Commits';
                        classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">' + lastCommitDate + '</td>';

                        // Status cell with conditional styling
                        var statusClass = '';
                        if (week.commit_status === 'On Time') {
                            statusClass = 'text-green-600';
                        } else if (week.commit_status === 'Late') {
                            statusClass = 'text-red-600';
                        } else {
                            statusClass = 'text-gray-600';
                        }
                        classReportHtml += '<td class="px-6 py-4 whitespace-nowrap text-sm ' + statusClass + '">' +
                            week.commit_status + '</td>';
                    });

                    classReportHtml += '</tr>';
                });

                classReportHtml += '</tbody></table>';
                $('#student_table').html(classReportHtml);

                // Show the student details section and adjust container width
                $('#main-container').addClass('max-w-[95%]');
                $('#all-student-details').removeClass('hidden');

                // Log activity
                $.ajax({
                    url: '/faculty/log_activity/',
                    type: 'POST',
                    data: {
                        action: 'Viewed Class Report',
                        course: course,
                        semester: semester,
                        csrfmiddlewaretoken: '{{ csrf_token }}'
                    },
                    success: function(response) {
                        console.log('Activity logged successfully');
                    },
                    error: function(xhr, status, error) {
                        console.error('Error logging activity: ', error);
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching class data:', error);
                alert('Error fetching class data. Please try again.');
            }
        });
    });

    $('#check_other').click(function() {
        $('#all-student-details').addClass('hidden');
        $('#main-container').removeClass('max-w-[95%]');
        // Show the form section again
        $('.space-y-4').show();
        $('h2').show();
        $('#course').val('');
        $('#semester').empty().append('<option value="">Select Semester</option>');
    });

    $('#download_excel').click(function() {
        downloadExcel(classData);

        $.ajax({
            url: '/faculty/log_activity/',
            type: 'POST',
            data: {
                action: 'Downloaded Class Report',
                course: course,
                semester: semester,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            }
        });
    });

    async function downloadExcel(classData) {
        const ExcelJS = window.ExcelJS;
        const workbook = new ExcelJS.Workbook();
        const worksheet = workbook.addWorksheet('Class Report');

        // Define columns
        const columns = [
            { header: 'Enroll no.', key: 'enrollment_number', width: 12 },
            { header: 'Faculty no.', key: 'faculty_number', width: 14 },
            { header: 'Name', key: 'name', width: 20 }
        ];

        if (classData.length > 0 && classData[0].weeks_data.length > 0) {
            classData[0].weeks_data.forEach((weekData, index) => {
                columns.push({ header: `Week ${weekData.week}`, key: `week_${weekData.week}_solved`, width: 7 });
                columns.push({ header: `Week ${weekData.week} Commit Date`, key: `week_${weekData.week}_commit_date`, width: 12 });
                columns.push({ header: `Week ${weekData.week} Status`, key: `week_${weekData.week}_status`, width: 7 });
            });
        }

        worksheet.columns = columns;

        // Add subheaders
        worksheet.addRow(['', '', '', ...Array.from({ length: classData[0].weeks_data.length }, () => ['Solved', 'Commit Date', 'Status']).flat()]);

        // Style headers
        worksheet.getRow(1).font = { bold: true, size: 14 };
        worksheet.getRow(1).alignment = { horizontal: 'center', vertical: 'middle' };
        worksheet.getRow(1).height = 30;
        worksheet.getRow(2).alignment = { horizontal: 'center' };

        // Add data rows
        classData.forEach(student => {
            let row = {
                enrollment_number: student.enrollment_number,
                faculty_number: student.faculty_number,
                name: student.name
            };

            student.weeks_data.forEach(week => {
                row[`week_${week.week}_solved`] = `${week.problems_solved}/${week.total_problems}`;
                row[`week_${week.week}_commit_date`] = week.last_commit_time !== 'No Commits'
                    ? formatDate(week.last_commit_time.split('T')[0])
                    : 'No Commits';
                row[`week_${week.week}_status`] = week.commit_status;
            });

            const dataRow = worksheet.addRow(row);
            dataRow.alignment = { horizontal: 'center' };
        });

        // Merge week header cells
        let startColumn = 4;
        classData[0].weeks_data.forEach(() => {
            worksheet.mergeCells(1, startColumn, 1, startColumn + 2);
            startColumn += 3;
        });

        // Write to file
        workbook.xlsx.writeBuffer().then(buffer => {
            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${course}Sem${semester}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }

    function formatDate(dateString) {
        var parts = dateString.split('-');
        return parts[2] + '-' + parts[1] + '-' + parts[0];
    }
});