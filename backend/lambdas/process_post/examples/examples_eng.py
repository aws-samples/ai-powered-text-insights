examples_eng = [

    {
        "text":
        """
        Six months ago, Wall Street Journal reporter Evan Gershkovich was detained in Russia during a reporting trip. 
        He remains in a Moscow prison.

        We’re offering resources for those who want to show their support for him. #IStandWithEvan https://wsj.com/Evan 
        """,
        "extraction":
        """
        {
            "topic": "detention of a reporter",
            "location": "Moscow",
            "entities": ["Evan Gershkovich", "Wall Street Journal"],
            "keyphrases": ["reporter", "detained", "prison"],
            "sentiment": "negative",
            "links": ["https://wsj.com/Evan"],
        }
        """
    },
    {
        "text":
        """
        We’re living an internal war": Once-peaceful Ecuador has become engulfed in the cocaine trade, and the bodies are piling up.
        """,
        "extraction":
        """
        {
            "topic": "drug war",
            "location": "Ecuador",
            "entities": ["Ecuador"],
            "keyphrases": ["drug war", "cocaine trade"],
            "sentiment": "negative",
            "links": [],
        }
        """
    },
    {
        "text":
        """
        House Democrats will soon face a difficult decision: Are they better off keeping Kevin McCarthy \
        as House speaker, or taking chances with someone else?
        """,
        "extraction":
        """
        {
            "topic": "house speaker choice",
            "location": "",
            "entities": ["Kevin McCarthy", "House Democrats"],
            "keyphrases": ["house speaker", "house democrats"],
            "sentiment": "neutral",
            "links": [],
        }
        """
    },
    {
        "text":
        """
        A postpandemic hiring spree has left airports vulnerable to security gaps as new staff gain access to secure areas, \
        creating an opening for criminal groups.
        """,
        "extraction":
        """
        {
            "topic": "airport security vulnerabilities",
            "location": "",
            "entities": [],
            "keyphrases": ["security gaps", "secure areas", "criminal groups"],
            "sentiment": "negative",
            "links": [],
        }
        """
    }
]