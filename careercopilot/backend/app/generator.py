import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_personalized_questions(retrieved_questions: list[dict], parsed_resume: dict) -> list[dict]:
    """
    Takes retrieved generic questions and the parsed resume details,
    sends them to Llama 3 via Groq to rewrite each question
    referencing the student's actual experience and projects where relevant.
    """
    # 1. Check Groq API availability
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or using placeholder. Returning original retrieved questions.")
        return [{
            "id": q["id"],
            "question": q["question"],
            "skill": q.get("skill", "General")
        } for q in retrieved_questions]

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {str(e)}")
        return [{
            "id": q["id"],
            "question": q["question"],
            "skill": q.get("skill", "General")
        } for q in retrieved_questions]

    # 2. Extract resume details for prompt construction
    skills_context = ", ".join(parsed_resume.get("skills", []))
    projects_context = "; ".join(parsed_resume.get("projects", []))
    experience_context = "; ".join(parsed_resume.get("experience", []))
    education_context = "; ".join(parsed_resume.get("education", []))

    # Format retrieved questions as a clear list
    questions_input = []
    for q in retrieved_questions:
        questions_input.append({
            "id": q["id"],
            "question": q["question"],
            "skill": q.get("skill", "")
        })

    system_prompt = (
        "You are an elite interviewer. You will receive a student's resume context "
        "(skills, projects, experiences, education) and a list of generic interview questions. "
        "Your task is to rewrite each question to reference the student's actual resume content "
        "where relevant to make it highly personalized. For example, if a question asks about React "
        "and the student's projects mention a 'weather app built with React', you should rewrite the question "
        "to ask: 'I see you built a weather app using React — walk me through how you structured the component state.' "
        "Ensure the rewritten question is natural, direct, and professional.\n\n"
        "If a question is behavioral and does not map to a specific technical skill, you can frame it "
        "referencing their work experience or projects. Keep the same core intent of the question.\n\n"
        "You MUST respond with a single, valid JSON array of objects. Absolutely nothing else. "
        "No explanations, no markdown block wraps (do NOT use ```json). Just the raw JSON.\n\n"
        "The JSON response schema must be exactly:\n"
        "[\n"
        "  {\n"
        "    \"id\": \"same question ID as input\",\n"
        "    \"question\": \"the rewritten, personalized question\",\n"
        "    \"skill\": \"the skill tag from input\"\n"
        "  }\n"
        "]"
    )

    user_content = (
        f"--- STUDENT RESUME CONTEXT ---\n"
        f"Skills: {skills_context}\n"
        f"Projects: {projects_context}\n"
        f"Experience: {experience_context}\n"
        f"Education: {education_context}\n\n"
        f"--- GENERIC QUESTIONS ---\n"
        f"{json.dumps(questions_input, indent=2)}\n"
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Groq LLM to personalize {len(retrieved_questions)} questions - Attempt {attempt + 1}")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # Extract list from potential JSON wrapping (if the model outputs e.g. {"questions": [...]})
            parsed_data = json.loads(response_text)
            
            if isinstance(parsed_data, dict):
                # Look for a list key if Llama returned dict instead of array
                for val in parsed_data.values():
                    if isinstance(val, list):
                        parsed_data = val
                        break
            
            if not isinstance(parsed_data, list):
                raise ValueError("LLM response did not parse as a list.")

            # Validate IDs map correctly to inputs
            valid_questions = []
            input_map = {q["id"]: q for q in retrieved_questions}
            
            for item in parsed_data:
                q_id = item.get("id")
                q_text = item.get("question")
                if q_id in input_map and q_text:
                    valid_questions.append({
                        "id": q_id,
                        "question": q_text,
                        "skill": input_map[q_id].get("skill", "General")
                    })

            # Check that we got back at least some questions
            if not valid_questions:
                raise ValueError("No matching valid question IDs returned.")
            
            # Fill in any missing questions with their generic equivalents
            if len(valid_questions) < len(retrieved_questions):
                added_ids = {q["id"] for q in valid_questions}
                for q in retrieved_questions:
                    if q["id"] not in added_ids:
                        valid_questions.append({
                            "id": q["id"],
                            "question": q["question"],
                            "skill": q.get("skill", "General")
                        })
                        
            return valid_questions

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Attempt {attempt + 1} failed during question personalization LLM call: {str(e)}")
            if attempt == max_retries - 1:
                # Return generic questions as fallback
                logger.error("All personalization LLM attempts failed. Returning generic questions as fallback.")
                return [{
                    "id": q["id"],
                    "question": q["question"],
                    "skill": q.get("skill", "General")
                } for q in retrieved_questions]
