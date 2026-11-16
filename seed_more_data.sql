-- =============================================================================
-- AI Career & Placement Companion — additional demo data
-- =============================================================================
-- Adds: 8 real-world companies, 16 jobs across all 4 supported roles,
-- 5 student accounts with distinct skill profiles (+ resumes), and 8 sample
-- applications so the tracker / admin review screens have real content.
--
-- HOW TO RUN
--   mysql -u <your_db_user> -p <your_db_name> < seed_more_data.sql
-- (or paste the contents into MySQL Workbench / phpMyAdmin / TablePlus)
--
-- This only INSERTs new rows — it does not touch or delete anything you
-- already have. Run it once against the same database your .env points at.
--
-- Student login password for ALL 5 new accounts: Student@123
-- (hashes below are real werkzeug scrypt hashes generated with the same
-- Werkzeug version pinned in requirements.txt, so check_password_hash()
-- in app.py will accept them as-is.)
--
-- Resume files: copy the /resumes folder that shipped alongside this SQL
-- file into your project's uploads/resumes/ folder before running the
-- INSERT statements below (or after — the app only reads the file when a
-- resume is opened, so order doesn't matter, just make sure the folder
-- exists at:  <project_root>/uploads/resumes/
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. Make sure companies has the columns the admin add/edit-company forms use.
--    Safe to skip (or ignore the error) if you already ran this from CHANGES.md.
-- -----------------------------------------------------------------------------
-- ALTER TABLE companies ADD COLUMN description TEXT;
-- ALTER TABLE companies ADD COLUMN website VARCHAR(255);


-- -----------------------------------------------------------------------------
-- 1. COMPANIES (8 real, recognizable recruiters)
-- -----------------------------------------------------------------------------
INSERT INTO companies (name, description, website) VALUES
('Google India', 'Global technology company building search, cloud and AI products; hires strong problem-solvers across SWE, AI/ML and infrastructure roles.', 'https://careers.google.com'),
('Microsoft India', 'Enterprise software and cloud platform company (Azure, Microsoft 365); large campus hiring across engineering and data roles.', 'https://careers.microsoft.com'),
('Amazon India', 'E-commerce and cloud computing (AWS) company; high-volume campus hiring for SDE and Data roles with strong PPO conversion.', 'https://www.amazon.jobs'),
('Tata Consultancy Services (TCS)', 'India\'s largest IT services company, hiring engineering graduates at scale across software development and digital roles.', 'https://www.tcs.com/careers'),
('Infosys', 'Global IT services and consulting company known for structured graduate hiring programs (Systems Engineer, Specialist Programmer).', 'https://www.infosys.com/careers'),
('Wipro', 'IT services and consulting company hiring engineering graduates for software development and emerging technology roles.', 'https://careers.wipro.com'),
('Zoho Corporation', 'Product-based software company building its own SaaS suite end-to-end; known for strong engineering + web development hiring.', 'https://www.zoho.com/careers'),
('Razorpay', 'Fintech company building payments and banking infrastructure for businesses; hires for high-ownership engineering roles.', 'https://razorpay.com/jobs');


-- -----------------------------------------------------------------------------
-- 2. JOBS (16 openings spanning all 4 roles the platform's RAG/analyzer supports)
-- -----------------------------------------------------------------------------
INSERT INTO jobs (company_id, title, description, education, required_skills, recommended_qualities, preferred_qualities, experience, certifications, location, job_type, ctc, stipend, deadline) VALUES
((SELECT id FROM companies WHERE name = 'Google India' LIMIT 1),
 'Software Engineer Intern', 'Work on core product teams building large-scale, high-availability systems used by billions of users.',
 'B.Tech/B.E in CS/IT, final year', 'C++, Python, Java, Data Structures, Algorithms, OOP, Git',
 'Strong problem-solving, clear communication', 'Prior open-source or competitive programming experience',
 '0-1 years', 'Not mandatory', 'Bengaluru', 'Internship', '32 LPA (on PPO conversion)', '1,10,000/month', '2026-11-20'),

((SELECT id FROM companies WHERE name = 'Google India' LIMIT 1),
 'AI/ML Engineer', 'Design and ship machine learning models powering search ranking and recommendation systems.',
 'B.Tech/M.Tech in CS/AI/DS', 'Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, SQL',
 'Strong math/stats foundation, research mindset', 'Published paper or Kaggle experience',
 '0-2 years', 'Not mandatory', 'Bengaluru', 'Full-time', '28 LPA', '-', '2026-12-05'),

((SELECT id FROM companies WHERE name = 'Microsoft India' LIMIT 1),
 'Software Engineer', 'Build and maintain services for Microsoft 365 and Azure-hosted products.',
 'B.Tech/B.E in CS/IT', 'C++, Java, Data Structures, Algorithms, DBMS, SQL, Git',
 'Ownership mindset, collaborative attitude', 'Cloud (Azure) exposure',
 '0-2 years', 'Not mandatory', 'Hyderabad', 'Full-time', '24 LPA', '-', '2026-11-25'),

((SELECT id FROM companies WHERE name = 'Microsoft India' LIMIT 1),
 'Data Scientist', 'Analyze large-scale product telemetry to guide feature and business decisions.',
 'B.Tech/M.Tech in CS/Statistics/DS', 'Python, Machine Learning, Statistics, Pandas, SQL, Data Visualization',
 'Strong analytical thinking, storytelling with data', 'Power BI or Tableau experience',
 '0-2 years', 'Not mandatory', 'Hyderabad', 'Full-time', '22 LPA', '-', '2026-12-10'),

((SELECT id FROM companies WHERE name = 'Amazon India' LIMIT 1),
 'SDE Intern', 'Build customer-facing and backend services within a two-pizza team, with strong PPO track record.',
 'B.Tech/B.E in CS/IT, pre-final or final year', 'Java, Python, Data Structures, Algorithms, OOP, SQL, Git',
 'Bias for action, ability to work independently', 'AWS exposure',
 '0-1 years', 'Not mandatory', 'Bengaluru', 'Internship', '24 LPA (on PPO conversion)', '80,000/month', '2026-11-15'),

((SELECT id FROM companies WHERE name = 'Amazon India' LIMIT 1),
 'Data Scientist', 'Build forecasting and optimization models supporting Amazon\'s logistics and retail operations.',
 'B.Tech/M.Tech in CS/Statistics/DS', 'Python, Machine Learning, Statistics, Pandas, NumPy, SQL, Scikit-learn',
 'Strong quantitative background', 'Experience with large-scale datasets',
 '0-2 years', 'Not mandatory', 'Bengaluru', 'Full-time', '20 LPA', '-', '2026-12-01'),

((SELECT id FROM companies WHERE name = 'Tata Consultancy Services (TCS)' LIMIT 1),
 'Software Engineer - TCS Digital', 'Work on digital transformation projects for global enterprise clients across domains.',
 'B.Tech/B.E in any engineering branch', 'Java, Python, DBMS, SQL, OOP, Git',
 'Adaptability, client communication skills', 'Prior internship experience',
 '0-1 years', 'Not mandatory', 'Pune', 'Full-time', '9.5 LPA', '-', '2026-10-31'),

((SELECT id FROM companies WHERE name = 'Tata Consultancy Services (TCS)' LIMIT 1),
 'Web Developer', 'Develop and maintain client-facing web applications for enterprise customers.',
 'B.Tech/B.E/BCA/MCA', 'HTML, CSS, JavaScript, React, SQL, Git, REST API',
 'Attention to detail, willingness to learn new stacks', 'Node.js experience',
 '0-1 years', 'Not mandatory', 'Chennai', 'Full-time', '6.5 LPA', '-', '2026-11-05'),

((SELECT id FROM companies WHERE name = 'Infosys' LIMIT 1),
 'Specialist Programmer - Software Engineer', 'Fast-track engineering role building products for Infosys\' digital and platform units.',
 'B.Tech/B.E in CS/IT with strong coding ability', 'Java, Python, Data Structures, Algorithms, DBMS, SQL',
 'Strong coding assessment performance', 'Open-source contributions',
 '0-1 years', 'Not mandatory', 'Mysuru', 'Full-time', '9 LPA', '-', '2026-10-25'),

((SELECT id FROM companies WHERE name = 'Infosys' LIMIT 1),
 'Data Scientist', 'Support analytics engagements for Infosys enterprise clients across industries.',
 'B.Tech/M.Tech in CS/DS/Statistics', 'Python, Machine Learning, Pandas, NumPy, SQL, Data Visualization',
 'Client-facing communication, analytical rigor', 'Domain knowledge in BFSI or retail',
 '0-2 years', 'Not mandatory', 'Bengaluru', 'Full-time', '12 LPA', '-', '2026-11-30'),

((SELECT id FROM companies WHERE name = 'Wipro' LIMIT 1),
 'Web Developer', 'Build and maintain web applications for Wipro\'s enterprise and product engineering clients.',
 'B.Tech/B.E/BCA', 'HTML, CSS, JavaScript, React, Node.js, Git',
 'Team collaboration, willingness to work across the stack', 'REST API design experience',
 '0-1 years', 'Not mandatory', 'Bengaluru', 'Full-time', '6.5 LPA', '-', '2026-11-10'),

((SELECT id FROM companies WHERE name = 'Wipro' LIMIT 1),
 'AI/ML Engineer', 'Build ML-driven automation features for Wipro\'s enterprise AI platform.',
 'B.Tech/M.Tech in CS/AI/DS', 'Python, Machine Learning, TensorFlow, Pandas, SQL, Docker',
 'Curiosity, structured experimentation', 'MLOps exposure',
 '0-2 years', 'Not mandatory', 'Pune', 'Full-time', '10 LPA', '-', '2026-12-08'),

((SELECT id FROM companies WHERE name = 'Zoho Corporation' LIMIT 1),
 'Web Developer', 'Build features across Zoho\'s in-house SaaS product suite, end-to-end from UI to backend.',
 'B.Tech/B.E/BCA/MCA (any recognized degree accepted)', 'HTML, CSS, JavaScript, React, Node.js, SQL, Git, REST API',
 'Product thinking, ownership of full feature lifecycle', 'Experience building a complete personal project',
 '0-1 years', 'Not mandatory', 'Chennai', 'Full-time', '8 LPA', '-', '2026-11-18'),

((SELECT id FROM companies WHERE name = 'Zoho Corporation' LIMIT 1),
 'Software Engineer Intern', 'Contribute to Zoho\'s core product engineering teams during a paid internship with PPO potential.',
 'B.Tech/B.E in CS/IT, pre-final or final year', 'Java, Python, Data Structures, Algorithms, DBMS',
 'Strong fundamentals, product sense', 'Personal or open-source projects',
 '0-1 years', 'Not mandatory', 'Chennai', 'Internship', '8 LPA (on PPO conversion)', '20,000/month', '2026-11-22'),

((SELECT id FROM companies WHERE name = 'Razorpay' LIMIT 1),
 'Software Engineer', 'Build reliable, secure payments infrastructure used by hundreds of thousands of businesses.',
 'B.Tech/B.E in CS/IT', 'Java, Python, Data Structures, Algorithms, DBMS, SQL, Git',
 'High ownership, attention to reliability and security', 'Fintech or distributed-systems exposure',
 '0-2 years', 'Not mandatory', 'Bengaluru', 'Full-time', '18 LPA', '-', '2026-12-12'),

((SELECT id FROM companies WHERE name = 'Razorpay' LIMIT 1),
 'AI/ML Engineer Intern', 'Work on fraud detection and risk models for Razorpay\'s payments platform.',
 'B.Tech in CS/AI/DS, pre-final or final year', 'Python, Machine Learning, Pandas, NumPy, SQL',
 'Analytical rigor, curiosity about fraud/risk patterns', 'Kaggle or hackathon experience',
 '0-1 years', 'Not mandatory', 'Bengaluru', 'Internship', '-', '50,000/month', '2026-11-28');


-- -----------------------------------------------------------------------------
-- 3. STUDENT USERS + PROFILES (5 accounts, each with a distinct skill profile)
--    Login password for all of them: Student@123
-- -----------------------------------------------------------------------------

-- 3a. Rohan Mehta — Software Engineer profile
INSERT INTO users (email, password, role) VALUES
('rohan.mehta@nit.edu.in', 'scrypt:32768:8:1$5jJby0iMMzAFIKUJ$35626cbc0dae0dbb8f948fb7607e037aa6a5d731d37406377d1f87362e0c37f745069497386f51b4e715707d30b2af0a219bfd2ff0ed64d91ee4682bdcc0cf7f', 'student');
SET @rohan_user_id = LAST_INSERT_ID();
INSERT INTO students (user_id, name, phone, college, degree, branch, cgpa, graduation_year, skills, projects, certifications, experience, preferred_role, university_roll_no) VALUES
(@rohan_user_id, 'Rohan Mehta', '9812345601', 'National Institute of Technology', 'B.Tech', 'Computer Science',
 '8.4', '2026', 'C++, Python, Java, Data Structures, Algorithms, OOP, DBMS, SQL, Git, Operating Systems',
 'Library Management System (Java, MySQL, Swing); Pathfinding Visualizer (C++, SFML)',
 'NPTEL - Data Structures and Algorithms (Elite, IIT Madras)',
 'Core member, campus Competitive Coding Club', 'Software Engineer', '21CSE034');
SET @rohan_student_id = LAST_INSERT_ID();
INSERT INTO resumes (student_id, file_name, file_path, resume_type) VALUES
(@rohan_student_id, 'Rohan_Mehta_Resume.pdf', 'uploads/resumes/resume_rohan_mehta_software_engineer.pdf', 'uploaded');

-- 3b. Sneha Iyer — AI/ML Engineer profile
INSERT INTO users (email, password, role) VALUES
('sneha.iyer@iot.edu.in', 'scrypt:32768:8:1$iHdG8jq1zDnlRUHd$1cb95d779265801612783d49eea02047571cc970d4d95f646dd10a5573b5d9bcc90e74aa9317482d5b13ce8d897b517f8572330ca3c5e0a61f3cdd55f70afe92', 'student');
SET @sneha_user_id = LAST_INSERT_ID();
INSERT INTO students (user_id, name, phone, college, degree, branch, cgpa, graduation_year, skills, projects, certifications, experience, preferred_role, university_roll_no) VALUES
(@sneha_user_id, 'Sneha Iyer', '9812345602', 'Institute of Technology', 'B.Tech', 'Artificial Intelligence & Data Science',
 '8.9', '2027', 'Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, Pandas, NumPy, SQL, Docker, MLOps, Git',
 'Image Classification with CNNs (PyTorch); Campus Chatbot using Transformers (HuggingFace, Flask)',
 'DeepLearning.AI - Deep Learning Specialization (Coursera)',
 'ML Intern, campus AI Research Lab', 'AI/ML Engineer', '23AID021');
SET @sneha_student_id = LAST_INSERT_ID();
INSERT INTO resumes (student_id, file_name, file_path, resume_type) VALUES
(@sneha_student_id, 'Sneha_Iyer_Resume.pdf', 'uploads/resumes/resume_sneha_iyer_ai_ml_engineer.pdf', 'uploaded');

-- 3c. Aditya Rao — Data Scientist profile
INSERT INTO users (email, password, role) VALUES
('aditya.rao@nit.edu.in', 'scrypt:32768:8:1$50aKzttPfvyX4GH7$24eb00a6150922934a0b3365ccb8510e0fd9f2411acf6382f1559806048aa02aca24560b97e62d40a712dae975ec61c75fcb56162b231606db9ce14464c2c453', 'student');
SET @aditya_user_id = LAST_INSERT_ID();
INSERT INTO students (user_id, name, phone, college, degree, branch, cgpa, graduation_year, skills, projects, certifications, experience, preferred_role, university_roll_no) VALUES
(@aditya_user_id, 'Aditya Rao', '9812345603', 'National Institute of Technology', 'B.Tech', 'Computer Science',
 '8.6', '2026', 'Python, Machine Learning, Statistics, Pandas, NumPy, Matplotlib, SQL, Scikit-learn, Data Visualization, Deep Learning',
 'Retail Sales Forecasting (XGBoost); Customer Churn Analysis (Scikit-learn, Matplotlib)',
 'IBM Data Science Professional Certificate (Coursera)',
 'Data Analyst Intern, college placement cell', 'Data Scientist', '21CSE099');
SET @aditya_student_id = LAST_INSERT_ID();
INSERT INTO resumes (student_id, file_name, file_path, resume_type) VALUES
(@aditya_student_id, 'Aditya_Rao_Resume.pdf', 'uploads/resumes/resume_aditya_rao_data_scientist.pdf', 'uploaded');

-- 3d. Kavya Reddy — Web Developer profile
INSERT INTO users (email, password, role) VALUES
('kavya.reddy@iot.edu.in', 'scrypt:32768:8:1$6knyjpsij2t5JF5I$0a45582478417d2c4d35e62c76a0f2e4c9d334ddf8d63c11e1818ca142f1d3cd43cd7fec74e26c741c13177539aee95ff5acf83f3635f9bb9dbc75b968ac3aeb', 'student');
SET @kavya_user_id = LAST_INSERT_ID();
INSERT INTO students (user_id, name, phone, college, degree, branch, cgpa, graduation_year, skills, projects, certifications, experience, preferred_role, university_roll_no) VALUES
(@kavya_user_id, 'Kavya Reddy', '9812345604', 'Institute of Technology', 'B.Tech', 'Information Technology',
 '8.2', '2026', 'HTML, CSS, JavaScript, React, Node.js, SQL, Git, REST API',
 'Campus Event Portal (React, Node.js, Express, MongoDB); Personal Portfolio & Blog (HTML, CSS, JS, REST API)',
 'Meta Front-End Developer Professional Certificate (Coursera)',
 'Freelance web developer - 2 small business websites', 'Web Developer', '21ITE045');
SET @kavya_student_id = LAST_INSERT_ID();
INSERT INTO resumes (student_id, file_name, file_path, resume_type) VALUES
(@kavya_student_id, 'Kavya_Reddy_Resume.pdf', 'uploads/resumes/resume_kavya_reddy_web_developer.pdf', 'uploaded');

-- 3e. Arjun Singh — entry-level / fresher profile (weaker skill match, for contrast)
INSERT INTO users (email, password, role) VALUES
('arjun.singh@nit.edu.in', 'scrypt:32768:8:1$aDNaSjOJwOgEfpB0$2e818e280416e889e79c7e7635264fe4560e3c6b92e1ff5a783203fb906e3c2421e1e7e930b46a0ff2cfd00060c842cebf59da78524d172080370efcb02740ab', 'student');
SET @arjun_user_id = LAST_INSERT_ID();
INSERT INTO students (user_id, name, phone, college, degree, branch, cgpa, graduation_year, skills, projects, certifications, experience, preferred_role, university_roll_no) VALUES
(@arjun_user_id, 'Arjun Singh', '9812345605', 'National Institute of Technology', 'B.Tech', 'Computer Science',
 '7.1', '2026', 'C, Python, Basic SQL',
 'Simple Calculator App (Python)',
 '', '', 'Software Engineer', '21CSE156');
SET @arjun_student_id = LAST_INSERT_ID();
INSERT INTO resumes (student_id, file_name, file_path, resume_type) VALUES
(@arjun_student_id, 'Arjun_Singh_Resume.pdf', 'uploads/resumes/resume_arjun_singh_fresher.pdf', 'uploaded');


-- -----------------------------------------------------------------------------
-- 4. SAMPLE APPLICATIONS (so /student/applications and /admin/applications
--    have varied, realistic content across every status)
-- -----------------------------------------------------------------------------

INSERT INTO applications (student_id, job_id, status, pwd_status, indian_resident_status, known_in_company, known_person_details, languages_known, language_proficiency, application_consent, resume_consent) VALUES
(@rohan_student_id, (SELECT id FROM jobs WHERE title = 'Software Engineer Intern' AND company_id = (SELECT id FROM companies WHERE name = 'Google India') LIMIT 1),
 'Interview', 'No', 'Yes', 'No', '', 'English, Hindi', 'English - Fluent\nHindi - Native', 1, 1),

(@rohan_student_id, (SELECT id FROM jobs WHERE title = 'Software Engineer - TCS Digital' LIMIT 1),
 'Selected', 'No', 'Yes', 'No', '', 'English, Hindi', 'English - Fluent\nHindi - Native', 1, 1),

(@sneha_student_id, (SELECT id FROM jobs WHERE title = 'AI/ML Engineer' AND company_id = (SELECT id FROM companies WHERE name = 'Google India') LIMIT 1),
 'Shortlisted', 'No', 'Yes', 'No', '', 'English, Tamil', 'English - Fluent\nTamil - Native', 1, 1),

(@aditya_student_id, (SELECT id FROM jobs WHERE title = 'Data Scientist' AND company_id = (SELECT id FROM companies WHERE name = 'Amazon India') LIMIT 1),
 'Applied', 'No', 'Yes', 'No', '', 'English, Kannada', 'English - Fluent\nKannada - Native', 1, 1),

(@aditya_student_id, (SELECT id FROM jobs WHERE title = 'Data Scientist' AND company_id = (SELECT id FROM companies WHERE name = 'Infosys') LIMIT 1),
 'Under Review', 'No', 'Yes', 'No', '', 'English, Kannada', 'English - Fluent\nKannada - Native', 1, 1),

(@kavya_student_id, (SELECT id FROM jobs WHERE title = 'Web Developer' AND company_id = (SELECT id FROM companies WHERE name = 'Zoho Corporation') LIMIT 1),
 'Selected', 'No', 'Yes', 'No', '', 'English, Telugu', 'English - Fluent\nTelugu - Native', 1, 1),

(@kavya_student_id, (SELECT id FROM jobs WHERE title = 'Web Developer' AND company_id = (SELECT id FROM companies WHERE name = 'Wipro') LIMIT 1),
 'Applied', 'No', 'Yes', 'No', '', 'English, Telugu', 'English - Fluent\nTelugu - Native', 1, 1),

(@arjun_student_id, (SELECT id FROM jobs WHERE title = 'Software Engineer - TCS Digital' LIMIT 1),
 'Rejected', 'No', 'Yes', 'No', '', 'English, Hindi', 'English - Fluent\nHindi - Native', 1, 1);

-- =============================================================================
-- Done. Log in as any of the 5 students above (password: Student@123) or as
-- your existing admin account to see the new companies, jobs, resumes and
-- application statuses across every screen of the platform.
-- =============================================================================
