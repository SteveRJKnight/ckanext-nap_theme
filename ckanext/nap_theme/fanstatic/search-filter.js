
var searchFilterElements = document.getElementsByClassName("filter-input")

for (searchFilterElement of searchFilterElements) {
    searchFilterElement.addEventListener("keyup", function(event) {
        var searchInputValue = event.target.value.toUpperCase();
        var parentDiv = event.target.parentElement.parentElement;
        var checkboxElements = parentDiv.getElementsByClassName("govuk-checkboxes__item");
    
        for (checkBox of checkboxElements) {
            var checkBoxText = checkBox.textContent || checkBox.innerText;
        
            if (checkBoxText.toUpperCase().indexOf(searchInputValue) > -1) {
                checkBox.style.display = "";
            } else {
                checkBox.style.display = "none";
            }
        }
        
    });
}

var filterFacetTags = document.getElementsByClassName("facet-tag__remove")

for (filterFacet of filterFacetTags) {
    filterFacet.addEventListener("click", function(event) {
        var elementId = event.target.dataset.value;
        var filterElement = document.getElementById(elementId);
        if (filterElement.type === 'checkbox') {
            filterElement.checked = !filterElement.checked;
        } 
        else if (filterElement.type === 'text') {
            filterElement.value = "";
        }
        filterElement.form.submit();
    });
}
