# What changed in this redesign

## New design system
- `static/style.css` was fully rewritten (old file is still compatible in
  spirit — every class name your existing pages already used still works).
- Theme: dark navy ("ink") navigation shell, **amber accent for student
  pages**, **teal accent for admin pages** (`body.theme-admin` swaps the
  accent color), so the two roles feel like distinct control surfaces of
  one product.
- Fonts: Sora for headings, Inter for body text (Google Fonts).
- Added reusable components: stat tiles, dashboard banners, action-tile
  grids, job cards, data tables, status badges, a status timeline, and an
  application-card layout.

## Bugs fixed
- **Admin Dashboard → "Add Company"** used to link to a route that did not
  exist. It's now fully wired up.
- **Admin Applications → "View" button** used to link to a route that did
  not exist. It now opens a real application detail page.
- `register.html` had a duplicate submit button and a misplaced role
  field — cleaned up into a proper role toggle.

## New features (these did not exist before)
- **Company management**: `/admin/companies` (list), `/admin/company/add`,
  `/admin/company/edit/<id>`, `/admin/company/delete/<id>` — full CRUD.
- **Student "My Applications" page** (`/student/applications`): the job
  status tracker you asked for, with a visual timeline per application
  (Applied → Under Review → Shortlisted → Interview → Selected, or
  Rejected).
- **Admin application detail page** (`/admin/application/<id>`): shows
  full student + job context and lets the admin change status from one
  place.
- **`/student/resume/view`**: lets a student view their own uploaded
  resume (the profile page already linked to this, but the route was
  missing).
- Both dashboards now show real stats (profile completeness, resume
  status, application counts for students; company/job/application counts
  for admins) instead of a bare list of links.

## What was left alone
The AI logic (`ai/resume_analyzer.py`, `ai/resume_writer.py`, `rag/`),
the resume-to-PDF generation, and the database schema were not touched —
they were already solid. Only navigation and surrounding markup were
updated on the large functional pages (`analyzer.html`, `generator.html`,
`analysis_result.html`, `application_questionnaire.html`) to keep the new
look consistent without risking their working JS.

## Before you demo it
- Make sure your `companies` table has `description` and `website`
  columns (the add/edit company forms use them) — add them if they're
  missing:
  ```sql
  ALTER TABLE companies ADD COLUMN description TEXT;
  ALTER TABLE companies ADD COLUMN website VARCHAR(255);
  ```
- Since templates now reference Google Fonts via `@import` in
  `style.css`, the machine you demo on needs internet access for the
  fonts to load (it still looks fine without it — it just falls back to
  system fonts).
