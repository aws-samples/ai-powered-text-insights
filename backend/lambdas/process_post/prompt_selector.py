from langchain.chains.prompt_selector import ConditionalPromptSelector

from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, \
    AIMessagePromptTemplate
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from examples.examples_eng import examples_eng
from examples.examples_es import examples_es

from typing import Callable

# ANTHROPIC CLAUDE 3 PROMPT TEMPLATES

# English Prompts

claude_information_extraction_system_prompt_en = """You are an information extraction system. Your task is to extract key information from the text that will be presented to you.

Here are some basic rules for the task:

- You can reason about the task and the information, take your time to think
- You must classify the sentiment of the text in one of the following: {sentiments}
- NEVER fill a value of your own for entries where you are unsure of and rather use default values

Here are some examples of how to extract information from text:
"""

claude_information_extraction_user_prompt_en = """
Extract the information from the following text:

{text}
"""

claude_topic_match_system_prompt_en = """
You are a highly accurate text classification system. Your task is to classify text into one or more categories. Even though you can classify text in any category \
for this task you are only interested in classifying the text in some of the topics listed below:

<meta_topics>
{meta_topics}
</meta_topics>

Here are some rules for the text classification you will perform:

- You should not be forced to classify the text in any of the existing categories, its ok if you cant fit a text into the topics of interest
- Only classify a text into a category if you are really sure it belongs to it
- Use only the categories in the <meta_topics> list for your classification
- You may classify a text in any number of topics (including zero) but your result must always be a list (even if its empty)
- You can classify text in multiple categories at once
- You can reason about your task, take your time to think
"""

claude_topic_match_user_prompt_en = user_prompt = """
Classify the following text into one or more categories of your interest:

{text}
"""

examples_prompt_template_eng = ChatPromptTemplate.from_messages(
    [
        HumanMessagePromptTemplate.from_template("{text}", input_variables=["text"], validate_template=True),
        AIMessagePromptTemplate.from_template("{extraction}", input_variables=["extraction"], validate_template=True)
    ]
)

few_shot_chat_prompt_eng = FewShotChatMessagePromptTemplate(
    example_prompt=examples_prompt_template_eng,
    examples=examples_eng,
)

CLAUDE_INFORMATION_EXTRACTION_PROMPT_TEMPLATE_EN = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(claude_information_extraction_system_prompt_en, input_variables=["sentiments"], validate_template=True),
    few_shot_chat_prompt_eng,
    HumanMessagePromptTemplate.from_template(claude_information_extraction_user_prompt_en, input_variables=["text"], validate_template=True),
])

CLAUDE_TOPIC_MATCH_PROMPT_TEMPLATE_EN = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(claude_topic_match_system_prompt_en, input_variables=["meta_topics"], validate_template=True),
    HumanMessagePromptTemplate.from_template(claude_topic_match_user_prompt_en, input_variables=["text"], validate_template=True),
])

# Spanish Prompts

claude_information_extraction_system_prompt_es = """
Eres un sistema de extraccion de informacion. Tu tarea consiste en extraer informacion clave del texto que te sera presentado.

Estas son algunas reglas basicas que debes seguir:

- Puedes razonar sobre la tarea y la informacion, tomate un tiempo para pensar
- Debes clasificar el sentimiento en uno de los siguientes: {sentiments}
- NUNCA acompletes un valor del cual no estas seguro con valores tuyos, en su lugar emplea los valores por defecto para cada campo

Aqui hay algunos ejemplos de como extraer informacion de texto:
"""

claude_information_extraction_user_prompt_es = """
Extrae la informacion de siguiente texto:

{text}
"""

claude_topic_match_system_prompt_es = """
Eres un sistema de clasificacion de texto altamente preciso. Tu tarea es clasificar texto en una o mas categorias. Aunque eres capaz de clasificar texto en cualquier \
categoria para esta tarea solo estas interesado en clasificar el texto en algunas de las categorias listadas aqui:

<meta_topics>
{meta_topics}
</meta_topics>

Aqui hay algunas reglas para la clasificacion de texto que vas a realizar:

- No te debes ver forzado a clasificar el texto en ninguna de las categorias existentes, esta bien si no puedes clasificar el texto en ninguno de los temas de interes
- Solo clasifica el texto en una categoria si estas completamente seguro que pertenece a esa categoria
- Usa solo las categorias en la lista <meta_topics> para tu clasificacion
- Puedes clasificar el texto en cualquier numero de categorias (incluso cero) pero tu respuesta siempre debe ser una lista (aunque sea una lista vacia)
- Puedes clasificar el texto en multiples categorias a la vez
- Puedes razonar sobre tu tarea, tomate tu tiempo para pensar
"""

claude_topic_match_user_prompt_es = """
Clasifica el siguiente texto en una o mas categorias de tu interes:

{text}
"""

examples_prompt_template_es = ChatPromptTemplate.from_messages(
    [
        HumanMessagePromptTemplate.from_template("{text}", input_variables=["text"], validate_template=True),
        AIMessagePromptTemplate.from_template("{extraction}", input_variables=["extraction"], validate_template=True)
    ]
)

few_shot_chat_prompt_es = FewShotChatMessagePromptTemplate(
    example_prompt=examples_prompt_template_es,
    examples=examples_es,
)

CLAUDE_INFORMATION_EXTRACTION_PROMPT_TEMPLATE_ES = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(claude_information_extraction_system_prompt_es, input_variables=["sentiments"], validate_template=True),
    few_shot_chat_prompt_eng,
    HumanMessagePromptTemplate.from_template(claude_information_extraction_user_prompt_es,
                                             input_variables=["text"], validate_template=True),
])

CLAUDE_TOPIC_MATCH_PROMPT_TEMPLATE_ES = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(claude_topic_match_system_prompt_es, input_variables=["meta_topics"],
                                              validate_template=True),
    HumanMessagePromptTemplate.from_template(claude_topic_match_user_prompt_es, input_variables=["text"],
                                             validate_template=True),
])


def is_es(language: str) -> bool:
    return "es" == language


def is_en(language: str) -> bool:
    return "en" == language


def is_claude(model_id: str) -> bool:
    return "claude" in model_id


def is_es_claude(language: str) -> Callable[[str], bool]:
    return lambda model_id: is_es(language) and is_claude(model_id)


def is_en_claude(language: str) -> Callable[[str], bool]:
    return lambda model_id: is_en(language) and is_claude(model_id)


def get_information_extraction_prompt_selector(lang: str) -> ConditionalPromptSelector:
    return ConditionalPromptSelector(
        default_prompt=CLAUDE_INFORMATION_EXTRACTION_PROMPT_TEMPLATE_EN,
        conditionals=[
            (is_es_claude(lang), CLAUDE_INFORMATION_EXTRACTION_PROMPT_TEMPLATE_ES),
        ]
    )


def get_topic_match_prompt_selector(lang: str) -> ConditionalPromptSelector:
    return ConditionalPromptSelector(
        default_prompt=CLAUDE_TOPIC_MATCH_PROMPT_TEMPLATE_EN,
        conditionals=[
            (is_es_claude(lang), CLAUDE_TOPIC_MATCH_PROMPT_TEMPLATE_ES)
        ]
    )