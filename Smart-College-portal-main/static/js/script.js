// Smart College Portal - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Smart College Portal loaded');

    const adminChartCanvas = document.getElementById('adminChart');
    if (adminChartCanvas && typeof Chart !== 'undefined') {
        const studentCount = Number(adminChartCanvas.dataset.students) || 0;
        const facultyCount = Number(adminChartCanvas.dataset.faculty) || 0;
        const assignmentCount = Number(adminChartCanvas.dataset.assignments) || 0;
        const noticeCount = Number(adminChartCanvas.dataset.notices) || 0;

        const ctx = adminChartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Students', 'Faculty', 'Assignments', 'Notices'],
                datasets: [{
                    label: 'Records',
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#0dcaf0'],
                    data: [studentCount, facultyCount, assignmentCount, noticeCount]
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
});