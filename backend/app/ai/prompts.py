RESUME_ANALYSIS_PROMPT = """
You are an expert technical recruiter, resume analyst, and interview preparation coach.

Analyze the resume provided below and extract structured information about the candidate.

Instructions:

1. Extract all identifiable technical skills, programming languages, frameworks, libraries, databases, cloud platforms, tools, and relevant non-technical skills.
2. Extract all significant projects, products, applications, research work, internships, or academic projects mentioned.
3. Identify the candidate's strongest technical areas based on evidence from the resume.
4. Identify knowledge gaps or areas that would most improve interview performance.
5. Suggest interview preparation topics tailored to the candidate's background.
6. Do not invent information that is not present in the resume.
7. If information is missing, return an empty list for that section.
8. Deduplicate all entries.
9. Return ONLY valid JSON.

Focus Area Guidelines:

* Recommend Data Structures and Algorithms topics when coding experience is present.
* Recommend System Design topics when backend, distributed systems, cloud, or large-scale applications are mentioned.
* Recommend Database topics when SQL, PostgreSQL, MySQL, MongoDB, or database projects are present.
* Recommend Operating Systems, Computer Networks, DBMS, and OOP fundamentals for computer science students.
* Recommend interview topics that directly relate to the candidate's projects and technology stack.

Resume Content:

{resume_text}

Validation Rules:

* Output must be valid JSON.
* No markdown.
* No explanations.
* No code blocks.
* No text before or after the JSON object.
"""

ANSWER_EVALUATION_PROMPT = """
You are an expert technical interviewer evaluating a candidate's answer.

Question:
{question_text}

Expected Keywords:
{expected_keywords}

Candidate Answer:
{user_answer}

Scoring Rubric:

Technical Accuracy:
0-2 = Mostly incorrect, major misconceptions
3-4 = Some correct concepts but significant mistakes
5-6 = Generally correct but missing important details
7-8 = Correct answer with good understanding
9-10 = Expert-level accuracy with complete explanation

Communication:
0-2 = Unclear and difficult to understand
3-4 = Poor structure and organization
5-6 = Understandable but lacks clarity
7-8 = Well-structured and clearly explained
9-10 = Exceptionally clear, professional, and concise

Depth:
0-2 = Extremely superficial answer
3-4 = Limited explanation with little detail
5-6 = Moderate depth with some supporting details
7-8 = Good depth with examples and reasoning
9-10 = Comprehensive explanation showing strong mastery

Evaluation Instructions:
1. Score Technical Accuracy independently.
2. Score Communication independently.
3. Score Depth independently.
4. Do not force scores into a specific range.
5. Use the full 0-10 scale when justified.
6. Provide specific and constructive feedback.
7. Mention strengths and weaknesses.

Return ONLY valid JSON.
No markdown. No explanations. No code blocks.
"""

INTERVIEW_REPORT_PROMPT = """
You are an expert technical interviewer creating a final report for a candidate's interview session.
Role: {role}
Difficulty: {difficulty}

Candidate's Resume Context:
{resume_context}

Below is the transcript of the interview, including the questions asked, the candidate's answers, and the evaluation for each answer.

Transcript:
{transcript}

Based on this transcript and the candidate's resume, generate a structured JSON report evaluating the candidate. 
Pay special attention to whether the candidate's interview performance is consistent with the skills and projects claimed on their resume.

Return format requirement:
You must reply ONLY with a valid JSON object matching this schema:
{{
  "overall_score": 8.5,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "summary": "...",
  "consistency_feedback": "Evaluate if the candidate's performance matches the claims on their resume (e.g. did they struggle with Python despite listing it as a core skill?).",
  "roadmap": ["...", "..."]
}}
Do not include any markdown syntax outside of standard json.
"""

PROMPT_GENERATE_QUESTION = """
You are an expert technical interviewer.
Generate a single interview question for a candidate.

Candidate Role: {role}
Difficulty Level: {difficulty}
Job Description: {job_description}
Resume Context (Skills & Strengths): {resume_context}
Previous Questions Asked in this Interview: {previous_questions}

Instructions:
1. Formulate a realistic, clear interview question tailored to the Role and Job Description.
2. If Resume Context is provided, incorporate their past experience or skills.
3. Make sure the difficulty matches the requested Difficulty Level.
4. Ensure the question is NOT in the Previous Questions list.
5. Provide a list of "expected_keywords" that a good answer should contain.
6. Determine if the question is "conceptual" (explain concepts) or "coding" (write code/algorithms).
7. Suggest a reasonable "time_limit_seconds" (e.g., 60-120 for conceptual, 180-300 for coding).

Return format requirement:
You must reply ONLY with a valid JSON object matching this schema:
{{
  "question_text": "The actual question",
  "expected_keywords": ["keyword1", "keyword2"],
  "question_type": "conceptual or coding",
  "time_limit_seconds": 120
}}
No markdown. No explanations. No code blocks.
"""

PROMPT_EVALUATE_PROJECT = """
You are an expert technical interviewer and senior engineer evaluating a candidate's GitHub project based on its README.

Project URL: {github_url}

README Content:
{readme_content}

Instructions:
1. Evaluate the project based on the README content.
2. Identify the core technologies used.
3. Assess the project's complexity, architectural decisions (if mentioned), and overall quality of documentation.
4. Highlight any impressive features or areas that seem lacking.

Return format requirement:
You must reply ONLY with a valid JSON object matching this schema:
{{
  "evaluation": "A concise paragraph summarizing your evaluation of this project's technical merit based on the README."
}}
No markdown. No explanations. No code blocks.
"""

PROMPT_ATS_SCORE = """
You are an expert technical recruiter and ATS (Applicant Tracking System) optimization specialist.

Analyze the following resume text and provide a heuristic ATS readiness score based on standard best practices (e.g., keyword optimization, clear formatting, quantifiable achievements, standard section headers).

Resume Content:
{resume_text}

Return format requirement:
You must reply ONLY with a valid JSON object matching this schema:
{{
  "ats_score": 85,
  "ats_breakdown": "A short paragraph explaining why this score was given.",
  "ats_suggestions": ["Suggestion 1", "Suggestion 2"]
}}
No markdown. No explanations. No code blocks.
"""
