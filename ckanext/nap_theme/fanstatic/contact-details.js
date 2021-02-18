const availabilityRadioElements = document.getElementsByName("data_available")
const contactDetailSpans = document.getElementById("contact-details-section").getElementsByTagName("span")

function setVisibility(elements, visibility) {
    for (element of elements) {
        element.style.visibility = visibility;
    }
}

for (availabilityRadioElement of availabilityRadioElements) {
    availabilityRadioElement.addEventListener('change', function() {
        if (this.value === "yes") {
            setVisibility(contactDetailSpans, "visible");
        } else {
            setVisibility(contactDetailSpans, "hidden");
        }
    });
}