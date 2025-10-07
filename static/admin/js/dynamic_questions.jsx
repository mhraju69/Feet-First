document.addEventListener("DOMContentLoaded", function() {
    const subcatSelect = document.getElementById("id_subcategory");

    function updateQuestionOptions(inlineRow) {
        const questionSelect = inlineRow.querySelector("select[id$='-question']");
        const answersDiv = inlineRow.querySelector(".field-answers");

        const subcatQuestions = JSON.parse(questionSelect.dataset.subcatQuestions);
        const questionAnswers = JSON.parse(questionSelect.dataset.questionAnswers);

        function renderAnswers(q) {
            const choices = questionAnswers[q] || [];
            answersDiv.innerHTML = "";
            choices.forEach(([val, label]) => {
                const li = document.createElement("li");
                li.innerHTML = `<label><input type="checkbox" value="${val}" name="${answersDiv.dataset.name}"> ${label}</label>`;
                answersDiv.appendChild(li);
            });
        }

        // Update questions dropdown based on selected subcategory
        const selectedSubcat = subcatSelect.value;
        questionSelect.innerHTML = "";
        if (subcatQuestions[selectedSubcat]) {
            subcatQuestions[selectedSubcat].forEach(([val, label]) => {
                const opt = document.createElement("option");
                opt.value = val;
                opt.text = label;
                questionSelect.appendChild(opt);
            });
        }

        // Initial render answers if a question is already selected
        if (questionSelect.value) {
            renderAnswers(questionSelect.value);
        }

        questionSelect.addEventListener("change", function() {
            renderAnswers(this.value);
        });
    }

    // Apply to all existing inlines
    document.querySelectorAll(".dynamic-inline").forEach(updateQuestionOptions);

    // Update all inlines when SubCategory changes
    subcatSelect.addEventListener("change", function() {
        document.querySelectorAll(".dynamic-inline").forEach(updateQuestionOptions);
    });
});
