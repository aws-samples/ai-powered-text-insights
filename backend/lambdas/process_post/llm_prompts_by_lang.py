# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

prompts_map = {
    "claude": {
        "es": {
            "info_extraction": """Eres un sistema de extraccion de informacion. Tu tarea es extraer informacion clave del texto encerrado entre\
             <post></post> ay ponerla en un objeto JSON.
    
            Aqui hay algunas reglas basicas para la tarea:
            
            - No imprimas tu razonamiento para la extraccion de la informacion
            - Siempre produce objetos JSON completos y validos
            - Si no se puede extraer la informacion o no puedes producir un objeto JSON valido imprime un objeto JSON vacio "{{}}"
    
            Aqui hay algunos ejemplos sobre como extraer la informacion del texto:
            
            <examples>
            {examples}
            </examples>
            
            Extrae la informacion del siguiente post y ponlo en <json></json>. 
    
            <post>
            {post}
            </post>
            
            Escribe tu respuesta como un objeto JSON con la siguiente definicion:
                
            <json_format>
            {json_format}
            </json_format>
            
            Assistant:<json>
            """,
            "topic_match": """Human:Determina si el texto entre <topic></topic> esta relacionado a uno o mas de los temas\
            enlistados en <meta_topics></meta_topics>.
            
            <topic>
            {text}
            </topic>
            
            <meta_topics>
            {meta_topics}
            </meta_topics>
            
            Presenta el resultado y colocalo en <json></json> empleando el formato JSON encerrado entre <json_format></json_format>. \
            
            <json_format>
            {json_format}
            </json_format>
            
            Usa solo los temas enlistados en <meta_topics></meta_topics> para formular la respuesta, si no encuentras temas relacionados la respuesta es:\
            
            {{
                "topic_match":False,
                "related_topics": []
            }}
            
            Assistant: <json>
            """,
        },
    "en": {
            "info_extraction": """You are an information extraction system. Your task is to extract key information from the text enclosed between\
             <post></post> and put it in a JSON object.
    
            Here are some basic rules for the task:
            
            - Do not output your reasoning for the information extraction
            - Always produce complete and valid JSON objects
            - If no information can be extracted or you can not produce a valid JSON object output an empty json object "{{}}"
    
            Here are some examples of how to extract information from text:
            
            <examples>
            {examples}
            </examples>
            
            Extract information from the following post and put it in the <json> XML tag. 
    
            <post>
            {post}
            </post>
            
            Write your answer as a JSON object with the following definition
                
            <json_format>
            {json_format}
            </json_format>
            
            Assistant:<json>
            """,
            "topic_match": """Determine if the text between <text></text> is related to one or more of the topics \
            listed in <meta_topics></meta_topics> and extract such topics.
            
            <meta_topics>
            {meta_topics}
            </meta_topics>
            
            Use only the topics listed in <meta_topics></meta_topics> for your answer, if no related topic is found the answer is:\
            
            {{
                "topic_match":False,
                "related_topics": []
            }}
            
            <text>
            {text}
            </text>
            
            Present the result and put it in the <json> XML tag using the JSON format described next
            
            <json_format>
            {json_format}
            </json_format>
            """,
        }
    }
}

examples_map = \
    {
    "claude":
        {
        "es":
            {
            "info_extraction_examples":
                [
                    (
                        """Inspírese para innovar en #AWSreInvent
                
                        Asista a la ponencia principal y escuche a los principales líderes de #AWS revelar los últimos lanzamientos de productos y compartir sus 
                        opiniones sobre las últimas tendencias en #CloudComputing
                
                        Regístrese: https://go.aws/3RBhhRq""",
                        """{
                            "topic": "ponencia principal de reinvent", 
                            "location": "", 
                            "entities": ["AWS", "AWSreInvent"], 
                            "keyphrases": ["ponencia principal", "lanzamientos de productos", "#CloudComputing", "#AWSreInvent"],
                            "sentiment": "neutral"
                            "links: ["https://go.aws/3RBhhRq"]
                            }"""
                    ),
                    (
                        """"Esta guerra fue forzada sobre nosotros por un enemigo horrendo", dice Netanyahu
                        
                        Más información: https://cnn.it/3RKT5MK""",
                        """{
                            "topic": "Guerra", 
                            "location": "", 
                            "entities": ["Netanyahu", "enemigo horrendo"], 
                            "keyphrases": ["enemigo horrendo", "guerra"],
                            "sentiment": "negativo"
                            "links": ["https://cnn.it/3RKT5MK"]
                            }"""
                    ),
                    (
                        """En medio de la cobertura del conflicto entre Israel y Gaza, el equipo de CNN, que se encuentra en Ashdod, Israel, 
                        tuvo que resguardarse de un "bombardeo masivo de cohetes".""",
                        """{
                            "topic": "equipo de CNN se resguardo de un bombardeo", 
                            "location": "Ashdod, Israel", 
                            "entities": ["Israel", "Gaza", "CNN"], 
                            "keyphrases": ["bombardeo masivo de cohetes", "conflicto entre Israel y Gaza"],
                            "sentiment": "negativo",
                            "links":[]
                            }"""
                    ),
                    (
                        """"El Consejo de la FIFA acordó por unanimidad celebrar el centenario de la Copa Mundial de la FIFA de la manera más apropiada. 
                        Tres países sudamericanos (Uruguay, Argentina y Paraguay) organizarán un partido cada uno de la Copa Mundial de la FIFA 2030.""",
                        """{
                            "topic": "Anfitriones copa del mundo 2030", 
                            "location": "", 
                            "entities": ["Uruguay", "Argentina", "Paraguay", "FIFA", "Copa Mundial de la FIFA"], 
                            "keyphrases": ["centenario de la Copa Mundial de la FIFA"],
                            "sentiment": "positivo",
                            "links":[]
                            }"""
                    ),
                ],
            },
        "en":
            {
            "info_extraction_examples":
                [
                    (
                        """Six months ago, Wall Street Journal reporter Evan Gershkovich was detained in Russia during a reporting trip.

                        He remains in a Moscow prison.
                        
                        We’re offering resources for those who want to show their support for him. #IStandWithEvan https://wsj.com/Evan""",
                        """{
                            "topic": "detention of a reporter", 
                            "location": "Moscow", 
                            "entities": ["Evan Gershkovich", "Wall Street Journal"], 
                            "keyphrases": ["reporter", "detained", "prison"],
                            "sentiment": "negative",
                            "links": ["https://wsj.com/Evan"],
                            }"""
                    ),
                    (
                        """"We’re living an internal war": Once-peaceful Ecuador has become engulfed in the cocaine trade, and the bodies are piling up.""",
                        """{
                            "topic": "drug war", 
                            "location": "Ecuador", 
                            "entities": ["Ecuador"], 
                            "keyphrases": ["drug war", "cocaine trade"],
                            "sentiment": "negative",
                            "links": [],
                            }"""
                    ),
                    (
                        """House Democrats will soon face a difficult decision: Are they better off keeping Kevin McCarthy 
                        as House speaker, or taking chances with someone else?""",
                        """{
                            "topic": "house speaker choice", 
                            "location": "", 
                            "entities": ["Kevin McCarthy", "House Democrats"], 
                            "keyphrases": ["house speaker", "house democrats"],
                            "sentiment": "neutral",
                            "links": [],
                            }"""
                    ),
                    (
                        """A postpandemic hiring spree has left airports vulnerable to security gaps as new staff gain access to secure areas, 
                        creating an opening for criminal groups.""",
                        """{
                            "topic": "airport security vulnerabilities", 
                            "location": "", 
                            "entities": [], 
                            "keyphrases": ["security gaps", "secure areas", "criminal groups"],
                            "sentiment": "negative",
                            "links": [],
                            }"""
                    ),
                ],
            }
        },
    }

json_format_str = {
    'info_extraction':
        """
        {
          "type": "object",
          "properties": {
            "topic": {
              "description": "the main topic of the post",
              "type": "string",
              "required": false
            },
            "location": {
              "description": "the location, if existing, where the events occur",
              "type": "string",
              "required": false
            },
            "entities": {
              "description": "the entities involved in the post",
              "type": "list",
              "required": false
            },
            "keyphrases": {
              "description": "the keyphrases in the short text",
              "type": "list",
              "required": false
            },
            "sentiment": {
              "description": "the sentiment of the post",
              "type": "string",
              "required": false
            },
            "links": {
              "description": "any links found withing the post",
              "type": "list",
              "required": false
            }
          }
        }
        """,
    'topic_match':
        """
        {
          "type": "object",
          "properties": {
            "topic_match": {
              "description": "determines if the text matches any topic in the list",
              "type": "boolean",
              "required": true
            },
            "related_topics": {
              "description": "the list of topics the input text can be matched to",
              "type": "list",
              "required": true
            }
          }
        }
        """,
}