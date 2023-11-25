
function submitRecipe() {
    document.getElementById('section3').style.backgroundImage = '';
    document.getElementById('section3').style.background = '#487b7f';
    document.getElementById('tick1').classList.remove('hidden');

    var field = document.getElementById('recipe')
    var button = document.getElementById('submit-recipe')

    if (field) {
        field.style.display = 'none';
    }
    if (button) {
        button.style.display = 'none';
    }
}

function submitZip() {
    document.getElementById('section2').style.backgroundImage = '';
    document.getElementById('section2').style.background = '#364851';
    document.getElementById('tick2').classList.remove('hidden');
    document.getElementById('section3').classList.add('visible');

    var field = document.getElementById('zip')
    var button = document.getElementById('zip-submit')

    if (field) {
        field.style.display = 'none';
    }
    if (button) {
        button.style.display = 'none';
    }


}

// function updateText() {
//     var text = document.getElementById('ingredients');
//     text.innerText = "Your new dynamic text here";
// }

window.onload = function() {
    var typed = new Typed('#animated-paragraph', {
        strings: ['How to use the application?', 'Step 1: Enter a zip code.', 'Step 2: Enter the name of the recipe.', 'Step 3: The crawler fetches the ingredients for the recipe. Next, it crawls the web to fetch you the best price for the ingredients from stores near you.'],
        typeSpeed: 50,
        onComplete: function() {
            document.getElementById('section2').classList.add('visible');
        }
    });
};
