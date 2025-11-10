from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from decouple import config

from classmatebot.subjects.schemas import TopicSchema, PreferencesSchema


def generate_bites(topic: str):
    bites_output_parser = PydanticOutputParser(pydantic_object=TopicSchema)
    bites_format_instructions = bites_output_parser.get_format_instructions()
    bites_template = """

    Role: You are an expert instructional designer. Your specialty is structuring complex information into cohesive, conceptually-sound micro-learning modules.

    Task: Your task is to decompose the provided content into a series of sequential, conceptually cohesive "Bites." A Bite represents a complete, self-contained idea or topic from the text.

    Core Directives for Creating "Bites":
    Identify Conceptual Blocks: First, read the content to identify its logical structure. Look for distinct concepts, such as a definition, a process, a specific stage, a list of reasons, or a topic introduced by a heading.
    Group for Cohesion: A Bite must contain all the text necessary to explain one conceptual block. This means a Bite will often be more than one sentence. It could be a full paragraph, a heading combined with its explanation, or a list. Group sentences together to form a complete thought.
    Verbatim Extraction: Each Bite must be an exact, word-for-word excerpt from the original text. You must not change, add, summarize, or remove any words from the chosen segment.
    Preserve Sequence: The final list of Bites must be presented in the same order that the concepts appear in the original content.

    Strict Constraints:
    DO NOT summarize, paraphrase, or interpret the content.
    DO NOT add any introductory text, commentary, or concluding remarks.
    Your output should only consist of the numbered list of Bites.

    Example of Correct Grouping:
    
    If the provided content is:
    The Chemical Equation of Life\nThe overall balanced chemical equation for photosynthesis is a simple representation of a complex series of reactions:\n6CO₂ (Carbon Dioxide) + 6H₂O (Water) + Light Energy → C₆H₁₂O₆ (Glucose) + 6O₂ (Oxygen)\nThis equation shows that six molecules of carbon dioxide and six molecules of water, in the presence of light energy, are transformed into one molecule of glucose and six molecules of oxygen.
    
    The correct output is a SINGLE Bite, because this is ONE concept:
    Content Bites
    The Chemical Equation of Life
    The overall balanced chemical equation for photosynthesis is a simple representation of a complex series of reactions:
    6CO₂ (Carbon Dioxide) + 6H₂O (Water) + Light Energy → C₆H₁₂O₆ (Glucose) + 6O₂ (Oxygen)
    This equation shows that six molecules of carbon dioxide and six molecules of water, in the presence of light energy, are transformed into one molecule of glucose and six molecules of oxygen.

    Content to Decompose:
    {topic}

    Format instructions: {format_instructions}, 
    """
    bites_prompt = PromptTemplate(
        template=bites_template,
        input_variables=['topic'],
        partial_variables={'format_instructions': bites_format_instructions},
    )
    llm = ChatGoogleGenerativeAI(google_api_key=config("GEMINI_API_KEY"), temperature=0.0, model='gemini-2.5-pro')

    bites_response = bites_prompt | llm | bites_output_parser
    
    response = bites_response.invoke({"topic": topic})
    
    return response


def generate_preference_content(preferences: str):
    output_parser = PydanticOutputParser(pydantic_object=PreferencesSchema)
    format_instructions = output_parser.get_format_instructions()
    prompt_template = """
    You are an expert content creator for a WhatsApp learning bot. Your primary goal is to take a user's request and transform it into a comprehensive, engaging, and well-structured piece of educational content that can be delivered in sequential messages.

    CONTEXT:
    The content is for a WhatsApp chat. The main `topic_content` will be programmatically split into smaller, "bite-sized" messages. This creates a better, more interactive learning experience.

    TASK:
    Based on the user's preference provided below, generate a complete set of information for the topic. The `topic_content` must be structured into 3-5 logical sections separated by the special delimiter `[BITE_BREAK]`. Each section should be a self-contained idea, suitable for a single WhatsApp message. Use emojis, short paragraphs, and an engaging tone.

    USER PREFERENCE:
    {preferences}

    STRICT FORMATTING INSTRUCTIONS:
    You MUST respond with a single, valid JSON object. Do not include any text, explanations, or markdown formatting like ```json before or after the JSON object.
    {format_instructions}
    
    --- EXAMPLES ---

    USER PREFERENCE: "tell me about black holes in a simple way"
    
    EXAMPLE OUTPUT:
    
        "preferences": "tell me about black holes in a simple way",
        "topic_content": "Imagine a star many times bigger than our Sun ☀️ running out of fuel. It collapses under its own weight into a super tiny point! This creates a place with such powerful gravity that nothing, not even light, can escape. That's a black hole! 🕳️\\n[BITE_BREAK]\\nThe 'edge' of a black hole is called the event horizon. Think of it as a one-way door in space. Once you cross it, there's no turning back because you'd need to travel faster than the speed of light to escape, which is impossible!\\n[BITE_BREAK]\\nSo if they're invisible, how do we know they're there? 🤔 Scientists are clever! They can't see the black hole itself, but they can see its effect on nearby stars and gas. They watch for stars that orbit around what looks like empty space, being pulled in by an immense gravitational force. ✨",
        "topic_name": "The Mystery of Black Holes",
        "topic_description": "A simple explanation of what black holes are, how they work, and how we find them.",
        "subject_name": "Astrophysics",
        "subject_description": "The branch of astronomy that studies the physics of the universe, including stars, galaxies, and celestial objects."
    
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=['preferences'], partial_variables={'format_instructions': format_instructions},)

    llm = ChatGoogleGenerativeAI(google_api_key=config("GEMINI_API_KEY"), temperature=0.0, model='gemini-2.5-pro')

    chain = prompt | llm | output_parser
    response = chain.invoke({"preferences": preferences})
    return response