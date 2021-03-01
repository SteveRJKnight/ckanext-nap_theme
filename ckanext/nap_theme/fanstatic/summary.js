window.addEventListener("DOMContentLoaded", function () {
  const maxHeight = 250;
  const summaryTextElement = document.getElementById("summary-text");
  if (summaryTextElement) {
    const summaryToggleElement = document.getElementById("summary-toggle");
    // Only show Show full summary button is content is too tall!
    if (summaryTextElement.clientHeight > maxHeight) {
      summaryToggleElement.style.display = "inline";
      summaryTextElement.style.overflow = "hidden";
      summaryTextElement.style.marginBottom = "0";
      summaryTextElement.style.maxHeight = maxHeight + "px";
      summaryToggleElement.addEventListener("click", function () {
        if (this.dataset.folded == "folded") {
          summaryTextElement.style.maxHeight = "none";
          this.setAttribute("data-folded", "expanded");
          this.innerHTML = "Hide full summary";
        } else {
          summaryTextElement.style.maxHeight = maxHeight + "px"
          this.setAttribute("data-folded", "folded");
          this.innerHTML = "Show full summary";
        }
      })
    } else {
      summaryToggleElement.style.display = "none";
    }
  }
})
