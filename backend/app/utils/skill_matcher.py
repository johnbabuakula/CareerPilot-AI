
import re

SKILLS = [
    "Python", "Java", "C++", "SQL", "MySQL",
    "HTML", "CSS", "JavaScript", "React",
    "FastAPI", "Django", "Flask",
    "Machine Learning", "Deep Learning", "Data Science",
    "Pandas", "NumPy", "TensorFlow", "PyTorch",
    "Scikit-learn", "Statistics", "Data Structures",
    "Algorithms", "Git", "GitHub", "REST API",
    "Object-Oriented Programming", "Problem Solving"
]


def find_skills(text: str) -> list:
    found_skills = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def calculate_skill_match(resume_text: str, job_description: str) -> dict:

    resume_skills = find_skills(resume_text)
    required_skills = find_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    if required_skills:
        match_percentage = round(
            len(matched_skills) / len(required_skills) * 100,
            2
        )
    else:
        match_percentage = 0

    suggestions = [
        f"Consider adding relevant evidence of {skill} to your resume, if you have this skill."
        for skill in missing_skills
    ]

    if not missing_skills:
        suggestions.append(
            "Your resume contains all the skills detected in this job description. "
            "Consider improving your project descriptions and achievements."
        )

    return {
        "match_percentage": match_percentage,
        "total_required_skills": len(required_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions
    }
