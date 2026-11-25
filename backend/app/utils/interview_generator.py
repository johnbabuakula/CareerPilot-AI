
INTERVIEW_QUESTIONS = {
    "Python": [
        "What are the main features of Python?",
        "Explain the difference between a list and a tuple.",
        "What is object-oriented programming?",
        "Explain Python decorators.",
        "What are generators in Python?",
        "What is the difference between == and is?",
        "Explain the use of lambda functions.",
        "What are Python dictionaries?",
        "What is exception handling in Python?",
        "Explain the difference between shallow copy and deep copy."
    ],

    "SQL": [
        "What is the difference between WHERE and HAVING?",
        "Explain primary keys and foreign keys.",
        "What is a JOIN in SQL?",
        "What is database normalization?",
        "How do you find the second highest salary?",
        "What is the difference between DELETE and TRUNCATE?",
        "Explain GROUP BY in SQL.",
        "What is the difference between UNION and UNION ALL?",
        "What is a subquery?",
        "What are SQL indexes?"
    ],

    "DSA": [
        "What is the time complexity of binary search?",
        "Explain arrays and linked lists.",
        "What is a stack?",
        "Explain the two-pointer technique.",
        "What is the difference between a stack and a queue?",
        "What is a hash table?",
        "Explain bubble sort.",
        "What is recursion?",
        "What is the difference between linear search and binary search?",
        "What is Big O notation?"
    ],

    "HR": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Why should we hire you?",
        "Where do you see yourself in five years?",
        "Why do you want this job?",
        "Why do you want to join our company?",
        "How do you handle pressure?",
        "Tell me about a challenging situation you faced.",
        "Are you comfortable working in a team?",
        "What are your career goals?"
    ]
}


def generate_questions(topic: str, count: int = 5):
    questions = INTERVIEW_QUESTIONS.get(topic)

    if not questions:
        return []

    return questions[:count]
