
function submitRecipe() {
    // Preserve your styling and visibility changes
    document.getElementById('section3').style.backgroundImage = '';
    document.getElementById('section3').style.background = '#487b7f';
    document.getElementById('tick1').classList.remove('hidden');

    var field = document.getElementById('recipe');
    var button = document.getElementById('submit-recipe');

    if (field) {
        field.style.display = 'none';
    }
    if (button) {
        button.style.display = 'none';
    }

    // Submit the form using AJAX
    $.ajax({
        type: 'POST',
        url: '/submit',
        data: $('#recipe-form').serialize(),
        success: function() {
            // Redirect to loading page
            window.location.href = '/loading';
        }
    });
}




function submitZip() {

    var field = document.getElementById('zip')
    var button = document.getElementById('zip-submit')
    var zipCode = field.value;

    if (!isValidUSZip(zipCode)) {
        // Display an error message
        alert("Invalid ZIP!! Please enter a valid US ZIP code.");

        // Prevent the form submission
        return false;
    }

    document.getElementById('section2').style.backgroundImage = '';
    document.getElementById('section2').style.background = '#364851';
    document.getElementById('tick2').classList.remove('hidden');
    document.getElementById('section3').classList.add('visible');

    

    if (field) {
        field.style.display = 'none';
    }
    if (button) {
        button.style.display = 'none';
    }


    // If the zip code is valid, allow the form submission
    return true;


}

function isValidUSZip(sZip) {
    return /^\d{5}(-\d{4})?$/.test(sZip);
}


window.onload = function() {
    var typed = new Typed('#animated-paragraph', {
        strings: ['How to use the application?', 'Step 1: Zip code.', 'Step 2: Your favorite recipe.', 'Step 3: Get ingredients and best prices!'],
        typeSpeed: 50,
        onComplete: function() {
            document.getElementById('section2').classList.add('visible');
        }
    });
};
