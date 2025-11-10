from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from decouple import config
from langchain_google_genai import ChatGoogleGenerativeAI

from classmatebot.quizzes.schemas import QuizSchema


def generate_quizzes(number_of_questions, number_of_options, text):
    generated_questions_output_parser = PydanticOutputParser(pydantic_object=QuizSchema)
    generated_questions_format_instructions = generated_questions_output_parser.get_format_instructions()
    generate_questions_template = """
                    This is a text below. Generate {number_of_questions} questions based on this. 
                    Each question should return {number_of_options} options. One of the option should be an answer. 
                    The answer is in UPPERCASE. The remaining options are in lowercases. 
                    
                    The text is {text} 
                    The number_of_questions is: {number_of_questions}
                    The number_of_options is: {number_of_options}  

                    Format instructions: {format_instructions}
                    """
    generate_questions_prompt = PromptTemplate(
        template=generate_questions_template,
        input_variables=["number_of_questions", "number_of_options", 'text'],
        partial_variables={"format_instructions": generated_questions_format_instructions})

    llm = ChatGoogleGenerativeAI(google_api_key=config("GEMINI_API_KEY"), temperature=0.0, model='gemini-2.5-pro')

    generated_questions = generate_questions_prompt | llm | generated_questions_output_parser

    response = generated_questions.invoke({"number_of_questions": number_of_questions,
                                         "number_of_options": number_of_options,
                                         'text': text})
    
    return response