# Extra demo data for AI Career & Placement Companion

This adds real-world companies, more jobs, and student accounts with different
skill profiles (each with a matching resume) to your existing database —
without touching or deleting anything you already have.

## What's inside

- `seed_more_data.sql` — one SQL script that inserts:
  - **8 companies**: Google India, Microsoft India, Amazon India, TCS, Infosys,
    Wipro, Zoho Corporation, Razorpay
  - **16 jobs** spread across all 4 roles your Resume Analyzer/RAG knowledge
    base supports (Software Engineer, AI/ML Engineer, Data Scientist, Web
    Developer), with realistic CTC/stipend, location, deadlines and required
    skills for each
  - **5 student accounts**, each with a genuinely different skill profile:
    | Student | Target Role | Login Email |
    |---|---|---|
    | Rohan Mehta | Software Engineer | rohan.mehta@nit.edu.in |
    | Sneha Iyer | AI/ML Engineer | sneha.iyer@iot.edu.in |
    | Aditya Rao | Data Scientist | aditya.rao@nit.edu.in |
    | Kavya Reddy | Web Developer | kavya.reddy@iot.edu.in |
    | Arjun Singh | Software Engineer (entry-level/weaker profile, for contrast) | arjun.singh@nit.edu.in |

    **Password for all 5: `Student@123`**
  - **8 sample applications** linking these students to the new jobs, spread
    across every status (Applied, Under Review, Shortlisted, Interview,
    Selected, Rejected) so the application tracker and admin review screens
    have real content to demo.

- `resumes/` — 5 ready-made, one-page PDF resumes, one per student above,
  each written to genuinely match that student's listed skills so the
  Resume Analyzer produces a meaningfully different match/score per role.

## How to use it

1. **Copy the resume files first.** Copy everything inside `resumes/` into
   your project's `uploads/resumes/` folder:
   ```
   <your project root>/uploads/resumes/resume_rohan_mehta_software_engineer.pdf
   <your project root>/uploads/resumes/resume_sneha_iyer_ai_ml_engineer.pdf
   <your project root>/uploads/resumes/resume_aditya_rao_data_scientist.pdf
   <your project root>/uploads/resumes/resume_kavya_reddy_web_developer.pdf
   <your project root>/uploads/resumes/resume_arjun_singh_fresher.pdf
   ```
   (Create the `resumes` folder if it doesn't already exist — the `.sql`
   script points each student's resume record at this exact path.)

2. **Run the SQL script** against the same database your `.env` points at:
   ```
   mysql -u <your_db_user> -p <your_db_name> < seed_more_data.sql
   ```
   Or paste its contents into MySQL Workbench / phpMyAdmin / TablePlus and
   run it as one script (the `SET @variable = LAST_INSERT_ID()` lines need
   to run in order, in the same session, so use "run script" rather than
   running statements one at a time out of order).

3. **If this is the first time** you're adding company data, uncomment the
   two `ALTER TABLE` lines near the top of the script (they add the
   `description` and `website` columns your admin "Add Company" form uses —
   skip this step if you already ran it before, per your own `CHANGES.md`).

4. Log in as any of the 5 students (password `Student@123`) to see their
   profile, resume, and applications, or log in as your existing admin
   account to see the new companies/jobs and review the new applications.

## Why these specific companies and skills

The companies are real, recognizable campus recruiters (a mix of global
product companies, Indian IT services majors, and fintech/product
startups) so the Job Portal reads like an actual placement season rather
than placeholder data. The 4 student skill profiles map 1:1 onto the 4
roles already defined in your `ROLE_SKILLS` dictionary in `app.py` and your
`knowledge_base/*.txt` files, so when you run each resume through the
Resume Analyzer you'll see genuinely different (and genuinely earned)
match scores and skill-gap breakdowns — not four copies of the same
generic resume. The 5th profile (Arjun Singh) is intentionally weaker, to
show the analyzer handling a lower-scoring, entry-level case too.
