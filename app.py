from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from db import get_db_connection
from config import SECRET_KEY

from ai.resume_writer import enhance_resume_content
from ai.resume_analyzer import analyze_resume_with_ai
from ai.interview_prep import generate_interview_questions, evaluate_interview
from rag.retriever import retrieve_context

import os
import re
import json
import secrets
import tempfile

from datetime import datetime, timedelta

from mailer import send_password_reset_email, APP_BASE_URL

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

from pypdf import PdfReader

from xml.sax.saxutils import escape


# ============================================================
# ROLE SKILLS
# ============================================================
# ROLE_CATEGORIES groups every selectable career role under a field,
# so the role dropdowns (Analyzer, Generator, Interview Prep) can be
# rendered as grouped <optgroup> lists from one source of truth.
# ROLE_SKILLS (flattened from the categories below) is used wherever
# a flat role -> skills lookup is needed.

ROLE_CATEGORIES = {

    "Software & IT": {
        "Software Engineer": [
            "C++", "Python", "Java", "Data Structures", "Algorithms",
            "OOP", "DBMS", "SQL", "Git", "Operating Systems"
        ],
        "Backend Developer": [
            "Python", "Java", "Node.js", "REST API", "SQL", "DBMS",
            "System Design", "Docker", "Git", "Microservices"
        ],
        "Frontend Developer": [
            "HTML", "CSS", "JavaScript", "React", "TypeScript",
            "Responsive Design", "Git", "REST API", "Accessibility"
        ],
        "Full Stack Developer": [
            "JavaScript", "React", "Node.js", "SQL", "REST API",
            "HTML", "CSS", "Git", "System Design", "Docker"
        ],
        "Web Developer": [
            "HTML", "CSS", "JavaScript", "React", "Node.js",
            "SQL", "Git", "REST API"
        ],
        "Mobile App Developer": [
            "Kotlin", "Swift", "Flutter", "React Native", "REST API",
            "SQLite", "Git", "UI Design", "App Performance"
        ],
        "DevOps Engineer": [
            "Linux", "Docker", "Kubernetes", "CI/CD", "AWS",
            "Terraform", "Git", "Shell Scripting", "Monitoring"
        ],
        "Cloud Engineer": [
            "AWS", "Azure", "GCP", "Linux", "Docker", "Kubernetes",
            "Networking", "Terraform", "CI/CD"
        ],
        "Cybersecurity Analyst": [
            "Network Security", "SIEM", "Vulnerability Assessment",
            "Penetration Testing", "Linux", "Cryptography",
            "Incident Response", "Firewalls", "Risk Assessment"
        ],
        "QA / Test Engineer": [
            "Manual Testing", "Automation Testing", "Selenium",
            "Test Case Design", "API Testing", "SQL", "Bug Tracking",
            "Agile", "Performance Testing"
        ],
        "Data Engineer": [
            "Python", "SQL", "ETL", "Apache Spark", "Data Warehousing",
            "Airflow", "Cloud Platforms", "Data Modeling", "Kafka"
        ],
    },

    "Data & AI": {
        "AI/ML Engineer": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow",
            "PyTorch", "Pandas", "NumPy", "SQL", "Docker", "MLOps", "Git"
        ],
        "Data Scientist": [
            "Python", "Machine Learning", "Statistics", "Pandas",
            "NumPy", "Matplotlib", "SQL", "Scikit-learn",
            "Data Visualization", "Deep Learning"
        ],
        "Data Analyst": [
            "SQL", "Excel", "Python", "Power BI", "Tableau",
            "Data Cleaning", "Statistics", "Data Visualization",
            "Reporting"
        ],
    },

    "Core Engineering": {
        "Mechanical Engineer": [
            "AutoCAD", "SolidWorks", "Thermodynamics", "Manufacturing Processes",
            "CAD/CAM", "Material Science", "Fluid Mechanics", "GD&T", "Quality Control"
        ],
        "Civil Engineer": [
            "AutoCAD", "Structural Analysis", "Construction Management",
            "Surveying", "STAAD Pro", "Building Codes", "Project Planning",
            "Cost Estimation", "Site Supervision"
        ],
        "Electrical Engineer": [
            "Circuit Design", "Power Systems", "MATLAB", "PLC Programming",
            "Electrical Machines", "AutoCAD Electrical", "Control Systems",
            "Switchgear", "Safety Standards"
        ],
        "Electronics & Communication Engineer": [
            "Embedded Systems", "Digital Signal Processing", "VLSI",
            "Microcontrollers", "Communication Systems", "PCB Design",
            "MATLAB", "Circuit Design", "IoT"
        ],
        "Chemical Engineer": [
            "Process Design", "Mass Transfer", "Thermodynamics",
            "Plant Operations", "Process Simulation", "Reaction Engineering",
            "Quality Control", "Safety Compliance", "HAZOP"
        ],
        "Industrial Engineer": [
            "Process Optimization", "Lean Manufacturing", "Six Sigma",
            "Quality Control", "Supply Chain", "Ergonomics",
            "Production Planning", "Time & Motion Study"
        ],
        "Automobile Engineer": [
            "Automotive Design", "CAD", "Vehicle Dynamics", "Engine Systems",
            "Manufacturing Processes", "Quality Testing", "CAE", "Thermodynamics"
        ],
        "Aerospace Engineer": [
            "Aerodynamics", "Flight Mechanics", "CAD", "Propulsion Systems",
            "Structural Analysis", "Avionics", "Materials Science", "CAE"
        ],
    },

    "Finance & Accounts": {
        "Accountant": [
            "Bookkeeping", "Tally", "GST", "Financial Statements",
            "Accounts Reconciliation", "MS Excel", "Taxation",
            "Accounts Payable/Receivable", "Auditing Basics"
        ],
        "Financial Analyst": [
            "Financial Modeling", "Excel", "Valuation", "Forecasting",
            "Budgeting", "Financial Statements", "Ratio Analysis",
            "PowerPoint", "Market Research"
        ],
        "Investment Banking Analyst": [
            "Financial Modeling", "Valuation", "Excel", "PowerPoint",
            "M&A Analysis", "DCF Analysis", "Pitch Decks",
            "Capital Markets", "Due Diligence"
        ],
        "Auditor": [
            "Auditing Standards", "Internal Controls", "Risk Assessment",
            "Financial Statements", "Compliance", "MS Excel",
            "Taxation", "Reporting", "Bookkeeping"
        ],
        "Tax Consultant": [
            "Income Tax", "GST", "Tax Planning", "Tax Compliance",
            "Financial Statements", "MS Excel", "Taxation Law",
            "Auditing Basics"
        ],
    },

    "Marketing": {
        "Marketing Manager": [
            "Marketing Strategy", "Brand Management", "Market Research",
            "Campaign Management", "Budgeting", "Analytics",
            "Team Leadership", "Digital Marketing"
        ],
        "Digital Marketing Specialist": [
            "SEO", "SEM", "Google Ads", "Social Media Marketing",
            "Email Marketing", "Google Analytics", "Content Strategy",
            "Campaign Management"
        ],
        "SEO Specialist": [
            "SEO", "Keyword Research", "Google Analytics", "Google Search Console",
            "Link Building", "On-Page SEO", "Technical SEO", "Content Optimization"
        ],
        "Content Marketing Specialist": [
            "Content Writing", "SEO", "Content Strategy", "Copywriting",
            "Social Media", "Editing", "Analytics", "Storytelling"
        ],
        "Brand Manager": [
            "Brand Strategy", "Market Research", "Campaign Management",
            "Consumer Insights", "Budgeting", "Cross-functional Collaboration",
            "Analytics"
        ],
        "Social Media Manager": [
            "Social Media Strategy", "Content Creation", "Analytics",
            "Community Management", "Campaign Management", "Copywriting",
            "Paid Social Ads"
        ],
    },

    "Sales & Business Development": {
        "Sales Executive": [
            "Lead Generation", "Negotiation", "CRM Software", "Client Relations",
            "Sales Pipeline Management", "Cold Calling", "Target Achievement",
            "Communication"
        ],
        "Business Development Executive": [
            "Market Research", "Lead Generation", "Negotiation", "CRM Software",
            "Partnership Building", "Pitching", "Communication", "Strategic Planning"
        ],
    },

    "Human Resources": {
        "HR Generalist": [
            "Recruitment", "Onboarding", "HR Policies", "Employee Relations",
            "Payroll Basics", "HRIS", "Compliance", "Performance Management"
        ],
        "Talent Acquisition / Recruiter": [
            "Sourcing", "Interviewing", "ATS Software", "Employer Branding",
            "Negotiation", "Candidate Screening", "LinkedIn Recruiting",
            "Onboarding"
        ],
        "HR Business Partner": [
            "Employee Relations", "Performance Management", "Workforce Planning",
            "HR Policies", "Stakeholder Management", "Compliance",
            "Organizational Development"
        ],
    },

    "Operations & Supply Chain": {
        "Operations Manager": [
            "Process Improvement", "Team Management", "Budgeting",
            "Supply Chain Coordination", "Quality Control", "Reporting",
            "Project Management"
        ],
        "Supply Chain Analyst": [
            "Inventory Management", "Demand Forecasting", "Excel",
            "SAP", "Logistics", "Data Analysis", "Procurement",
            "Vendor Management"
        ],
        "Logistics Coordinator": [
            "Inventory Management", "Shipment Tracking", "Vendor Coordination",
            "Warehouse Management", "Excel", "Supply Chain Software",
            "Route Planning"
        ],
    },

    "Design": {
        "UI/UX Designer": [
            "Figma", "Wireframing", "Prototyping", "User Research",
            "Interaction Design", "Adobe XD", "Usability Testing",
            "Design Systems"
        ],
        "Graphic Designer": [
            "Adobe Photoshop", "Adobe Illustrator", "Typography",
            "Branding", "Layout Design", "Color Theory", "Canva",
            "Print & Digital Design"
        ],
        "Product Designer": [
            "Figma", "User Research", "Wireframing", "Prototyping",
            "Design Systems", "Interaction Design", "Usability Testing"
        ],
    },

    "Management & Strategy": {
        "Product Manager": [
            "Product Strategy", "Roadmapping", "User Research", "Agile",
            "Stakeholder Management", "Data Analysis", "Prioritization",
            "Wireframing"
        ],
        "Business Analyst": [
            "Requirements Gathering", "SQL", "Process Mapping",
            "Stakeholder Management", "Excel", "Data Analysis",
            "Documentation", "Agile"
        ],
        "Project Manager": [
            "Project Planning", "Agile", "Scrum", "Risk Management",
            "Budgeting", "Stakeholder Management", "MS Project",
            "Team Leadership"
        ],
        "Management Consultant": [
            "Problem Solving", "Data Analysis", "PowerPoint", "Excel",
            "Market Research", "Strategic Planning", "Client Management",
            "Business Case Development"
        ],
    },

}

ROLE_SKILLS = {
    role: skills
    for category_roles in ROLE_CATEGORIES.values()
    for role, skills in category_roles.items()
}


# ============================================================
# ONE-PAGE RESUME LIMITS
# ============================================================

OBJECTIVE_LIMIT = 420
COURSEWORK_LIMIT = 250

PROJECT_TITLE_LIMIT = 110
PROJECT_TECH_LIMIT = 220
PROJECT_LIMIT = 900

PROGRAMMING_LIMIT = 220
SKILLS_LIMIT = 500

EXPERIENCE_LIMIT = 550
CERTIFICATION_LIMIT = 250


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.config["UPLOAD_FOLDER"] = "uploads"

os.makedirs(
    "uploads",
    exist_ok=True
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_resume_text(text):

    if not text:
        return ""

    text = str(text)

    text = text.replace("```", "")

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"(?<!\w)\*(?!\w)",
        "",
        text
    )

    text = text.replace("`", "")

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# BULLET CLEANING
# ============================================================

def clean_bullet_marker(line):

    if not line:
        return ""

    line = line.strip()

    line = re.sub(
        r"^\s*(?:[•●▪◦*\-]|\d+[.)])\s*",
        "",
        line
    )

    return line.strip()


# ============================================================
# CHARACTER LIMIT
# ============================================================

def limit_text(text, limit):

    if not text:
        return ""

    text = clean_resume_text(text)

    if len(text) <= limit:
        return text

    shortened = text[:limit]

    positions = [
        shortened.rfind(". "),
        shortened.rfind("; "),
        shortened.rfind("."),
        shortened.rfind(";"),
        shortened.rfind(",")
    ]

    best_position = max(positions)

    if best_position >= int(limit * 0.65):

        shortened = shortened[
            :best_position + 1
        ]

    else:

        shortened = shortened.rsplit(
            " ",
            1
        )[0]

    return shortened.strip()


# ============================================================
# IMPORTANT METRICS
# ============================================================

def extract_important_metrics(text):

    if not text:
        return []

    text = str(text)

    metrics = []

    patterns = [

        r"\bMAE\s*[:=]\s*[\d.]+(?:\s*cycles?)?",

        r"\bRMSE\s*[:=]\s*[\d.]+(?:\s*cycles?)?",

        r"\bAccuracy\s*[:=]\s*[\d.]+%?",

        r"\bPrecision\s*[:=]\s*[\d.]+%?",

        r"\bRecall\s*[:=]\s*[\d.]+%?",

        r"\bF1(?:[-\s]?score)?\s*[:=]\s*[\d.]+%?",

        r"\bROC[-\s]?AUC\s*[:=]\s*[\d.]+%?",

        r"\bFD00[1-4]\b[^,\n;]*"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            cleaned = clean_resume_text(
                match
            )

            if cleaned and cleaned not in metrics:

                metrics.append(
                    cleaned
                )

    return metrics


# ============================================================
# METRIC LINES
# ============================================================

def extract_metric_lines(text):

    if not text:
        return []

    important = []

    metric_words = [
        "mae",
        "rmse",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc-auc",
        "roc auc",
        "fd001",
        "fd002",
        "fd003",
        "fd004"
    ]

    for line in str(text).splitlines():

        clean_line = clean_resume_text(
            line
        )

        if not clean_line:
            continue

        lower_line = clean_line.lower()

        if any(
            word in lower_line
            for word in metric_words
        ):

            if clean_line not in important:

                important.append(
                    clean_line
                )

    return important


# ============================================================
# PRESERVE IMPORTANT METRICS
# ============================================================

def preserve_metrics(
    original_text,
    enhanced_text,
    limit
):

    original_text = clean_resume_text(
        original_text
    )

    enhanced_text = clean_resume_text(
        enhanced_text
    )

    if not original_text:
        return limit_text(
            enhanced_text,
            limit
        )

    metric_lines = extract_metric_lines(
        original_text
    )

    if not metric_lines:

        return limit_text(
            enhanced_text,
            limit
        )

    missing_lines = []

    for line in metric_lines:

        numbers = re.findall(
            r"\d+(?:\.\d+)?",
            line
        )

        if not numbers:
            continue

        all_present = all(
            number in enhanced_text
            for number in numbers
        )

        if not all_present:

            missing_lines.append(
                line
            )

    if not missing_lines:

        return limit_text(
            enhanced_text,
            limit
        )

    compact_metrics = []

    for line in missing_lines:

        clean_line = clean_bullet_marker(
            line
        )

        if clean_line not in compact_metrics:

            compact_metrics.append(
                clean_line
            )

    metric_text = (
        "Key Results: "
        + "; ".join(compact_metrics)
    )

    combined = (
        enhanced_text.rstrip()
        + "\n"
        + metric_text
    )

    if len(combined) <= limit:

        return combined

    # Reserve enough space for important metrics.
    metric_budget = min(
        len(metric_text),
        int(limit * 0.45)
    )

    shortened_metrics = limit_text(
        metric_text,
        metric_budget
    )

    content_budget = (
        limit
        - len(shortened_metrics)
        - 2
    )

    if content_budget < 100:

        content_budget = 100

    shortened_content = limit_text(
        enhanced_text,
        content_budget
    )

    result = (
        shortened_content.rstrip()
        + "\n"
        + shortened_metrics
    )

    return limit_text(
        result,
        limit
    )


# ============================================================
# RAG + QWEN ENHANCEMENT
# ============================================================

def enhance_if_available(
    content,
    role,
    section,
    limit=None
):

    if not content or not content.strip():
        return ""

    original_content = clean_resume_text(
        content
    )

    try:

        enhanced = enhance_resume_content(
            original_content,
            role,
            section
        )

    except Exception:

        # If AI enhancement fails, retain the
        # user's original content.
        enhanced = original_content

    enhanced = clean_resume_text(
        enhanced
    )

    if section == "project":

        enhanced = preserve_metrics(
            original_content,
            enhanced,
            limit or PROJECT_LIMIT
        )

    elif limit:

        enhanced = limit_text(
            enhanced,
            limit
        )

    return enhanced


# ============================================================
# PROJECT TEXT COMPRESSION
# ============================================================

def compress_project_lines(
    original_text,
    enhanced_text,
    limit
):

    enhanced_text = preserve_metrics(
        original_text,
        enhanced_text,
        limit
    )

    lines = []

    for line in enhanced_text.splitlines():

        line = clean_bullet_marker(
            line
        )

        if not line:
            continue

        lower = line.lower()

        if lower in [
            "projects",
            "project",
            "project description",
            "key results"
        ]:
            continue

        lines.append(line)

    # Keep each project readable.
    # Do not allow excessive bullet count.
    if len(lines) > 5:

        metric_lines = []

        normal_lines = []

        for line in lines:

            low = line.lower()

            if any(
                word in low
                for word in [
                    "mae",
                    "rmse",
                    "accuracy",
                    "precision",
                    "recall",
                    "f1",
                    "roc-auc",
                    "fd001",
                    "fd002",
                    "fd003",
                    "fd004"
                ]
            ):

                metric_lines.append(line)

            else:

                normal_lines.append(line)

        lines = (
            normal_lines[:4]
            + metric_lines
        )

    result = "\n".join(
        lines
    )

    return limit_text(
        result,
        limit
    )


# ============================================================
# ADD PROJECT TO PDF
# ============================================================

def add_project_to_story(
    story,
    title,
    technologies,
    original_project_text,
    enhanced_project_text,
    styles
):

    if not title and not enhanced_project_text:
        return

    # --------------------------------------------------------
    # PROJECT TITLE
    # --------------------------------------------------------

    if title:

        title = limit_text(
            title,
            PROJECT_TITLE_LIMIT
        )

        story.append(
            Paragraph(
                f"<b>{escape(title)}</b>",
                styles["Heading3"]
            )
        )

    # --------------------------------------------------------
    # TECHNOLOGIES
    # --------------------------------------------------------

    if technologies:

        technologies = clean_resume_text(
            technologies
        )

        technologies = limit_text(
            technologies,
            PROJECT_TECH_LIMIT
        )

        story.append(
            Paragraph(
                f"<b>Technologies:</b> "
                f"{escape(technologies)}",
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 3)
        )

    # --------------------------------------------------------
    # PROJECT DESCRIPTION
    # --------------------------------------------------------

    if enhanced_project_text:

        enhanced_project_text = compress_project_lines(
            original_project_text,
            enhanced_project_text,
            PROJECT_LIMIT
        )

        lines = enhanced_project_text.splitlines()

        for line in lines:

            line = clean_bullet_marker(
                line
            )

            if not line:
                continue

            story.append(
                Paragraph(
                    f"• {escape(line)}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 2)
            )

    # Space between projects.
    story.append(
        Spacer(1, 7)
    )


# ============================================================
# RESUME STYLES
# ============================================================

def create_resume_styles():

    styles = getSampleStyleSheet()

    # ========================================================
    # IMPORTANT:
    # MAIN TEXT = 11 PT
    # ========================================================

    styles["Title"].fontSize = 18
    styles["Title"].leading = 20
    styles["Title"].alignment = TA_CENTER
    styles["Title"].spaceBefore = 0
    styles["Title"].spaceAfter = 4

    styles["Heading2"].fontSize = 12
    styles["Heading2"].leading = 14
    styles["Heading2"].spaceBefore = 8
    styles["Heading2"].spaceAfter = 5

    styles["Heading3"].fontSize = 11
    styles["Heading3"].leading = 13
    styles["Heading3"].spaceBefore = 3
    styles["Heading3"].spaceAfter = 2

    # MAIN BODY TEXT
    styles["Normal"].fontSize = 11
    styles["Normal"].leading = 12.5
    styles["Normal"].spaceBefore = 0
    styles["Normal"].spaceAfter = 1

    return styles


# ============================================================
# PDF BUILDER
# ============================================================

def _build_resume_pdf(
    form,
    filepath
):

    # ========================================================
    # PERSONAL INFORMATION
    # ========================================================

    name = form.get(
        "name",
        ""
    ).strip()

    email = form.get(
        "email",
        ""
    ).strip()

    phone = form.get(
        "phone",
        ""
    ).strip()

    address = form.get(
        "address",
        ""
    ).strip()

    # ========================================================
    # OBJECTIVE
    # ========================================================

    objective = form.get(
        "objective",
        ""
    ).strip()

    # ========================================================
    # COURSEWORK
    # ========================================================

    coursework = form.get(
        "coursework",
        ""
    ).strip()

    # ========================================================
    # EDUCATION
    # ========================================================

    college = form.get(
        "college",
        ""
    ).strip()

    degree = form.get(
        "degree",
        ""
    ).strip()

    cgpa = form.get(
        "cgpa",
        ""
    ).strip()

    education_start = form.get(
        "education_start",
        ""
    ).strip()

    education_end = form.get(
        "education_end",
        ""
    ).strip()

    # ========================================================
    # PROJECT 1
    # ========================================================

    project1_title = form.get(
        "project1_title",
        ""
    ).strip()

    project1_technologies = form.get(
        "project1_technologies",
        ""
    ).strip()

    project1 = form.get(
        "project1",
        ""
    ).strip()

    # ========================================================
    # PROJECT 2
    # ========================================================

    project2_title = form.get(
        "project2_title",
        ""
    ).strip()

    project2_technologies = form.get(
        "project2_technologies",
        ""
    ).strip()

    project2 = form.get(
        "project2",
        ""
    ).strip()

    # ========================================================
    # SKILLS
    # ========================================================

    programming_languages = clean_resume_text(
        form.get(
            "programming_languages",
            ""
        ).strip()
    )

    other_skills = clean_resume_text(
        form.get(
            "other_skills",
            ""
        ).strip()
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    experience = form.get(
        "experience",
        ""
    ).strip()

    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    certifications = form.get(
        "certifications",
        ""
    ).strip()

    # ========================================================
    # ROLE
    # ========================================================

    role = form.get(
        "role",
        "Software Engineer"
    ).strip()

    # ========================================================
    # OBJECTIVE
    # ========================================================

    if objective:

        enhanced_objective = enhance_if_available(
            objective,
            role,
            "objective",
            OBJECTIVE_LIMIT
        )

    else:

        objective_parts = []

        if degree:

            objective_parts.append(
                f"Student pursuing {degree}."
            )

        if role:

            objective_parts.append(
                f"Seeking opportunities as a {role}."
            )

        if programming_languages:

            objective_parts.append(
                f"Programming: {programming_languages}"
            )

        if other_skills:

            objective_parts.append(
                f"Technical skills: {other_skills}"
            )

        objective_input = "\n".join(
            objective_parts
        )

        if objective_input:

            enhanced_objective = enhance_if_available(
                objective_input,
                role,
                "objective",
                OBJECTIVE_LIMIT
            )

        else:

            enhanced_objective = ""

    # ========================================================
    # PROJECTS
    # ========================================================

    enhanced_project1 = enhance_if_available(
        project1,
        role,
        "project",
        PROJECT_LIMIT
    )

    enhanced_project2 = enhance_if_available(
        project2,
        role,
        "project",
        PROJECT_LIMIT
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    enhanced_experience = enhance_if_available(
        experience,
        role,
        "experience",
        EXPERIENCE_LIMIT
    )

    # ========================================================
    # FINAL CONTENT LIMITS
    # ========================================================

    enhanced_objective = limit_text(
        enhanced_objective,
        OBJECTIVE_LIMIT
    )

    enhanced_project1 = compress_project_lines(
        project1,
        enhanced_project1,
        PROJECT_LIMIT
    )

    enhanced_project2 = compress_project_lines(
        project2,
        enhanced_project2,
        PROJECT_LIMIT
    )

    enhanced_experience = limit_text(
        enhanced_experience,
        EXPERIENCE_LIMIT
    )

    coursework = limit_text(
        coursework,
        COURSEWORK_LIMIT
    )

    programming_languages = limit_text(
        programming_languages,
        PROGRAMMING_LIMIT
    )

    other_skills = limit_text(
        other_skills,
        SKILLS_LIMIT
    )

    certifications = limit_text(
        certifications,
        CERTIFICATION_LIMIT
    )

    # ========================================================
    # DOCUMENT
    # ========================================================

    document = SimpleDocTemplate(
        filepath,
        pagesize=A4,

        # Enough usable space while maintaining
        # a professional page layout.
        rightMargin=32,
        leftMargin=32,
        topMargin=25,
        bottomMargin=25
    )

    styles = create_resume_styles()

    story = []

    # ========================================================
    # NAME
    # ========================================================

    if name:

        story.append(
            Paragraph(
                f"<b>{escape(name)}</b>",
                styles["Title"]
            )
        )

    # ========================================================
    # CONTACT
    # ========================================================

    contact_parts = []

    if email:
        contact_parts.append(
            escape(email)
        )

    if phone:
        contact_parts.append(
            escape(phone)
        )

    if address:
        contact_parts.append(
            escape(address)
        )

    if contact_parts:

        story.append(
            Paragraph(
                " | ".join(contact_parts),
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # CAREER OBJECTIVE
    # ========================================================

    if enhanced_objective:

        story.append(
            Paragraph(
                "<b>CAREER OBJECTIVE</b>",
                styles["Heading2"]
            )
        )

        for line in enhanced_objective.splitlines():

            line = clean_bullet_marker(
                line
            )

            if line:

                story.append(
                    Paragraph(
                        escape(line),
                        styles["Normal"]
                    )
                )

        story.append(
            Spacer(1, 4)
        )

    # ========================================================
    # COURSE WORK
    # ========================================================

    if coursework:

        story.append(
            Paragraph(
                "<b>COURSE WORK</b>",
                styles["Heading2"]
            )
        )

        coursework_parts = []

        for line in coursework.splitlines():

            line = clean_bullet_marker(
                line
            )

            if line:

                coursework_parts.append(
                    line
                )

        if coursework_parts:

            coursework_text = " | ".join(
                coursework_parts
            )

            story.append(
                Paragraph(
                    escape(coursework_text),
                    styles["Normal"]
                )
            )

        story.append(
            Spacer(1, 4)
        )

    # ========================================================
    # EDUCATION
    # ========================================================

    if college or degree:

        story.append(
            Paragraph(
                "<b>EDUCATION</b>",
                styles["Heading2"]
            )
        )

        education_parts = []

        if degree:

            education_parts.append(
                escape(degree)
            )

        if cgpa:

            education_parts.append(
                f"CGPA: {escape(cgpa)}"
            )

        if education_start or education_end:

            date_text = education_start

            if education_end:

                if date_text:

                    date_text += " - "

                date_text += education_end

            if date_text:

                education_parts.append(
                    escape(date_text)
                )

        if education_parts:

            story.append(
                Paragraph(
                    " | ".join(education_parts),
                    styles["Normal"]
                )
            )

        if college:

            story.append(
                Paragraph(
                    escape(college),
                    styles["Normal"]
                )
            )

        story.append(
            Spacer(1, 4)
        )

    # ========================================================
    # PROJECTS
    # ========================================================

    if (
        project1_title
        or project1
        or project2_title
        or project2
    ):

        story.append(
            Paragraph(
                "<b>PROJECTS</b>",
                styles["Heading2"]
            )
        )

        add_project_to_story(
            story,
            project1_title,
            project1_technologies,
            project1,
            enhanced_project1,
            styles
        )

        add_project_to_story(
            story,
            project2_title,
            project2_technologies,
            project2,
            enhanced_project2,
            styles
        )

        story.append(
            Spacer(1, 2)
        )

    # ========================================================
    # TECHNICAL SKILLS
    # ========================================================

    if programming_languages or other_skills:

        story.append(
            Paragraph(
                "<b>TECHNICAL SKILLS</b>",
                styles["Heading2"]
            )
        )

        if programming_languages:

            story.append(
                Paragraph(
                    f"<b>Languages:</b> "
                    f"{escape(programming_languages)}",
                    styles["Normal"]
                )
            )

        if other_skills:

            story.append(
                Paragraph(
                    f"<b>Other Skills:</b> "
                    f"{escape(other_skills)}",
                    styles["Normal"]
                )
            )

        story.append(
            Spacer(1, 4)
        )

    # ========================================================
    # EXPERIENCE & INTERESTS
    # ========================================================

    if enhanced_experience:

        story.append(
            Paragraph(
                "<b>EXPERIENCE &amp; INTERESTS</b>",
                styles["Heading2"]
            )
        )

        for line in enhanced_experience.splitlines():

            line = clean_bullet_marker(
                line
            )

            if line:

                story.append(
                    Paragraph(
                        f"• {escape(line)}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Spacer(1, 2)
                )

        story.append(
            Spacer(1, 3)
        )

    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    if certifications:

        story.append(
            Paragraph(
                "<b>CERTIFICATIONS</b>",
                styles["Heading2"]
            )
        )

        for line in certifications.splitlines():

            line = clean_bullet_marker(
                line
            )

            if not line:
                continue

            if line.lower() in [
                "certification",
                "certifications"
            ]:

                continue

            story.append(
                Paragraph(
                    f"• {escape(line)}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 2)
            )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )


# ============================================================
# ONE-PAGE PDF BUILDER
# ============================================================

def build_resume_pdf(
    form,
    preview=False
):

    name = form.get(
        "name",
        ""
    ).strip()

    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        name
    ).strip("_")

    if not safe_name:

        safe_name = "Resume"

    if preview:

        filename = (
            f"{safe_name}_Resume_Preview.pdf"
        )

    else:

        filename = (
            f"{safe_name}_Resume.pdf"
        )

    filepath = os.path.join(
        "uploads",
        filename
    )

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    _build_resume_pdf(
        form,
        filepath
    )

    # --------------------------------------------------------
    # CHECK PAGE COUNT
    # --------------------------------------------------------

    try:

        page_count = len(
            PdfReader(filepath).pages
        )

    except Exception:

        page_count = 1

    # The normal version is the preferred version.
    if page_count == 1:

        return filepath

    # --------------------------------------------------------
    # IF TWO PAGES:
    #
    # The content budgets are already deliberately limited.
    # Ask the AI layer to compress the sections further by
    # creating a shortened form while preserving metrics.
    # --------------------------------------------------------

    compressed_form = form.copy()

    # Objective
    objective = compressed_form.get(
        "objective",
        ""
    ).strip()

    if objective:

        compressed_form["objective"] = (
            enhance_if_available(
                objective,
                compressed_form.get(
                    "role",
                    "Software Engineer"
                ),
                "objective",
                340
            )
        )

    # Project 1
    project1 = compressed_form.get(
        "project1",
        ""
    ).strip()

    if project1:

        enhanced = enhance_if_available(
            project1,
            compressed_form.get(
                "role",
                "Software Engineer"
            ),
            "project",
            720
        )

        compressed_form["project1"] = (
            compress_project_lines(
                project1,
                enhanced,
                720
            )
        )

    # Project 2
    project2 = compressed_form.get(
        "project2",
        ""
    ).strip()

    if project2:

        enhanced = enhance_if_available(
            project2,
            compressed_form.get(
                "role",
                "Software Engineer"
            ),
            "project",
            720
        )

        compressed_form["project2"] = (
            compress_project_lines(
                project2,
                enhanced,
                720
            )
        )

    # Experience
    experience = compressed_form.get(
        "experience",
        ""
    ).strip()

    if experience:

        compressed_form["experience"] = (
            enhance_if_available(
                experience,
                compressed_form.get(
                    "role",
                    "Software Engineer"
                ),
                "experience",
                350
            )
        )

    # Coursework
    compressed_form["coursework"] = limit_text(
        compressed_form.get(
            "coursework",
            ""
        ),
        200
    )

    # Skills
    compressed_form["other_skills"] = limit_text(
        compressed_form.get(
            "other_skills",
            ""
        ),
        400
    )

    # Certifications
    compressed_form["certifications"] = limit_text(
        compressed_form.get(
            "certifications",
            ""
        ),
        180
    )

    # --------------------------------------------------------
    # BUILD COMPRESSED VERSION
    # --------------------------------------------------------

    _build_resume_pdf(
        compressed_form,
        filepath
    )

    try:

        page_count = len(
            PdfReader(filepath).pages
        )

    except Exception:

        page_count = 1

    if page_count == 1:

        return filepath

    # --------------------------------------------------------
    # FINAL FALLBACK
    #
    # Keep 11 pt font but remove lower-priority content
    # before allowing the resume to become unnecessarily
    # congested.
    # --------------------------------------------------------

    final_form = compressed_form.copy()

    # Keep important project information.
    final_form["project1"] = limit_text(
        final_form.get(
            "project1",
            ""
        ),
        650
    )

    final_form["project1"] = preserve_metrics(
        project1,
        final_form["project1"],
        650
    )

    final_form["project2"] = limit_text(
        final_form.get(
            "project2",
            ""
        ),
        650
    )

    final_form["project2"] = preserve_metrics(
        project2,
        final_form["project2"],
        650
    )

    final_form["objective"] = limit_text(
        final_form.get(
            "objective",
            ""
        ),
        280
    )

    final_form["experience"] = limit_text(
        final_form.get(
            "experience",
            ""
        ),
        280
    )

    final_form["coursework"] = limit_text(
        final_form.get(
            "coursework",
            ""
        ),
        150
    )

    final_form["other_skills"] = limit_text(
        final_form.get(
            "other_skills",
            ""
        ),
        320
    )

    final_form["certifications"] = limit_text(
        final_form.get(
            "certifications",
            ""
        ),
        140
    )

    _build_resume_pdf(
        final_form,
        filepath
    )

    return filepath


# ============================================================
# BASIC ROUTES
# ============================================================

@app.route("/")
def home():

    if session.get("role") == "student":

        return redirect(
            "/student/dashboard"
        )

    if session.get("role") == "admin":

        return redirect(
            "/admin/dashboard"
        )

    return redirect(
        "/login"
    )


@app.route("/generator")
def generator():

    return render_template(
        "generator.html",
        role_categories=ROLE_CATEGORIES
    )


@app.route("/analyzer")
def analyzer():

    return render_template(
        "analyzer.html",
        role_categories=ROLE_CATEGORIES
    )


# ============================================================
# GENERATE RESUME
# ============================================================

@app.route(
    "/generate_resume",
    methods=["POST"]
)
def generate_resume():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    filepath = build_resume_pdf(
        request.form,
        preview=False
    )

    return send_file(
        filepath,
        as_attachment=True
    )


# ============================================================
# PREVIEW RESUME
# ============================================================

@app.route(
    "/preview_resume",
    methods=["POST"]
)
def preview_resume():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    filepath = build_resume_pdf(
        request.form,
        preview=True
    )

    return send_file(
        filepath,
        as_attachment=False
    )


# ============================================================
# RESUME ANALYZER
# ============================================================

@app.route(
    "/analyze_resume",
    methods=["POST"]
)
def analyze_resume():

    resume = request.files["resume"]

    role = request.form["role"]

    if resume.filename == "":

        return "No file selected"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(
        filepath
    )

    reader = PdfReader(
        filepath
    )

    resume_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:

            resume_text += (
                text + "\n"
            )

    query = f"""
    What skills, technologies, projects and resume requirements
    are expected for a {role}?
    """

    documents, metadata = retrieve_context(
        query,
        role,
        n_results=5
    )

    rag_context = "\n\n".join(
        documents
    )

    analysis = analyze_resume_with_ai(
        resume_text,
        role,
        rag_context
    )

    return render_template(
        "analysis_result.html",
        role=role,
        score=analysis["overall_score"],
        eligibility=analysis["eligibility"],
        category_scores=analysis["category_scores"],
        education=analysis["education"],
        skills=analysis["skills"],
        projects=analysis["projects"],
        certifications=analysis["certifications"],
        experience=analysis["experience"],
        keywords=analysis["keywords"],
        strengths=analysis["strengths"],
        weak_areas=analysis["weak_areas"],
        recommendations=analysis["recommendations"]
    )


# ============================================================
# INTERVIEW PREP
# ============================================================

@app.route(
    "/interview-prep"
)
def interview_prep():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    return render_template(
        "interview_prep.html",
        role_categories=ROLE_CATEGORIES
    )


@app.route(
    "/interview-prep/generate",
    methods=["POST"]
)
def interview_prep_generate():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    role = request.form["role"]

    query = f"""
    What skills, technologies, projects and typical interview questions
    are relevant for a {role}?
    """

    documents, metadata = retrieve_context(
        query,
        role,
        n_results=5
    )

    rag_context = "\n\n".join(
        documents
    )

    result = generate_interview_questions(
        role,
        rag_context
    )

    return render_template(
        "interview_prep_result.html",
        role=role,
        questions=result["questions"]
    )


@app.route(
    "/interview-prep/evaluate",
    methods=["POST"]
)
def interview_prep_evaluate():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    role = request.form["role"]

    transcript_raw = request.form["transcript"]

    try:

        qa_pairs = json.loads(transcript_raw)

    except (ValueError, TypeError):

        qa_pairs = []

    result = evaluate_interview(
        role,
        qa_pairs
    )

    return render_template(
        "interview_score.html",
        role=role,
        result=result
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    name = request.form["name"]

    email = request.form["email"]

    password = request.form["password"]

    confirm_password = request.form[
        "confirm_password"
    ]

    role = request.form["role"]

    special_chars = set('!@#$%^&*()_+-=[]{};:\'",.<>/?\\')

    has_number_or_symbol = any(
        ch.isdigit() or ch in special_chars
        for ch in password
    )

    if len(password) < 8 or not has_number_or_symbol:

        return render_template(
            "register.html",
            error="Password must be at least 8 characters long and include at least one number or special character (such as @, #, $).",
            name=name,
            email=email,
            role=role
        ), 400

    if password != confirm_password:

        return render_template(
            "register.html",
            error="Passwords do not match. Please try again.",
            name=name,
            email=email,
            role=role
        ), 400

    hashed_password = generate_password_hash(
        password
    )

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (email, password, role)
            VALUES
            (%s, %s, %s)
            """,
            (
                email,
                hashed_password,
                role
            )
        )

        user_id = cursor.lastrowid

        if role == "student":

            cursor.execute(
                """
                INSERT INTO students
                (user_id, name)
                VALUES
                (%s, %s)
                """,
                (
                    user_id,
                    name
                )
            )

        connection.commit()

    except Exception as e:

        connection.rollback()

        cursor.close()
        connection.close()

        if "Duplicate entry" in str(e):

            friendly_error = "An account with this email already exists. Try logging in instead."

        else:

            friendly_error = "Registration failed. Please try again."

        return render_template(
            "register.html",
            error=friendly_error,
            name=name,
            email=email,
            role=role
        ), 400

    cursor.close()
    connection.close()

    return redirect(
        "/login"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html",
            reset_success=(request.args.get("reset") == "success")
        )

    email = request.form["email"]

    password = request.form["password"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:

        return render_template(
            "login.html",
            error="That email or password doesn't look right. Please try again.",
            email=email
        ), 401

    if not check_password_hash(
        user["password"],
        password
    ):

        return render_template(
            "login.html",
            error="That email or password doesn't look right. Please try again.",
            email=email
        ), 401

    session["user_id"] = user["id"]

    session["role"] = user["role"]

    if user["role"] == "student":

        return redirect(
            "/student/dashboard"
        )

    return redirect(
        "/admin/dashboard"
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "GET":

        return render_template(
            "forgot_password.html"
        )

    email = request.form["email"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user:

            token = secrets.token_urlsafe(32)

            expires_at = datetime.now() + timedelta(minutes=30)

            cursor.execute(
                """
                INSERT INTO password_resets
                (user_id, token, expires_at)
                VALUES
                (%s, %s, %s)
                """,
                (
                    user["id"],
                    token,
                    expires_at
                )
            )

            connection.commit()

            reset_link = f"{APP_BASE_URL}/reset-password/{token}"

            send_password_reset_email(
                email,
                reset_link
            )

    finally:

        cursor.close()
        connection.close()

    # Always show the same message, whether or not the email exists,
    # so this form can't be used to check which emails are registered.
    return render_template(
        "forgot_password.html",
        sent=True
    )


@app.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                expires_at,
                used
            FROM password_resets
            WHERE token = %s
            """,
            (token,)
        )

        reset_row = cursor.fetchone()

        token_valid = (
            reset_row is not None
            and not reset_row["used"]
            and reset_row["expires_at"] > datetime.now()
        )

        if not token_valid:

            return render_template(
                "reset_password.html",
                invalid=True
            )

        if request.method == "GET":

            return render_template(
                "reset_password.html",
                token=token
            )

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        special_chars = set('!@#$%^&*()_+-=[]{};:\'",.<>/?\\')

        has_number_or_symbol = any(
            ch.isdigit() or ch in special_chars
            for ch in password
        )

        if len(password) < 8 or not has_number_or_symbol:

            return render_template(
                "reset_password.html",
                token=token,
                error="Password must be at least 8 characters long and include at least one number or special character (such as @, #, $)."
            )

        if password != confirm_password:

            return render_template(
                "reset_password.html",
                token=token,
                error="Passwords do not match. Please try again."
            )

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                reset_row["user_id"]
            )
        )

        cursor.execute(
            """
            UPDATE password_resets
            SET used = 1
            WHERE id = %s
            """,
            (reset_row["id"],)
        )

        connection.commit()

        return redirect(
            "/login?reset=success"
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route(
    "/student/dashboard"
)
def student_dashboard():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    applications_count = 0

    resume_uploaded = False

    profile_percent = 0

    if student:

        student_id = student["id"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM applications
            WHERE student_id = %s
            """,
            (student_id,)
        )

        applications_count = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT id
            FROM resumes
            WHERE student_id = %s
            AND resume_type = 'uploaded'
            LIMIT 1
            """,
            (student_id,)
        )

        resume_uploaded = cursor.fetchone() is not None

        profile_fields = [
            student.get("name"),
            student.get("phone"),
            student.get("college"),
            student.get("degree"),
            student.get("branch"),
            student.get("cgpa"),
            student.get("skills"),
            student.get("preferred_role"),
        ]

        filled = sum(1 for field in profile_fields if field)

        profile_percent = round(
            (filled / len(profile_fields)) * 100
        )

    recent_applications = []

    if student:

        cursor.execute(
            """
            SELECT
                applications.id,
                applications.status,
                jobs.id AS job_id,
                jobs.title AS job_title,
                companies.name AS company_name
            FROM applications
            JOIN jobs
                ON applications.job_id = jobs.id
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE applications.student_id = %s
            ORDER BY applications.id DESC
            LIMIT 3
            """,
            (student_id,)
        )

        recent_applications = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            jobs.id,
            jobs.title,
            jobs.location,
            jobs.job_type,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        ORDER BY jobs.created_at DESC
        LIMIT 3
        """
    )

    latest_jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        applications_count=applications_count,
        resume_uploaded=resume_uploaded,
        profile_percent=profile_percent,
        recent_applications=recent_applications,
        latest_jobs=latest_jobs
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route(
    "/admin/dashboard"
)
def admin_dashboard():

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute("SELECT COUNT(*) AS total FROM companies")
    companies_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    jobs_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    applications_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM applications
        WHERE status = 'Applied'
        """
    )
    pending_review_count = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        pending_review_count=pending_review_count
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login"
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route(
    "/student/profile",
    methods=["GET", "POST"]
)
def student_profile():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    if student is None:

        cursor.close()
        connection.close()

        return (
            "Student profile not found",
            404
        )

    student_id = student["id"]

    if request.method == "POST":

        name = request.form["name"]

        phone = request.form["phone"]

        college = request.form["college"]

        degree = request.form["degree"]

        branch = request.form["branch"]

        cgpa = (
            request.form["cgpa"]
            or None
        )

        graduation_year = (
            request.form["graduation_year"]
            or None
        )

        skills = request.form["skills"]

        projects = request.form["projects"]

        certifications = request.form[
            "certifications"
        ]

        experience = request.form[
            "experience"
        ]

        preferred_role = request.form[
            "preferred_role"
        ]

        cursor.execute(
            """
            UPDATE students
            SET
                name = %s,
                phone = %s,
                college = %s,
                degree = %s,
                branch = %s,
                cgpa = %s,
                graduation_year = %s,
                skills = %s,
                projects = %s,
                certifications = %s,
                experience = %s,
                preferred_role = %s
            WHERE user_id = %s
            """,
            (
                name,
                phone,
                college,
                degree,
                branch,
                cgpa,
                graduation_year,
                skills,
                projects,
                certifications,
                experience,
                preferred_role,
                user_id
            )
        )

        connection.commit()

        resume = request.files.get(
            "resume"
        )

        if resume and resume.filename:

            if not resume.filename.lower().endswith(
                ".pdf"
            ):

                cursor.close()
                connection.close()

                return (
                    "Only PDF resumes are allowed."
                )

            upload_folder = (
                "uploads/resumes"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            original_filename = (
                resume.filename
            )

            filename = (
                f"{student_id}_resume.pdf"
            )

            filepath = os.path.join(
                upload_folder,
                filename
            )

            resume.save(
                filepath
            )

            cursor.execute(
                """
                SELECT id
                FROM resumes
                WHERE student_id = %s
                AND resume_type = 'uploaded'
                ORDER BY uploaded_at DESC
                LIMIT 1
                """,
                (student_id,)
            )

            existing_resume = (
                cursor.fetchone()
            )

            if existing_resume:

                cursor.execute(
                    """
                    UPDATE resumes
                    SET
                        file_name = %s,
                        file_path = %s,
                        uploaded_at =
                            CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        original_filename,
                        filepath,
                        existing_resume["id"]
                    )
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO resumes
                    (
                        student_id,
                        file_name,
                        file_path,
                        resume_type
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        'uploaded'
                    )
                    """,
                    (
                        student_id,
                        original_filename,
                        filepath
                    )
                )

            connection.commit()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE user_id = %s
            """,
            (user_id,)
        )

        student = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM resumes
        WHERE student_id = %s
        AND resume_type = 'uploaded'
        ORDER BY uploaded_at DESC
        LIMIT 1
        """,
        (student_id,)
    )

    resume = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "student_profile.html",
        student=student,
        resume=resume
    )


# ============================================================
# STUDENT - VIEW OWN RESUME
# ============================================================

@app.route("/student/resume/view")
def view_own_resume():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    if student is None:

        cursor.close()
        connection.close()

        return (
            "Student profile not found",
            404
        )

    cursor.execute(
        """
        SELECT *
        FROM resumes
        WHERE student_id = %s
        AND resume_type = 'uploaded'
        ORDER BY uploaded_at DESC
        LIMIT 1
        """,
        (student["id"],)
    )

    resume = cursor.fetchone()

    cursor.close()
    connection.close()

    if resume is None:

        return (
            "No resume uploaded yet",
            404
        )

    return send_file(
        resume["file_path"],
        mimetype="application/pdf"
    )


# ============================================================
# ADMIN - ADD COMPANY
# ============================================================

@app.route(
    "/admin/company/add",
    methods=["GET", "POST"]
)
def add_company():

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    if request.method == "GET":

        return render_template(
            "add_company.html"
        )

    name = request.form["name"]

    description = request.form.get(
        "description"
    )

    website = request.form.get(
        "website"
    )

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO companies
            (name, description, website)
            VALUES
            (%s, %s, %s)
            """,
            (
                name,
                description,
                website
            )
        )

        connection.commit()

    except Exception as e:

        connection.rollback()

        cursor.close()
        connection.close()

        return (
            f"Failed to add company: {e}"
        )

    cursor.close()
    connection.close()

    return redirect(
        "/admin/companies"
    )


# ============================================================
# ADMIN - MANAGE COMPANIES
# ============================================================

@app.route("/admin/companies")
def manage_companies():

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            companies.*,
            (
                SELECT COUNT(*)
                FROM jobs
                WHERE jobs.company_id = companies.id
            ) AS jobs_count
        FROM companies
        ORDER BY companies.name
        """
    )

    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "manage_companies.html",
        companies=companies
    )


# ============================================================
# ADMIN - EDIT COMPANY
# ============================================================

@app.route(
    "/admin/company/edit/<int:company_id>",
    methods=["GET", "POST"]
)
def edit_company(company_id):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    if request.method == "POST":

        name = request.form["name"]

        description = request.form.get(
            "description"
        )

        website = request.form.get(
            "website"
        )

        cursor.execute(
            """
            UPDATE companies
            SET
                name = %s,
                description = %s,
                website = %s
            WHERE id = %s
            """,
            (
                name,
                description,
                website,
                company_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            "/admin/companies"
        )

    cursor.execute(
        """
        SELECT *
        FROM companies
        WHERE id = %s
        """,
        (company_id,)
    )

    company = cursor.fetchone()

    cursor.close()
    connection.close()

    if company is None:

        return (
            "Company not found",
            404
        )

    return render_template(
        "edit_company.html",
        company=company
    )


# ============================================================
# ADMIN - DELETE COMPANY
# ============================================================

@app.route(
    "/admin/company/delete/<int:company_id>",
    methods=["POST"]
)
def delete_company(company_id):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM companies
            WHERE id = %s
            """,
            (company_id,)
        )

        connection.commit()

    except Exception as e:

        connection.rollback()

        cursor.close()
        connection.close()

        return (
            "Failed to delete company. Remove its jobs "
            f"first, or check for related records: {e}"
        )

    cursor.close()
    connection.close()

    return redirect(
        "/admin/companies"
    )


# ============================================================
# ADMIN - ADD JOB
# ============================================================

@app.route(
    "/admin/job/add",
    methods=["GET", "POST"]
)
def add_job():

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    if request.method == "POST":

        company_id = request.form[
            "company_id"
        ]

        title = request.form[
            "title"
        ]

        description = request.form[
            "description"
        ]

        education = request.form[
            "education"
        ]

        required_skills = request.form[
            "required_skills"
        ]

        recommended_qualities = request.form[
            "recommended_qualities"
        ]

        preferred_qualities = request.form[
            "preferred_qualities"
        ]

        experience = request.form[
            "experience"
        ]

        certifications = request.form[
            "certifications"
        ]

        location = request.form[
            "location"
        ]

        job_type = request.form[
            "job_type"
        ]

        ctc = request.form[
            "ctc"
        ]

        stipend = request.form[
            "stipend"
        ]

        deadline = (
            request.form["deadline"]
            or None
        )

        cursor.execute(
            """
            INSERT INTO jobs (
                company_id,
                title,
                description,
                education,
                required_skills,
                recommended_qualities,
                preferred_qualities,
                experience,
                certifications,
                location,
                job_type,
                ctc,
                stipend,
                deadline
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                company_id,
                title,
                description,
                education,
                required_skills,
                recommended_qualities,
                preferred_qualities,
                experience,
                certifications,
                location,
                job_type,
                ctc,
                stipend,
                deadline
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            "/admin/jobs"
        )

    cursor.execute(
        """
        SELECT id, name
        FROM companies
        ORDER BY name
        """
    )

    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_job.html",
        companies=companies
    )


# ============================================================
# ADMIN - MANAGE JOBS
# ============================================================

@app.route("/admin/jobs")
def manage_jobs():

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            jobs.*,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        ORDER BY jobs.created_at DESC
        """
    )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "manage_jobs.html",
        jobs=jobs
    )


# ============================================================
# ADMIN - EDIT JOB
# ============================================================

@app.route(
    "/admin/job/edit/<int:job_id>",
    methods=["GET", "POST"]
)
def edit_job(job_id):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    if request.method == "POST":

        company_id = request.form[
            "company_id"
        ]

        title = request.form[
            "title"
        ]

        description = request.form[
            "description"
        ]

        education = request.form[
            "education"
        ]

        required_skills = request.form[
            "required_skills"
        ]

        recommended_qualities = request.form[
            "recommended_qualities"
        ]

        preferred_qualities = request.form[
            "preferred_qualities"
        ]

        experience = request.form[
            "experience"
        ]

        certifications = request.form[
            "certifications"
        ]

        location = request.form[
            "location"
        ]

        job_type = request.form[
            "job_type"
        ]

        ctc = request.form[
            "ctc"
        ]

        stipend = request.form[
            "stipend"
        ]

        deadline = (
            request.form["deadline"]
            or None
        )

        cursor.execute(
            """
            UPDATE jobs
            SET
                company_id = %s,
                title = %s,
                description = %s,
                education = %s,
                required_skills = %s,
                recommended_qualities = %s,
                preferred_qualities = %s,
                experience = %s,
                certifications = %s,
                location = %s,
                job_type = %s,
                ctc = %s,
                stipend = %s,
                deadline = %s
            WHERE id = %s
            """,
            (
                company_id,
                title,
                description,
                education,
                required_skills,
                recommended_qualities,
                preferred_qualities,
                experience,
                certifications,
                location,
                job_type,
                ctc,
                stipend,
                deadline,
                job_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            "/admin/jobs"
        )

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = %s
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    if job is None:

        cursor.close()
        connection.close()

        return (
            "Job not found",
            404
        )

    cursor.execute(
        """
        SELECT id, name
        FROM companies
        ORDER BY name
        """
    )

    companies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_job.html",
        job=job,
        companies=companies
    )


# ============================================================
# ADMIN - DELETE JOB
# ============================================================

@app.route(
    "/admin/job/delete/<int:job_id>",
    methods=["POST"]
)
def delete_job(job_id):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM jobs
            WHERE id = %s
            """,
            (job_id,)
        )

        connection.commit()

    except Exception as e:

        connection.rollback()

        cursor.close()
        connection.close()

        return (
            f"Failed to delete job: {e}"
        )

    cursor.close()
    connection.close()

    return redirect(
        "/admin/jobs"
    )


# ============================================================
# ADMIN - APPLICATIONS
# ============================================================

@app.route("/admin/applications")
def admin_applications():

    if session.get("role") != "admin":
        return redirect("/login")

    page = request.args.get("page", 1, type=int)

    # Optional filters — filter applications down to one company
    # and/or one specific job posting.
    company_filter = request.args.get("company_id", type=int)
    job_filter = request.args.get("job_id", type=int)

    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    where_clauses = []
    where_params = []

    if company_filter:
        where_clauses.append("c.id = %s")
        where_params.append(company_filter)

    if job_filter:
        where_clauses.append("j.id = %s")
        where_params.append(job_filter)

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Total number of applications matching the current filters
    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.id
        JOIN companies c
            ON j.company_id = c.id
        {where_sql}
    """, tuple(where_params))

    total_applications = cursor.fetchone()["total"]

    total_pages = (
        (total_applications + per_page - 1)
        // per_page
    )

    # Only fetch the applications required for this page
    cursor.execute(f"""
        SELECT
            a.id AS application_id,
            s.name AS student_name,
            s.university_roll_no AS roll_no,
            a.status,
            j.title AS job_title,
            c.name AS company_name
        FROM applications a
        JOIN students s
            ON a.student_id = s.id
        JOIN jobs j
            ON a.job_id = j.id
        JOIN companies c
            ON j.company_id = c.id
        {where_sql}
        ORDER BY a.id DESC
        LIMIT %s OFFSET %s
    """, tuple(where_params) + (per_page, offset))

    applications = cursor.fetchall()

    # Companies + jobs to populate the filter dropdowns
    cursor.execute("""
        SELECT id, name
        FROM companies
        ORDER BY name
    """)

    filter_companies = cursor.fetchall()

    cursor.execute("""
        SELECT
            jobs.id,
            jobs.title,
            jobs.company_id,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        ORDER BY companies.name, jobs.title
    """)

    filter_jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_applications.html",
        applications=applications,
        page=page,
        total_pages=total_pages,
        filter_companies=filter_companies,
        filter_jobs=filter_jobs,
        selected_company_id=company_filter,
        selected_job_id=job_filter
    )


# ============================================================
# ADMIN - APPLICATION DETAIL
# ============================================================

@app.route(
    "/admin/application/<int:application_id>"
)
def admin_application_detail(application_id):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            applications.*,
            students.name AS student_name,
            students.university_roll_no AS roll_no,
            students.college,
            students.branch,
            students.cgpa,
            students.skills,
            jobs.title AS job_title,
            companies.name AS company_name
        FROM applications
        JOIN students
            ON applications.student_id = students.id
        JOIN jobs
            ON applications.job_id = jobs.id
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE applications.id = %s
        """,
        (application_id,)
    )

    application = cursor.fetchone()

    cursor.close()
    connection.close()

    if application is None:

        return (
            "Application not found",
            404
        )

    return render_template(
        "admin_application_detail.html",
        application=application
    )


# ============================================================
# ADMIN - UPDATE APPLICATION STATUS
# ============================================================

@app.route(
    "/admin/application/status/<int:application_id>",
    methods=["POST"]
)
def update_application_status(
    application_id
):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    status = request.form[
        "status"
    ]

    next_url = request.form.get(
        "next"
    ) or "/admin/applications"

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE applications
        SET status = %s
        WHERE id = %s
        """,
        (
            status,
            application_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        next_url
    )


# ============================================================
# ADMIN - VIEW APPLICATION RESUME
# ============================================================

@app.route(
    "/admin/application/resume/<int:application_id>"
)
def view_application_resume(
    application_id
):

    if session.get("role") != "admin":

        return redirect(
            "/login"
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            resumes.file_path,
            applications.resume_consent
        FROM applications
        JOIN resumes
            ON applications.student_id =
               resumes.student_id
        WHERE applications.id = %s
        AND resumes.resume_type = 'uploaded'
        AND applications.resume_consent = TRUE
        ORDER BY resumes.uploaded_at DESC
        LIMIT 1
        """,
        (application_id,)
    )

    resume = cursor.fetchone()

    cursor.close()
    connection.close()

    if resume is None:

        return (
            "Resume cannot be accessed. "
            "The student has not provided "
            "resume consent for this application."
        ), 403

    if not os.path.exists(
        resume["file_path"]
    ):

        return (
            "Resume file not found",
            404
        )

    return send_file(
        resume["file_path"],
        as_attachment=False
    )


# ============================================================
# STUDENT - VIEW JOBS
# ============================================================

@app.route("/jobs")
def view_jobs():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    # Optional job-title search (?q=...)
    search_query = request.args.get(
        "q",
        ""
    ).strip()

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    if search_query:

        cursor.execute(
            """
            SELECT
                jobs.id,
                jobs.title,
                jobs.location,
                jobs.job_type,
                jobs.ctc,
                jobs.stipend,
                jobs.deadline,
                companies.name AS company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE jobs.title LIKE %s
            ORDER BY jobs.created_at DESC
            """,
            (f"%{search_query}%",)
        )

    else:

        cursor.execute(
            """
            SELECT
                jobs.id,
                jobs.title,
                jobs.location,
                jobs.job_type,
                jobs.ctc,
                jobs.stipend,
                jobs.deadline,
                companies.name AS company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.id
            ORDER BY jobs.created_at DESC
            """
        )

    jobs = cursor.fetchall()

    cursor.execute(
        """
        SELECT DISTINCT jobs.title
        FROM jobs
        ORDER BY jobs.title
        """
    )

    all_job_titles = [row["title"] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs,
        search_query=search_query,
        all_job_titles=all_job_titles
    )


# ============================================================
# STUDENT - JOB DETAILS
# ============================================================

@app.route(
    "/job/<int:job_id>"
)
def job_details(job_id):

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            jobs.*,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE jobs.id = %s
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    if job is None:

        cursor.close()
        connection.close()

        return (
            "Job not found",
            404
        )

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    if student is None:

        cursor.close()
        connection.close()

        return (
            "Student profile not found",
            404
        )

    student_id = student["id"]

    cursor.execute(
        """
        SELECT id
        FROM applications
        WHERE student_id = %s
        AND job_id = %s
        """,
        (
            student_id,
            job_id
        )
    )

    application = cursor.fetchone()

    already_applied = (
        application is not None
    )

    cursor.close()
    connection.close()

    return render_template(
        "job_details.html",
        job=job,
        already_applied=already_applied
    )


# ============================================================
# STUDENT - APPLY FOR JOB
# ============================================================

@app.route(
    "/job/<int:job_id>/apply",
    methods=["GET", "POST"]
)
def apply_job(job_id):

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            jobs.*,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE jobs.id = %s
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    if job is None:

        cursor.close()
        connection.close()

        return (
            "Job not found",
            404
        )

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    if student is None:

        cursor.close()
        connection.close()

        return (
            "Student profile not found",
            404
        )

    student_id = student["id"]

    cursor.execute(
        """
        SELECT id
        FROM applications
        WHERE student_id = %s
        AND job_id = %s
        """,
        (
            student_id,
            job_id
        )
    )

    existing_application = (
        cursor.fetchone()
    )

    if existing_application:

        cursor.close()
        connection.close()

        return redirect(
            f"/job/{job_id}"
        )

    if request.method == "GET":

        cursor.close()
        connection.close()

        return render_template(
            "application_questionnaire.html",
            job=job
        )

    pwd_status = request.form.get(
        "pwd_status"
    )

    indian_resident_status = request.form.get(
        "indian_resident_status"
    )

    known_in_company = request.form.get(
        "known_in_company"
    )

    known_person_details = request.form.get(
        "known_person_details"
    )

    languages = request.form.getlist(
        "languages[]"
    )

    language_proficiencies = []

    for i, language in enumerate(
        languages
    ):

        proficiency = request.form.get(
            f"proficiency_{i}"
        )

        if language and proficiency:

            language_proficiencies.append(
                f"{language} - {proficiency}"
            )

    languages_known = ", ".join(
        languages
    )

    language_proficiency = "\n".join(
        language_proficiencies
    )

    application_consent = request.form.get(
        "application_consent"
    )

    resume_consent = request.form.get(
        "resume_consent"
    )

    if application_consent != "yes":

        cursor.close()
        connection.close()

        return (
            "Application consent is required."
        )

    if resume_consent != "yes":

        cursor.close()
        connection.close()

        return (
            "Resume usage consent is required."
        )

    try:

        cursor.execute(
            """
            INSERT INTO applications
            (
                student_id,
                job_id,
                status,
                pwd_status,
                indian_resident_status,
                known_in_company,
                known_person_details,
                languages_known,
                language_proficiency,
                application_consent,
                resume_consent
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                student_id,
                job_id,
                "Applied",
                pwd_status,
                indian_resident_status,
                known_in_company,
                known_person_details,
                languages_known,
                language_proficiency,
                True,
                True
            )
        )

        connection.commit()

    except Exception as e:

        connection.rollback()

        cursor.close()
        connection.close()

        return (
            f"Failed to submit application: {e}"
        )

    cursor.close()
    connection.close()

    return redirect(
        f"/job/{job_id}"
    )


# ============================================================
# STUDENT - MY APPLICATIONS / JOB STATUS
# ============================================================

@app.route("/student/applications")
def student_applications():

    if session.get("role") != "student":

        return redirect(
            "/login"
        )

    user_id = session["user_id"]

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = %s
        """,
        (user_id,)
    )

    student = cursor.fetchone()

    if student is None:

        cursor.close()
        connection.close()

        return (
            "Student profile not found",
            404
        )

    cursor.execute(
        """
        SELECT
            applications.id,
            applications.status,
            jobs.id AS job_id,
            jobs.title AS job_title,
            jobs.location,
            jobs.job_type,
            jobs.deadline,
            companies.name AS company_name
        FROM applications
        JOIN jobs
            ON applications.job_id = jobs.id
        JOIN companies
            ON jobs.company_id = companies.id
        WHERE applications.student_id = %s
        ORDER BY applications.id DESC
        """,
        (student["id"],)
    )

    applications = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_applications.html",
        applications=applications
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
    