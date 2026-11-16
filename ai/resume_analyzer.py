import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_resume_with_ai(
    resume_text,
    role,
    rag_context
):

    prompt = f"""
You are an expert recruitment and career analysis assistant.

Your task is to compare a student's resume against the requirements
for a specific target job role.

TARGET ROLE:
{role}

ROLE REQUIREMENTS FROM RAG:
{rag_context}

STUDENT RESUME:
{resume_text}

Analyze the candidate carefully.

Separate requirements into:

1. Education
2. Technical Skills
3. Projects
4. Certifications
5. Experience
6. Resume / ATS Keywords

For every category determine:

- What the candidate already has
- What is missing
- What is weak or insufficient
- How closely the candidate matches the role

IMPORTANT RULES:

1. Do not invent information that is not present in the resume.
2. Do not assume the candidate has a skill just because it is related
   to another skill.
3. For entry-level candidates, lack of professional experience should
   not automatically result in a very low score.
4. Relevant projects can partially compensate for lack of professional
   experience.
5. Certifications are beneficial unless the role requirements explicitly
   make them mandatory.
6. Distinguish between required qualifications and desirable
   qualifications.
7. Evaluate the resume specifically for the selected role.
8. The overall score must reflect the actual match between the resume
   and the role requirements.

Calculate scores from 0 to 100.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_score": 0,

    "eligibility": {{
        "status": "Eligible",
        "reason": ""
    }},

    "category_scores": {{
        "technical_skills": 0,
        "projects": 0,
        "education": 0,
        "certifications": 0,
        "experience": 0,
        "keywords": 0
    }},

    "education": {{
        "matched": [],
        "missing": [],
        "weak": []
    }},

    "skills": {{
        "matched": [],
        "missing": [],
        "weak": []
    }},

    "projects": {{
        "matched": [],
        "missing": [],
        "weak": []
    }},

    "certifications": {{
        "matched": [],
        "missing": [],
        "weak": []
    }},

    "experience": {{
        "matched": [],
        "missing": [],
        "weak": []
    }},

    "keywords": {{
        "matched": [],
        "missing": []
    }},

    "strengths": [],

    "weak_areas": [],

    "recommendations": []
}}
"""

    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    return json.loads(result)