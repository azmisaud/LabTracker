$(document).ready(function() {
    $('#course').change(function() {
        course=$(this).val();
        $.ajax({
            url: '/teachers/get-semesters/',
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
            url: '/teachers/get-week/',
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
})