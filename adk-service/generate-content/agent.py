from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent
from .schemas import PreferencesSchema
from .tools import create_subject, create_topic, create_quiz, enroll_user, notify_user, update_user_state

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

# Agent 1: Curriculum Planner
# Creates the high-level structure and metadata for the lesson.
curriculum_planner_agent = LlmAgent(
    name="CurriculumPlannerAgent",
    model='gemini-2.5-flash',
    instruction="""You are an expert instructional designer.
Based on the user's learning preference, create a structured plan for a lesson.
Your output MUST be a single, valid JSON object containing:
- "preferences": The original user preference string.
- "subject_name": The broad subject category.
- "subject_description": A one-sentence description of the subject.
- "topic_name": A concise title for the lesson topic.
- "topic_description": A one-sentence description of the lesson.

Do not include any text or markdown before or after the JSON object.
""",
    description="Plans the curriculum by defining the subject and topic.",
    output_key="curriculum_plan"
)

# Agent 2: Content Drafter
# Writes the initial version of the lesson content based on the plan.
content_drafter_agent = LlmAgent(
    name="ContentDrafterAgent",
    model='gemini-2.5-flash',
    instruction="""You are a skilled educator writing for a WhatsApp bot.
Based on the provided curriculum plan, write the full lesson content.

**Curriculum Plan:**
{curriculum_plan}

**Task:**
Write engaging and easy-to-understand lesson content, structured into 3-5 logical sections separated by the `[BITE_BREAK]` delimiter. Use emojis and a friendly tone.
Output *only* the raw text of the lesson content.
""",
    description="Drafts the initial lesson content.",
    output_key="drafted_content"
)

# Agent 3: Content Reviewer
# Reviews the drafted content and provides feedback.
content_reviewer_agent = LlmAgent(
    name="ContentReviewerAgent",
    model='gemini-2.5-flash',
    instruction="""You are a meticulous editor. Review the drafted lesson content.

**Drafted Content to Review:**
{drafted_content}

**Review Criteria:**
1. Clarity: Is it easy for a beginner to understand?
2. Accuracy: Is the information correct?
3. Engagement: Is the tone interesting and appropriate for WhatsApp?

**Output:**
Provide feedback as a concise, bulleted list. If no changes are needed, state: "No major issues found."
Output *only* the review comments.
""",
    description="Reviews the drafted content and provides feedback.",
    output_key="review_feedback"
)

# Agent 4: Content Refiner
# Improves the draft based on the reviewer's feedback.
content_refiner_agent = LlmAgent(
    name="ContentRefinerAgent",
    model='gemini-2.5-flash',
    instruction="""You are an expert content refiner.
Improve the original content based on the provided review comments.

**Original Content:**
{drafted_content}

**Review Comments:**
{review_feedback}

**Task:**
Apply the suggestions to improve the original content. If the review is "No major issues found," return the original content unchanged.
Ensure the final content is polished and ready for a student.
Output *only* the final, refined lesson content.
""",
    description="Refines the lesson content based on review feedback.",
    output_key="refined_content"
)

# Agent 5: JSON Assembler
# Assembles the final, structured JSON output, now with schema enforcement.
json_assembler_agent = LlmAgent(
    name="JsonAssemblerAgent",
    model='gemini-2.5-flash',
    instruction="""You are a data formatting expert.
Combine the curriculum plan and the **refined** lesson content into a single, final JSON object that strictly follows the provided schema.

**Curriculum Plan (JSON):**
{curriculum_plan}

**Refined Content (Text):**
{refined_content}

**Task:**
Take the JSON from the "Curriculum Plan" and add a new key to it: "topic_content".
The value for "topic_content" must be the exact text from the "Refined Content".
Your output MUST be the final, complete JSON object and nothing else.
""",
    description="Assembles the final JSON output from all previous steps.",
    output_schema=PreferencesSchema,  # Enforce the output structure
    output_key="final_json_output"
)


# --- 2. Create the SequentialAgent to Orchestrate the Full Pipeline ---
content_pipeline_agent = SequentialAgent(
    name="ContentPipelineAgent",
    sub_agents=[
        curriculum_planner_agent,
        content_drafter_agent,
        content_reviewer_agent,
        content_refiner_agent,
        json_assembler_agent
    ],
    description="Executes a full sequence of planning, drafting, reviewing, refining, and formatting to generate lesson content.",
    tools=[create_subject, create_topic, create_quiz, enroll_user, notify_user, update_user_state]
)

root_agent = content_pipeline_agent