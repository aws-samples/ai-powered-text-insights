examples_es = [
    {
        "text":
        """
        Inspírese para innovar en #AWSreInvent
        
        Asista a la ponencia principal y escuche a los principales líderes de #AWS revelar los últimos lanzamientos de productos y compartir sus 
        opiniones sobre las últimas tendencias en #CloudComputing

        Regístrese: https://go.aws/3RBhhRq
        """,
        "extraction":
        """
        {
            "topic": "ponencia principal de reinvent", 
            "location": "", 
            "entities": ["AWS", "AWSreInvent"], 
            "keyphrases": ["ponencia principal", "lanzamientos de productos", "#CloudComputing", "#AWSreInvent"],
            "sentiment": "neutral"
            "links: ["https://go.aws/3RBhhRq"]
        }
        """
    },
    {
        "text":
        """
        Esta guerra fue forzada sobre nosotros por un enemigo horrendo", dice Netanyahu
                        
        Más información: https://cnn.it/3RKT5MK
        """,
        "extraction":
        """
        {
            "topic": "Guerra", 
            "location": "", 
            "entities": ["Netanyahu", "enemigo horrendo"], 
            "keyphrases": ["enemigo horrendo", "guerra"],
            "sentiment": "negativo"
            "links": ["https://cnn.it/3RKT5MK"]
        }
        """
    },
    {
        "text":
        """
        En medio de la cobertura del conflicto entre Israel y Gaza, el equipo de CNN, que se encuentra en Ashdod, Israel, 
        tuvo que resguardarse de un "bombardeo masivo de cohetes".
        """,
        "extraction":
        """
        {
            "topic": "equipo de CNN se resguardo de un bombardeo", 
            "location": "Ashdod, Israel", 
            "entities": ["Israel", "Gaza", "CNN"], 
            "keyphrases": ["bombardeo masivo de cohetes", "conflicto entre Israel y Gaza"],
            "sentiment": "negativo",
            "links":[]
        }
        """
    },
    {
        "text":
        """
        El Consejo de la FIFA acordó por unanimidad celebrar el centenario de la Copa Mundial de la FIFA de la manera más apropiada. \
        Tres países sudamericanos (Uruguay, Argentina y Paraguay) organizarán un partido cada uno de la Copa Mundial de la FIFA 2030.
        """,
        "extraction":
        """
        {
            "topic": "Anfitriones copa del mundo 2030", 
            "location": "", 
            "entities": ["Uruguay", "Argentina", "Paraguay", "FIFA", "Copa Mundial de la FIFA"], 
            "keyphrases": ["centenario de la Copa Mundial de la FIFA"],
            "sentiment": "positivo",
            "links":[]
        }
        """
    }
]