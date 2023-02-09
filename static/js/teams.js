document.addEventListener("DOMContentLoaded", function () {
    var source = new EventSource('/question');
    var answerForm = document.getElementById("answerForm")
    var questionSpan = document.getElementById("question")
    var answerInput = document.getElementById("answer")
    var question = ""

    source.addEventListener("question",
        function (event) {

            question = event.data
            questionSpan.innerHTML = question
            if (question === "") {
                answerInput.disabled = true
                answerForm.classList.add("needs-validation")
                answerForm.classList.remove("was-validated")
            }
            else {
                answerInput.disabled = false
                answerInput.focus()
            }
            answerInput.value = ""
        }

    )

    answerForm.addEventListener("submit", (e) => {
        e.preventDefault()
        answer = answerForm["answer"].value

        if (answer != eval(question)) {
            answerForm["answer"].value = ""

            function removeValidation(e) {
                console.log("change")
                answerForm.classList.add("needs-validation")
                answerForm.classList.remove("was-validated")
                answerInput.removeEventListener("keypress", removeValidation)
            }
            answerInput.addEventListener("keypress", removeValidation)

        }
        else {
            fetch('/answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "teamId": answerForm["teamId"].value,
                    "answer": answerForm["answer"].value
                })
            })
        }
    })
})
