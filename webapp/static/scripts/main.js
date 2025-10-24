// Form submission with loading state
document.getElementById('predictionForm').addEventListener('submit', function(e) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');

    // Show loading state
    submitBtn.disabled = true;
    btnText.textContent = 'Predicting...';
    btnLoading.style.display = 'inline-block';

    // Form will submit normally, loading state will persist until page reloads
});

// Form validation
function validateForm() {
    const age = document.getElementById('age').value;
    const bmi = document.getElementById('bmi').value;
    const sex = document.getElementById('sex').value;
    const smoker = document.getElementById('smoker').value;
    const region = document.getElementById('region').value;

    if (!age || !bmi || !sex || !smoker || !region) {
        alert('Please fill in all required fields.');
        return false;
    }

    if (age < 18 || age > 64) {
        alert('Age must be between 18 and 64.');
        return false;
    }

    if (bmi < 10 || bmi > 50) {
        alert('BMI must be between 10 and 50.');
        return false;
    }

    return true;
}

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add animation to response sections when they appear
function animateResponses() {
    const responses = document.querySelectorAll('.response-me, .response-ai');
    responses.forEach((response, index) => {
        if (response.innerHTML.trim()) {
            response.style.animationDelay = `${index * 0.2}s`;
        }
    });
}

// Run animations on page load
document.addEventListener('DOMContentLoaded', function() {
    animateResponses();
});

// Enhanced form interactions
document.querySelectorAll('input, select').forEach(element => {
    element.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
    });

    element.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
    });
});
