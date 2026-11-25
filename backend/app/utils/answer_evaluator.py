
def evaluate_answer(answer: str, question: str) -> dict:
    answer = answer.strip()

    if not answer:
        return {
            "score": 0,
            "feedback": "Please provide an answer."
        }

    words = answer.split()
    word_count = len(words)

    if word_count < 5:
        score = 2
        feedback = "Your answer is too short. Explain the concept in more detail."

    elif word_count < 15:
        score = 5
        feedback = "Good start, but add more explanation and a practical example."

    elif word_count < 40:
        score = 7
        feedback = "Good answer. Try including technical details or examples."

    else:
        score = 9
        feedback = "Detailed answer. Make sure the explanation is accurate and relevant."

    return {
        "score": score,
        "feedback": feedback
    }
