import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_interview_questions(
    role,
    rag_context,
    num_questions=8
):

    prompt = f"""
You are an experienced technical interviewer and campus placement coach.

Generate a realistic set of interview questions for a candidate applying
for the role of {role}.

ROLE CONTEXT (from the placement knowledge base):
{rag_context}

Create exactly {num_questions} questions, spanning a mix of:
1. Technical / role-specific questions
2. Behavioral / HR-style questions
3. At least one resume/project-discussion style question

For every question, provide:
- "category": one of "Technical", "Behavioral", "Project & Resume"
- "question": the interview question itself
- "tip": a short (1-2 sentence) tip on how to structure a strong answer.
  Give guidance on approach, not the full answer itself.

IMPORTANT RULES:
1. Keep questions realistic for a campus placement interview for this
   specific role - do not invent unrelated topics.
2. Vary the difficulty across the set (some easier warm-up questions,
   some that probe depth).
3. Do not repeat the same question twice.

Return ONLY valid JSON. Use exactly this structure:

{{
    "role": "{role}",
    "questions": [
        {{
            "category": "Technical",
            "question": "",
            "tip": ""
        }}
    ]
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

        temperature=0.4,

        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    return json.loads(result)


def evaluate_interview(
    role,
    qa_pairs
):
    """
    qa_pairs: list of {"category": str, "question": str, "answer": str}
    (answer may be an empty string if the candidate skipped it)
    """

    transcript_lines = []

    for i, qa in enumerate(qa_pairs, start=1):

        answer_text = qa.get("answer", "").strip()

        if not answer_text:
            answer_text = "(No answer given - the candidate skipped this question.)"

        transcript_lines.append(
            f"Q{i} ({qa.get('category', 'General')}): {qa.get('question', '')}\n"
            f"Candidate's answer: {answer_text}"
        )

    transcript = "\n\n".join(transcript_lines)

    prompt = f"""
You are an experienced interview coach and placement panel member,
reviewing a completed mock interview transcript for a candidate
applying for the role of {role}.

INTERVIEW TRANSCRIPT:
{transcript}

Evaluate the candidate's answers as a whole. For each answer, judge:
- Relevance to the question
- Clarity and structure of the response
- Technical/role accuracy where applicable
- Depth (not just a one-line answer)

An unanswered or skipped question should score very low for that
question and should reduce the overall score.

Return ONLY valid JSON, using exactly this structure:

{{
    "overall_score": 0,
    "summary": "2-3 sentence overall assessment of interview performance.",
    "strengths": ["short strength 1", "short strength 2"],
    "areas_to_improve": ["short improvement area 1", "short improvement area 2"],
    "per_question": [
        {{
            "question": "the question text",
            "score": 0,
            "feedback": "1-2 sentence feedback on this specific answer."
        }}
    ]
}}

"overall_score" must be an integer from 0 to 100.
"score" inside "per_question" must be an integer from 0 to 10.
Include one "per_question" entry for every question in the transcript,
in the same order.
"""

    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3,

        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    return json.loads(result)
