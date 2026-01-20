document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('init-sequence-btn');
    const indicator = document.getElementById('system-indicator');
    const logWindow = document.getElementById('data-log-window');

    startBtn.addEventListener('click', () => {
        // Toggle system status via class replacement
        if (indicator.classList.contains('label-inactive')) {
            indicator.classList.remove('label-inactive');
            indicator.classList.add('label-active');
            indicator.textContent = 'Operational';
            
            // Show the log window
            logWindow.classList.remove('hidden-element');
            startBtn.textContent = 'Shutdown';
        } else {
            indicator.classList.add('label-inactive');
            indicator.classList.remove('label-active');
            indicator.textContent = 'Standby';
            
            logWindow.classList.add('hidden-element');
            startBtn.textContent = 'Initialize System';
        }
    });
});