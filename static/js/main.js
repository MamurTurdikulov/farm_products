document.addEventListener("submit", function(e) {
    const numberInput = e.target.querySelector("input[type=number]");
    if (numberInput) {
        if (parseInt(numberInput.value) <= 0) {
            e.preventDefault();
            alert("Amount must be at least 1 kg.");
        }
    }
});
