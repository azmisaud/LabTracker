$(document).ready(function() {
    $('#update-data-btn').on('click', function() {
        $('#update-data-form').toggle();
        $('#update-data-btn').hide();
        $('#start-new-semester-btn').hide();
    });

    $('#course').change(function() {
        course=$(this).val();
        $.ajax({
            url: '/faculty/get-semesters/',
            data: { course: course },
            success: function(data){
                $('#semester').empty();
                $('#semester').append('<option value="">Select Semester</option>');
                data.forEach(function(semester) {
                    $('#semester').append('<option value="'+ semester + '">' + semester + '</option>');
                });
            }
        });
    });

    $('#update-data-form').on('submit', function(event) {
        event.preventDefault();
        const course=$('#course').val();
        const semester=$('#semester').val();

        $.ajax({
            url : '/faculty/trigger-update/',
            type: 'POST',
            data: {
                course: course,
                semester: semester,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function(data) {
                if(data.success) {
                    alert('Data Updated Successfully');
                    $('#update-data-form').hide();
                } else if (data.error) {
                    alert(data.error);
                }
            },
            error: function() {
                alert('Error updating data. Please try again.');
            },
            complete : function () {
                submitButton.removeClass('loading');
                submitButton.find('.loading-icon').hide();
            }
        });

        $('#update-data-btn').show();
        $('#start-new-semester-btn').show();
        $('#update-data-form').hide();
    });

    $('#start-new-semester-btn').click(function() {
        if (confirm('Are you sure you want to start a new semester? This will delete students who have been on the platform for more than or equal to 150 days.')) {
            $.ajax({
                url: '/faculty/start-new/',
                type: 'GET',
                success: function (response) {
                    if(response.success){
                        alert(response.success);
                    } else if(response.error) {
                        alert(response.error);
                    }
                },
                error: function () {
                    alert('Error starting a new semester, please try again.')
                }
            });
        }
    });

    function renderChart(ctx, data, labels) {
        function fixDpi(canvas) {
            const dpi = window.devicePixelRatio;
            const style_height = +getComputedStyle(canvas).getPropertyValue('height').slice(0, -2);
            const style_width = +getComputedStyle(canvas).getPropertyValue('width').slice(0, -2);
            canvas.setAttribute('height', style_height * dpi);
            canvas.setAttribute('width', style_width * dpi);
        }

        fixDpi(ctx.canvas);

        new Chart(ctx, {
            type: 'pie',  // Pie chart type
            data: {
                labels: labels,  // Labels for each slice
                datasets: [{
                    label: data.label,
                    data: data.values,  // Data values for the pie chart
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',  // Light red
                        'rgba(54, 162, 235, 0.6)',  // Light blue
                        'rgba(255, 206, 86, 0.6)',   // Light yellow
                        'rgba(75, 192, 192, 0.6)',   // Light teal
                        'rgba(153, 102, 255, 0.6)',  // Light purple
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',    // Dark red
                        'rgba(54, 162, 235, 1)',    // Dark blue
                        'rgba(255, 206, 86, 1)',     // Dark yellow
                        'rgba(75, 192, 192, 1)',     // Dark teal
                        'rgba(153, 102, 255, 1)',    // Dark purple
                    ],
                    borderWidth: 1,
                    hoverBackgroundColor: [
                        'rgba(255, 99, 132, 0.8)',  // Darker light red
                        'rgba(54, 162, 235, 0.8)',  // Darker light blue
                        'rgba(255, 206, 86, 0.8)',   // Darker light yellow
                        'rgba(75, 192, 192, 0.8)',   // Darker light teal
                        'rgba(153, 102, 255, 0.8)',  // Darker light purple
                    ],
                    hoverBorderColor: [
                        'rgba(255, 99, 132, 1)',    // Dark red
                        'rgba(54, 162, 235, 1)',    // Dark blue
                        'rgba(255, 206, 86, 1)',     // Dark yellow
                        'rgba(75, 192, 192, 1)',     // Dark teal
                        'rgba(153, 102, 255, 1)',    // Dark purple
                    ],
                    hoverBorderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainsAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutBounce'
                },
                plugins: {
                    legend: {
                        display: true,
                    },
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw}`;
                            }
                        }
                    },
                    onHover: (event, chartElement) => {
                        event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
                    }
                }
            }
        });
    }

        function fetchGraphData(week) {
            $.ajax({
                url: '/faculty/fetch-graph-data/',
                data: { week: week },
                success: function(data) {
                    $('#graphs').empty();

                    data.forEach(function(item) {
                        $('#graphs').append(`
                            <div class="graph">
                                <h4> Course: ${item.course} - Semester: ${item.semester}</h4>
                                <canvas id="graph-${item.course}-${item.semester}"></canvas>
                            </div>
                        `);

                        const ctx = document.getElementById(`graph-${item.course}-${item.semester}`).getContext('2d');
                        renderChart(ctx, {
                            label: `Course: ${item.course}, Semester: ${item.semester}`,
                            values: [item.late_solved, item.late_unsolved, item.on_time_solved, item.on_time_unsolved, item.not_committed]
                        }, ['Late Solved', 'Late Unsolved', 'On Time Solved', 'On Time Unsolved', 'Not Committed']);
                    });
                },
                error: function() {
                    alert('Error fetching data, please try again.')
                }
            });
        }

        $('#week-select').val('1');
        fetchGraphData('1');

        $('#week-select').change(function() {
            const selectedWeek = $(this).val();
            fetchGraphData(selectedWeek);
        });

});