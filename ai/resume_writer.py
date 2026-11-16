import os
import re

from groq import Groq
from dotenv import load_dotenv

from rag.retriever import retrieve_context


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# SECTION CHARACTER LIMITS
# ============================================================

SECTION_LIMITS = {

    "objective": 450,

    "project": 950,

    "experience": 600,

    "skills": 550,

    "certification": 250
}


# ============================================================
# RAG CONTEXT
# ============================================================

def get_rag_context(query, role):

    documents, metadatas = retrieve_context(
        query=query,
        role=role,
        n_results=3
    )

    if not documents:
        return ""

    return "\n\n".join(
        documents
    )


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_resume_text(text):

    if not text:
        return ""

    text = text.replace(
        "```",
        ""
    )

    # Remove bold markdown
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    # Remove italic markdown
    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )

    # Remove backticks
    text = text.replace(
        "`",
        ""
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT IMPORTANT METRICS
# ============================================================

def extract_metrics(text):

    if not text:
        return []

    patterns = [

        # MAE
        r"(?:MAE|Mean Absolute Error)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?\s*(?:cycles?|%)?",

        # RMSE
        r"(?:RMSE|Root Mean Squared Error)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?\s*(?:cycles?|%)?",

        # Accuracy
        r"(?:accuracy|Accuracy)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?\s*%?",

        # Precision
        r"(?:precision|Precision)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?",

        # Recall
        r"(?:recall|Recall)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?",

        # F1
        r"(?:F1|F1-score|F1 score)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?",

        # ROC-AUC
        r"(?:ROC-AUC|ROC AUC)\s*[=:]?\s*"
        r"\d+(?:\.\d+)?",

        # Dataset IDs
        r"FD00[1-4]"
    ]


    found = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            if isinstance(
                match,
                tuple
            ):
                match = match[0]

            if match not in found:

                found.append(
                    match
                )


    return found


# ============================================================
# COMPRESS WITHOUT DESTROYING IMPORTANT INFORMATION
# ============================================================

def enforce_character_limit(
    text,
    limit
):

    if not text:
        return ""

    text = clean_resume_text(
        text
    )

    if len(text) <= limit:
        return text


    # Split into lines/bullets
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


    selected = []

    current_length = 0


    for line in lines:

        line_length = len(line)


        if current_length + line_length + 1 <= limit:

            selected.append(
                line
            )

            current_length += (
                line_length + 1
            )

        else:

            break


    result = "\n".join(
        selected
    )


    # If no complete line fits,
    # make a safe character cut.
    if not result:

        result = text[:limit]


        # Don't cut in the middle of a word
        last_space = result.rfind(" ")

        if last_space > 0:

            result = result[
                :last_space
            ]


    return result.strip()


# ============================================================
# MAIN AI RESUME ENHANCER
# ============================================================

def enhance_resume_content(
    user_input,
    role,
    section
):

    if not user_input or not user_input.strip():

        return ""


    user_input = user_input.strip()


    # ========================================================
    # SECTION LIMIT
    # ========================================================

    max_chars = SECTION_LIMITS.get(
        section,
        700
    )


    # ========================================================
    # EXTRACT METRICS BEFORE AI
    # ========================================================

    important_metrics = extract_metrics(
        user_input
    )


    metrics_text = "\n".join(
        important_metrics
    )


    # ========================================================
    # RAG QUERY
    # ========================================================

    query = f"""
    Professional resume writing guidelines for the
    {section} section.

    Target role:
    {role}

    User content:
    {user_input}

    Retrieve guidelines about:

    - ATS-friendly writing
    - technical resume writing
    - concise bullet points
    - action verbs
    - measurable achievements
    - preserving technical metrics
    - presenting machine learning results
    - presenting datasets and evaluation results
    """


    rag_context = get_rag_context(
        query,
        role
    )


    # ========================================================
    # PROJECT INSTRUCTION
    # ========================================================

    if section == "project":

        instruction = f"""
        Rewrite the project for a one-page technical resume.

        Maximum final length:
        {max_chars} characters.

        IMPORTANT:

        The goal is NOT to blindly shorten the project.

        The goal is to intelligently compress it while
        preserving the most technically valuable information.

        PRIORITY ORDER:

        1. Important performance metrics
        2. Dataset names
        3. Algorithms/models
        4. Important technologies
        5. Important implementation details
        6. Deployment/application details
        7. General descriptive wording

        Preserve:

        - Technologies
        - Frameworks
        - Libraries
        - Datasets
        - Algorithms
        - Models
        - Important preprocessing
        - Deployment
        - Performance metrics
        - Accuracy
        - Precision
        - Recall
        - F1-score
        - ROC-AUC
        - MAE
        - RMSE
        - Record counts
        - Feature counts

        DO NOT INVENT ANY INFORMATION.

        DO NOT CHANGE NUMERICAL VALUES.

        DO NOT REMOVE IMPORTANT METRICS.

        If multiple metrics are repetitive, combine them
        into ONE compact bullet instead of repeating
        the same wording.

        For example, instead of:

        FD001: MAE = 12.77 cycles, RMSE = 15.45 cycles,
        Test MAE = 12.77 cycles

        write:

        RUL Performance: FD001 — MAE 12.77, RMSE 15.45 cycles

        However, if Test MAE is different from MAE,
        preserve both values.

        If Test MAE is exactly the same as MAE,
        do not unnecessarily repeat the same number.

        For multiple datasets, combine results compactly.

        Example:

        RUL Performance: FD001 — MAE 12.77, RMSE 15.45;
        FD002 — MAE 12.92, RMSE 16.80;
        FD003 — MAE 11.70, RMSE 16.18;
        FD004 — MAE 10.80, RMSE 16.04 cycles.

        Use 3-5 strong bullets.

        Do not add a separate "Project" heading.

        Return ONLY the project bullets.
        """


    # ========================================================
    # EXPERIENCE
    # ========================================================

    elif section == "experience":

        instruction = f"""
        Rewrite the experience for a one-page resume.

        Maximum length:
        {max_chars} characters.

        Preserve:

        - Responsibilities
        - Technologies
        - Achievements
        - Important technical details
        - Metrics

        Use 2-4 strong bullets.

        Remove generic filler.

        Do not invent anything.

        Return ONLY the final bullets.
        """


    # ========================================================
    # OBJECTIVE
    # ========================================================

    elif section == "objective":

        instruction = f"""
        Create a concise professional career objective.

        Maximum length:
        {max_chars} characters.

        Target role:
        {role}

        Use only information provided by the student.

        Mention relevant technical strengths where useful.

        Avoid generic filler.

        Do not invent experience.

        Return only the objective paragraph.
        """


    # ========================================================
    # SKILLS
    # ========================================================

    elif section == "skills":

        instruction = f"""
        Clean the technical skills.

        Maximum length:
        {max_chars} characters.

        Do not add skills.

        Do not remove important skills.

        Do not duplicate skills.

        Do not use Markdown.

        Return one clean technical skills line.
        """


    # ========================================================
    # CERTIFICATION
    # ========================================================

    elif section == "certification":

        instruction = f"""
        Clean the certification information.

        Maximum length:
        {max_chars} characters.

        Preserve certification names exactly.

        Do not invent certifications.

        Do not duplicate certifications.

        Remove Markdown.

        Return only the certification names.
        """


    # ========================================================
    # DEFAULT
    # ========================================================

    else:

        instruction = f"""
        Improve the content professionally.

        Maximum length:
        {max_chars} characters.

        Preserve all important factual information.

        Do not invent anything.

        Return only the improved content.
        """


    # ========================================================
    # FINAL PROMPT
    # ========================================================

    prompt = f"""
    You are an expert technical resume writer.

    TARGET ROLE:
    {role}

    RESUME SECTION:
    {section}

    MAXIMUM CHARACTER LENGTH:
    {max_chars}

    USER'S ORIGINAL CONTENT:
    {user_input}

    IMPORTANT VALUES DETECTED IN ORIGINAL CONTENT:
    {metrics_text}

    RESUME WRITING KNOWLEDGE RETRIEVED USING RAG:
    {rag_context}

    TASK:
    {instruction}

    GLOBAL RULES:

    1. The user's original content is the source of truth.
    2. Never hallucinate information.
    3. Never add technologies not provided by the user.
    4. Never add algorithms not provided by the user.
    5. Never add datasets not provided by the user.
    6. Never create fake achievements.
    7. Never change numerical values.
    8. Preserve important performance metrics.
    9. Preserve dataset names.
    10. Preserve model names.
    11. Preserve important technical implementation details.
    12. Use strong technical action verbs.
    13. Use concise ATS-friendly language.
    14. Remove Markdown syntax.
    15. Avoid unnecessary repetition.
    16. Prefer information density over generic descriptions.
    17. Do not write explanations.
    18. Return ONLY the final resume content.
    19. Stay within the maximum character length.
    """


    # ========================================================
    # CALL QWEN
    # ========================================================

    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.15
    )


    result = response.choices[
        0
    ].message.content


    result = clean_resume_text(
        result
    )


    # ========================================================
    # FINAL SAFETY LIMIT
    # ========================================================

    result = enforce_character_limit(
        result,
        max_chars
    )


    return result