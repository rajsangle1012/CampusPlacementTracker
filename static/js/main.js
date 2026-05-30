/* main.js – CampusPlacementTracker */

// Auto-dismiss flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity .5s';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 500);
        }, 4000);
    });

    // Confirm before deleting
    document.querySelectorAll('.btn-danger').forEach(function (btn) {
        // Only attach if it is a link (not a submit button inside confirm page)
        if (btn.tagName === 'A') {
            btn.addEventListener('click', function (e) {
                if (!confirm('Are you sure you want to delete this?')) {
                    e.preventDefault();
                }
            });
        }
    });
});
