function submitRecipe() {
    var recipe = document.getElementById('recipe').value;
    // Do something with the recipe
    document.getElementById('section1').style.backgroundImage = '';
    document.getElementById('section1').style.background = '#487b7f';
    document.getElementById('tick1').classList.remove('hidden');
}

function submitZip() {
    var zip = document.getElementById('zip').value;
    // Do something with the zip code
    document.getElementById('section2').style.background = 'darkgreen';
    document.getElementById('tick2').classList.remove('hidden');
}

function updateText() {
    var text = document.getElementById('ingredients');
    text.innerText = "Your new dynamic text here";
}