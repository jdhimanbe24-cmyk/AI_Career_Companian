-- Postgres schema for Render deployment (translated from schema_mysql_dump.sql).
-- Run order respects foreign key dependencies.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    university_roll_no VARCHAR(30) UNIQUE,
    phone VARCHAR(20),
    college VARCHAR(255),
    degree VARCHAR(255),
    branch VARCHAR(255),
    cgpa NUMERIC(4,2),
    graduation_year INTEGER,
    skills TEXT,
    projects TEXT,
    certifications TEXT,
    experience TEXT,
    preferred_role VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    education TEXT,
    required_skills TEXT,
    recommended_qualities TEXT,
    preferred_qualities TEXT,
    experience TEXT,
    certifications TEXT,
    location VARCHAR(255),
    job_type VARCHAR(100),
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ctc VARCHAR(100),
    stipend VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'Applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pwd_status VARCHAR(50),
    indian_resident_status VARCHAR(50),
    known_in_company VARCHAR(10),
    known_person_details TEXT,
    languages_known TEXT,
    language_proficiency TEXT,
    application_consent BOOLEAN DEFAULT FALSE,
    resume_consent BOOLEAN DEFAULT FALSE,
    UNIQUE (student_id, job_id)
);

CREATE TABLE IF NOT EXISTS job_matches (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    match_score NUMERIC(5,2),
    matched_skills TEXT,
    missing_skills TEXT,
    matched_qualities TEXT,
    missing_qualities TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, job_id)
);

CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    resume_type VARCHAR(20) DEFAULT 'uploaded' CHECK (resume_type IN ('uploaded', 'generated')),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resume_analysis (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    job_id INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    overall_score NUMERIC(5,2),
    technical_skills_score NUMERIC(5,2),
    projects_score NUMERIC(5,2),
    education_score NUMERIC(5,2),
    certifications_score NUMERIC(5,2),
    experience_score NUMERIC(5,2),
    keywords_score NUMERIC(5,2),
    eligibility_status VARCHAR(100),
    analysis_result JSONB,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MySQL's `ON UPDATE CURRENT_TIMESTAMP` (on students.updated_at) has no
-- direct Postgres equivalent, so replicate it with a trigger.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_students_updated_at ON students;
CREATE TRIGGER trg_students_updated_at
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
