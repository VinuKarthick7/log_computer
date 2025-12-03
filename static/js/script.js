/**
 * Lab Registration System - Client-side JavaScript
 * Professional Edition - Static Version
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    
    // Input fields
    const registerNoInput = document.getElementById('register_no');
    const nameInput = document.getElementById('name');
    const departmentSelect = document.getElementById('department');
    const systemNoInput = document.getElementById('system_no');
    const inTimeInput = document.getElementById('in_time');
    const inDateInput = document.getElementById('in_date');
    
    // Display elements
    const displayTime = document.getElementById('displayTime');
    const displayDate = document.getElementById('displayDate');
    
    // State
    let sessionId = null;
    let isSubmitting = false;
    
    // Initialize
    init();
    
    function init() {
        // Update time every second
        updateTime();
        setInterval(updateTime, 1000);
        
        // Add input event listeners
        registerNoInput.addEventListener('input', handleRegisterNoInput);
        registerNoInput.addEventListener('blur', () => validateField(registerNoInput));
        
        nameInput.addEventListener('input', () => validateField(nameInput));
        nameInput.addEventListener('blur', () => validateField(nameInput));
        
        departmentSelect.addEventListener('change', () => validateField(departmentSelect));
        
        // Form submission
        form.addEventListener('submit', handleSubmit);
        
        // Prevent accidental page close
        window.addEventListener('beforeunload', handleBeforeUnload);
        
        // Disable right-click
        document.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Disable F12 and developer tools shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F12' || 
                (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) ||
                (e.ctrlKey && (e.key === 'U' || e.key === 'u'))) {
                e.preventDefault();
            }
        });
    }
    
    function updateTime() {
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0]; // HH:MM:SS
        const dateString = now.toISOString().split('T')[0]; // YYYY-MM-DD
        
        inTimeInput.value = timeString;
        inDateInput.value = dateString;
        
        if (displayTime) displayTime.textContent = timeString;
        if (displayDate) displayDate.textContent = dateString;
    }
    
    function handleRegisterNoInput(e) {
        // Convert to uppercase and allow only alphanumeric
        let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        e.target.value = value;
        validateField(e.target);
    }
    
    function validateField(field) {
        const value = field.value.trim();
        let isValid = false;
        
        switch(field.id) {
            case 'register_no':
                isValid = /^[A-Z0-9]{12}$/.test(value);
                break;
            case 'name':
                isValid = value.length >= 2;
                break;
            case 'department':
                isValid = value !== '';
                break;
            default:
                isValid = value !== '';
        }
        
        // Update UI
        if (value === '') {
            field.classList.remove('valid', 'invalid');
        } else {
            field.classList.toggle('valid', isValid);
            field.classList.toggle('invalid', !isValid);
        }
        
        return isValid;
    }
    
    function validateForm() {
        const registerValid = validateField(registerNoInput);
        const nameValid = validateField(nameInput);
        const departmentValid = validateField(departmentSelect);
        
        return registerValid && nameValid && departmentValid;
    }
    
    async function handleSubmit(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            showError('Please fill all required fields correctly.');
            return;
        }
        
        if (isSubmitting) return;
        
        isSubmitting = true;
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        hideAlerts();
        
        // Gather form data
        const formData = {
            register_no: registerNoInput.value.trim().toUpperCase(),
            name: nameInput.value.trim(),
            department: departmentSelect.value,
            system_no: systemNoInput.value,
            in_time: inTimeInput.value,
            in_date: inDateInput.value
        };
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                sessionId = data.session_id;
                showSuccess(`Welcome, ${data.name}! You are now signed in.`);
                
                // Store session ID in sessionStorage
                sessionStorage.setItem('lab_session_id', sessionId);
                
                // Close window after 3 seconds
                setTimeout(() => {
                    window.close();
                    // If window doesn't close, show message
                    showSuccess('You are signed in! You may now close this window.');
                }, 3000);
            } else {
                showError(data.error || 'Registration failed. Please try again.');
                isSubmitting = false;
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please check your connection and try again.');
            isSubmitting = false;
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'flex';
        successAlert.style.display = 'none';
    }
    
    function showSuccess(message) {
        successMessage.textContent = message;
        successAlert.style.display = 'flex';
        errorAlert.style.display = 'none';
    }
    
    function hideAlerts() {
        errorAlert.style.display = 'none';
        successAlert.style.display = 'none';
    }
    
    function handleBeforeUnload(e) {
        if (!sessionId && (registerNoInput.value || nameInput.value)) {
            e.preventDefault();
            e.returnValue = 'You have not completed registration. Are you sure you want to leave?';
            return e.returnValue;
        }
    }
});
