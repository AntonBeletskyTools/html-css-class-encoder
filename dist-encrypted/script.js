document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('x074f37');
    const indicator = document.getElementById('x714ada');
    const logWindow = document.getElementById('xfb47c4');

    startBtn.addEventListener('click', () => {
        // Toggle system status via class replacement
        if (indicator.classList.contains('x611201')) {
            indicator.classList.remove('x611201');
            indicator.classList.add('label-active');
            indicator.textContent = 'Operational';
            
            // Show the log window
            logWindow.classList.remove('x3ded60');
            startBtn.textContent = 'Shutdown';
        } else {
            indicator.classList.add('x611201');
            indicator.classList.remove('label-active');
            indicator.textContent = 'Standby';
            
            logWindow.classList.add('x3ded60');
            startBtn.textContent = 'Initialize System';
        }
    });
});