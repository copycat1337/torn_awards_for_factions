// ================== SIDEBAR TOGGLE ==================
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebar-toggle');
    const overlay = document.getElementById('sidebar-overlay');

    if (!sidebar || !toggle) return;

    // Restore saved state on desktop
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved === 'true' && window.innerWidth > 900) {
        sidebar.classList.add('collapsed');
    }

    toggle.addEventListener('click', () => {
        if (window.innerWidth <= 900) {
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('show');
        } else {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
        }
    });

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('show');
        });
    }

    // Sidebar nav links that switch tabs (instead of navigating)
    document.querySelectorAll('[data-nav-tab]').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const tabName = link.dataset.navTab;
            switchAdminTab(tabName);

            // Highlight active sidebar link
            document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Close mobile sidebar
            if (window.innerWidth <= 900) {
                sidebar.classList.remove('mobile-open');
                overlay.classList.remove('show');
            }
        });
    });
});

// Tab switching helper (used by sidebar)
function switchAdminTab(tabName) {
    const btn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    if (btn) btn.click();
}