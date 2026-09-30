"""PILOT ADAPTATION DATASET (TASK-011C)

Hand-crafted, pedagogically rigorous, structurally compliant adaptations
for the 20 selected pilot exercises (A1 + A2).

Guarantees:
1. Exact invariance of lesson, exercise, and question ordering.
2. Invariant response_model, gap count, and option count.
3. Invariant correct answer cardinality (e.g. exactly 2 for multiple_choice, 1 for single_choice).
4. Full originality: non-overlapping contexts and varied vocabulary.
"""

from typing import Dict, Any, List

PILOT_DATA: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # EXERCISE 1: quiz-388 (A2) First conditional and future time clauses
    # =========================================================================
    "quiz-388": {
        "title": "Exercise 2",
        "instruction": "Choose the correct forms to complete the first conditional sentences and future time clauses below.",
        "questions": [
            {
                "question_id": "3329",
                "adapted_text": "1 Where will you travel if you _____ the scholarship?",
                "options": [
                    {"text": "might win", "is_correct": 0},
                    {"text": "will win", "is_correct": 0},
                    {"text": "win", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["if", "win", "will", "might"],
            },
            {
                "question_id": "3326",
                "adapted_text": "2 As soon as you meet Sarah, you ____ amazed by how fast she speaks Spanish. (Select TWO valid choices)",
                "options": [
                    {"text": "are", "is_correct": 0},
                    {"text": "will be", "is_correct": 1},
                    {"text": "might be", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["will be", "might be", "are"],
            },
            {
                "question_id": "3325",
                "adapted_text": "3 The detective will not stop until he ____ who took the necklace.",
                "options": [
                    {"text": "discovers", "is_correct": 1},
                    {"text": "will discover", "is_correct": 0},
                    {"text": "should discover", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["until", "discovers", "will discover"],
            },
            {
                "question_id": "3327",
                "adapted_text": "4 The passengers will start boarding the plane as soon as the gate _____.",
                "options": [
                    {"text": "opens", "is_correct": 1},
                    {"text": "will open", "is_correct": 0},
                    {"text": "may open", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["as soon as", "opens", "will open"],
            },
            {
                "question_id": "3330",
                "adapted_text": "5 If you feel uncertain about the directions, _____ a local police officer. (Select TWO valid choices)",
                "options": [
                    {"text": "consult", "is_correct": 1},
                    {"text": "you consult", "is_correct": 0},
                    {"text": "you should consult", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["consult", "you should consult"],
            },
            {
                "question_id": "3331",
                "adapted_text": "6 If we _____ a reliable car, we won't be able to visit our grandparents.",
                "options": [
                    {"text": "won't buy", "is_correct": 0},
                    {"text": "don't buy", "is_correct": 1},
                    {"text": "should buy", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["don't buy", "won't buy"],
            },
            {
                "question_id": "3328",
                "adapted_text": "7 The manager _____ the contract until the legal team checks every detail.",
                "options": [
                    {"text": "won't sign", "is_correct": 1},
                    {"text": "doesn't sign", "is_correct": 0},
                    {"text": "is not signing", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["won't sign", "doesn't sign"],
            },
            {
                "question_id": "3332",
                "adapted_text": "8 If you leave your umbrella by the entrance, someone ____ it by mistake.",
                "options": [
                    {"text": "take", "is_correct": 0},
                    {"text": "takes", "is_correct": 0},
                    {"text": "might take", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["might take", "takes"],
            },
            {
                "question_id": "3333",
                "adapted_text": "9 When my daughter _____ university, we will move to a quiet village.",
                "options": [
                    {"text": "finishes", "is_correct": 1},
                    {"text": "might finish", "is_correct": 0},
                    {"text": "will finish", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["finishes", "will finish"],
            },
            {
                "question_id": "3334",
                "adapted_text": "10 If she practices every afternoon, she _____ the tennis tournament. (Select TWO valid choices)",
                "options": [
                    {"text": "win", "is_correct": 0},
                    {"text": "'ll win", "is_correct": 1},
                    {"text": "might win", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["'ll win", "might win"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 2: quiz-409 (A2) So, neither: So am I, neither do I, etc.
    # =========================================================================
    "quiz-409": {
        "title": "Exercise 2",
        "instruction": "Choose the correct forms with so, neither, too, either to complete the sentences below.",
        "questions": [
            {
                "question_id": "3493",
                "adapted_text": "1 A: 'I cannot attend the workshop tomorrow.' B: '_____.'",
                "options": [
                    {"text": "Neither can't I", "is_correct": 0},
                    {"text": "Neither can I", "is_correct": 1},
                    {"text": "So can I", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["neither", "can", "i"],
            },
            {
                "question_id": "3508",
                "adapted_text": "2 A: 'I am not attending the party this evening.' B: '_____.' (Identify TWO valid responses)",
                "options": [
                    {"text": "Neither I am", "is_correct": 0},
                    {"text": "Neither am I", "is_correct": 1},
                    {"text": "I am either", "is_correct": 0},
                    {"text": "I am not attending either", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["neither", "am", "i", "either"],
            },
            {
                "question_id": "3494",
                "adapted_text": "3 A: 'We haven't got enough chairs in the dining room.' B: 'Neither _____ in our office.'",
                "options": [
                    {"text": "have we", "is_correct": 1},
                    {"text": "we have", "is_correct": 0},
                    {"text": "do we", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["neither", "have", "we"],
            },
            {
                "question_id": "3495",
                "adapted_text": "4 A: 'We bought fresh vegetables at the farmers market.' B: '_____.' (Identify TWO valid responses)",
                "options": [
                    {"text": "So did we", "is_correct": 1},
                    {"text": "So are we", "is_correct": 0},
                    {"text": "So were we", "is_correct": 0},
                    {"text": "We bought fresh vegetables too", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["so", "did", "we", "too"],
            },
            {
                "question_id": "3496",
                "adapted_text": "5 A: 'I rarely eat seafood in winter.' B: '______.'",
                "options": [
                    {"text": "Neither do I", "is_correct": 1},
                    {"text": "Neither am I", "is_correct": 0},
                    {"text": "So am I", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["neither", "do", "i"],
            },
            {
                "question_id": "3497",
                "adapted_text": "6 A: 'Marcus is not joining our team.' B: 'And _____.'",
                "options": [
                    {"text": "so isn't Lucas", "is_correct": 0},
                    {"text": "neither is Lucas", "is_correct": 1},
                    {"text": "either isn't Lucas", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["neither", "is"],
            },
            {
                "question_id": "3507",
                "adapted_text": "7 A: 'I crave a hot cup of tea.' B: '_____.'",
                "options": [
                    {"text": "So do I", "is_correct": 1},
                    {"text": "Neither do I", "is_correct": 0},
                    {"text": "So I do", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["so", "do", "i"],
            },
            {
                "question_id": "3509",
                "adapted_text": "8 A: 'I was not anxious about the examination results.' B: '_____.' (Identify TWO valid responses)",
                "options": [
                    {"text": "Neither was I", "is_correct": 1},
                    {"text": "Neither wasn't I", "is_correct": 0},
                    {"text": "I was anxious either", "is_correct": 0},
                    {"text": "I was not anxious either", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["neither", "was", "i", "either"],
            },
            {
                "question_id": "3510",
                "adapted_text": "9 A: 'I considered the lecture fascinating.' B: '_____.'",
                "options": [
                    {"text": "Neither did I", "is_correct": 0},
                    {"text": "So I did", "is_correct": 0},
                    {"text": "So did I", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["so", "did", "i"],
            },
            {
                "question_id": "3511",
                "adapted_text": "10 A: 'The customer did not appreciate the delay.' B: '_____.' (Identify TWO valid responses)",
                "options": [
                    {"text": "So didn't I", "is_correct": 0},
                    {"text": "Neither didn't I", "is_correct": 0},
                    {"text": "Neither did I", "is_correct": 1},
                    {"text": "I did not appreciate it either", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["neither", "did", "i", "either"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 3: quiz-428 (A1) Adjectives: Old, interesting, expensive, etc.
    # =========================================================================
    "quiz-428": {
        "title": "Exercise 2",
        "instruction": "Put the words in the correct order.",
        "questions": [
            {
                "question_id": "3706",
                "adapted_text": "1 Which sentence has the correct word order?",
                "options": [
                    {"text": "Her fantastic suggestion is.", "is_correct": 0},
                    {"text": "Her suggestion is fantastic.", "is_correct": 1},
                    {"text": "Fantastic her suggestion is.", "is_correct": 0},
                    {"text": "Her suggestion fantastic is.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3707",
                "adapted_text": "2 Which sentence has the correct word order?",
                "options": [
                    {"text": "He a talented musician is.", "is_correct": 0},
                    {"text": "He is a musician talented.", "is_correct": 0},
                    {"text": "He is a talented musician.", "is_correct": 1},
                    {"text": "He a musician talented is.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3708",
                "adapted_text": "3 Which sentence has the correct word order?",
                "options": [
                    {"text": "Is that jacket Japanese?", "is_correct": 1},
                    {"text": "Is Japanese that jacket?", "is_correct": 0},
                    {"text": "That jacket Japanese is?", "is_correct": 0},
                    {"text": "That jacket is Japanese?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3709",
                "adapted_text": "4 Which sentence has the correct word order?",
                "options": [
                    {"text": "This hotel room extremely clean is.", "is_correct": 0},
                    {"text": "This is a hotel room extremely clean.", "is_correct": 0},
                    {"text": "Extremely clean is this hotel room.", "is_correct": 0},
                    {"text": "This hotel room is extremely clean.", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3710",
                "adapted_text": "5 Which sentence has the correct word order?",
                "options": [
                    {"text": "She a German vehicle drives.", "is_correct": 0},
                    {"text": "She drives a German vehicle.", "is_correct": 1},
                    {"text": "She drives a vehicle German.", "is_correct": 0},
                    {"text": "A vehicle German she drives.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3711",
                "adapted_text": "6 Which sentence has the correct word order?",
                "options": [
                    {"text": "That is their residence primary.", "is_correct": 0},
                    {"text": "Their primary residence is that.", "is_correct": 0},
                    {"text": "Is that their residence primary?", "is_correct": 0},
                    {"text": "That is their primary residence.", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3713",
                "adapted_text": "7 Which sentence has the correct word order?",
                "options": [
                    {"text": "It is a neighborhood extremely quiet.", "is_correct": 0},
                    {"text": "It is an extremely quiet neighborhood.", "is_correct": 1},
                    {"text": "Extremely quiet it is a neighborhood.", "is_correct": 0},
                    {"text": "A neighborhood extremely quiet is.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3714",
                "adapted_text": "8 Which sentence has the correct word order?",
                "options": [
                    {"text": "Are the new neighbors friendly?", "is_correct": 1},
                    {"text": "Are friendly the new neighbors?", "is_correct": 0},
                    {"text": "Friendly are the new neighbors?", "is_correct": 0},
                    {"text": "The new neighbors are friendly?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3715",
                "adapted_text": "9 Which sentence has the correct word order?",
                "options": [
                    {"text": "That city ancient is.", "is_correct": 0},
                    {"text": "A city ancient that is.", "is_correct": 0},
                    {"text": "That is an ancient city.", "is_correct": 1},
                    {"text": "That is a city ancient.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
            {
                "question_id": "3716",
                "adapted_text": "10 Which sentence has the correct word order?",
                "options": [
                    {"text": "That ancient city is peaceful.", "is_correct": 1},
                    {"text": "That ancient city peaceful is.", "is_correct": 0},
                    {"text": "Is peaceful that ancient city?", "is_correct": 0},
                    {"text": "That ancient city is peaceful?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "is", "the", "correct", "order"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 4: quiz-447 (A1) Adverbs of frequency with present simple
    # =========================================================================
    "quiz-447": {
        "title": "Exercise 1",
        "instruction": "Order the following sentences, which contain adverbs of frequency.",
        "questions": [
            {
                "question_id": "3890",
                "adapted_text": "1 Which sentence is correctly structured?",
                "options": [
                    {"text": "The librarian is usually helpful.", "is_correct": 1},
                    {"text": "The librarian usually is helpful.", "is_correct": 0},
                    {"text": "Is usually the librarian helpful?", "is_correct": 0},
                    {"text": "Usually the librarian is helpful.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3891",
                "adapted_text": "2 Which sentence is correctly structured?",
                "options": [
                    {"text": "Seldom they drink sugary soda.", "is_correct": 0},
                    {"text": "They drink seldom sugary soda.", "is_correct": 0},
                    {"text": "They drink sugary soda seldom.", "is_correct": 0},
                    {"text": "They seldom drink sugary soda.", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3892",
                "adapted_text": "3 Which sentence is correctly structured?",
                "options": [
                    {"text": "Our grandfather doesn't rarely read newspapers online.", "is_correct": 0},
                    {"text": "Our grandfather reads rarely newspapers online.", "is_correct": 0},
                    {"text": "Our grandfather reads newspapers online rarely.", "is_correct": 0},
                    {"text": "Our grandfather rarely reads newspapers online.", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3893",
                "adapted_text": "4 Which sentence is correctly structured?",
                "options": [
                    {"text": "Do frequently you visit art galleries?", "is_correct": 0},
                    {"text": "Do you frequently visit art galleries?", "is_correct": 1},
                    {"text": "Do you visit frequently art galleries?", "is_correct": 0},
                    {"text": "Do you visit art galleries frequently?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3894",
                "adapted_text": "5 Which sentence is correctly structured?",
                "options": [
                    {"text": "She normally doesn't wake up early.", "is_correct": 0},
                    {"text": "She doesn't wake up early normally.", "is_correct": 0},
                    {"text": "She doesn't normally wake up early.", "is_correct": 1},
                    {"text": "Does she wake usually early up?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3895",
                "adapted_text": "6 Which sentence is correctly structured?",
                "options": [
                    {"text": "We every Saturday attend swimming sessions.", "is_correct": 0},
                    {"text": "We attend every Saturday swimming sessions.", "is_correct": 0},
                    {"text": "We attend swimming sessions every Saturday.", "is_correct": 1},
                    {"text": "We every Saturday attend swimming sessions.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3896",
                "adapted_text": "7 Which sentence is correctly structured?",
                "options": [
                    {"text": "The children always are quite hungry after swimming.", "is_correct": 0},
                    {"text": "The children are always quite hungry after swimming.", "is_correct": 1},
                    {"text": "The children are quite hungry after swimming always.", "is_correct": 0},
                    {"text": "Always the children are quite hungry after swimming.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3897",
                "adapted_text": "8 Which sentence is correctly structured?",
                "options": [
                    {"text": "I constantly drink coffee before noon.", "is_correct": 1},
                    {"text": "Constantly I drink coffee before noon.", "is_correct": 0},
                    {"text": "I drink constantly coffee before noon.", "is_correct": 0},
                    {"text": "I drink coffee before noon constantly.", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3898",
                "adapted_text": "9 Which sentence is correctly structured?",
                "options": [
                    {"text": "He doesn't carry an umbrella often.", "is_correct": 0},
                    {"text": "He often doesn't carry an umbrella.", "is_correct": 0},
                    {"text": "Often he doesn't carry an umbrella.", "is_correct": 0},
                    {"text": "He doesn't often carry an umbrella.", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
            {
                "question_id": "3899",
                "adapted_text": "10 Which sentence is correctly structured?",
                "options": [
                    {"text": "Is your roommate sometimes noisy late in the evening?", "is_correct": 1},
                    {"text": "Is sometimes your roommate noisy late in the evening?", "is_correct": 0},
                    {"text": "Is your roommate noisy sometimes late in the evening?", "is_correct": 0},
                    {"text": "Your roommate is sometimes noisy late in the evening?", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["which", "sentence", "is", "correct"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 5: quiz-472 (A1) A, some, any: Countable and uncountable nouns
    # =========================================================================
    "quiz-472": {
        "title": "Exercise 2",
        "instruction": "Choose the correct option to complete these sentences.",
        "questions": [
            {
                "question_id": "4122",
                "adapted_text": "1 We did not spot _____ during the guided tour.",
                "options": [
                    {"text": "any tourists", "is_correct": 1},
                    {"text": "some tourists", "is_correct": 0},
                    {"text": "any tourist", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["any", "some"],
            },
            {
                "question_id": "4123",
                "adapted_text": "2 The museum purchased _____ for the exhibition.",
                "options": [
                    {"text": "some antique luggages", "is_correct": 0},
                    {"text": "an antique luggage", "is_correct": 0},
                    {"text": "some antique luggage", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["some", "an"],
            },
            {
                "question_id": "4124",
                "adapted_text": "3 Could you pass me _____ orange, please?",
                "options": [
                    {"text": "an", "is_correct": 1},
                    {"text": "some", "is_correct": 0},
                    {"text": "any", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["an", "some", "any"],
            },
            {
                "question_id": "4125",
                "adapted_text": "4 The donor provided _____ for the laboratory archive.",
                "options": [
                    {"text": "some rare manuscripts", "is_correct": 1},
                    {"text": "a rare manuscripts", "is_correct": 0},
                    {"text": "some rare manuscript", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["some", "a"],
            },
            {
                "question_id": "4126",
                "adapted_text": "5 The resort where they reserved a room features _____.",
                "options": [
                    {"text": "tennis court", "is_correct": 0},
                    {"text": "a tennis court", "is_correct": 1},
                    {"text": "some tennis court", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["a", "some"],
            },
            {
                "question_id": "4127",
                "adapted_text": "6 The tour guide understands _____ Italian.",
                "options": [
                    {"text": "some", "is_correct": 1},
                    {"text": "any", "is_correct": 0},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["some", "any", "an"],
            },
            {
                "question_id": "4129",
                "adapted_text": "7 We didn't receive _____ regarding the proposed timetable.",
                "options": [
                    {"text": "a messages", "is_correct": 0},
                    {"text": "any messages", "is_correct": 1},
                    {"text": "any message", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["any", "a"],
            },
            {
                "question_id": "4128",
                "adapted_text": "8 Could you lend me _____ cash for the parking meter?",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "any", "is_correct": 0},
                    {"text": "some", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["some", "any", "a"],
            },
            {
                "question_id": "4130",
                "adapted_text": "9 Do you have _____ living abroad?",
                "options": [
                    {"text": "any aunt or uncle", "is_correct": 0},
                    {"text": "some aunts or uncles", "is_correct": 0},
                    {"text": "any aunts or uncles", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["any", "some"],
            },
            {
                "question_id": "4131",
                "adapted_text": "10 The doctor shared _____.",
                "options": [
                    {"text": "an encouraging new", "is_correct": 0},
                    {"text": "some encouraging news", "is_correct": 1},
                    {"text": "an encouraging news", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["some", "an"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 6: quiz-493 (A1) A/an, the, no article: The use of articles
    # =========================================================================
    "quiz-493": {
        "title": "Exercise 2",
        "instruction": "Choose a/an, the or no article to complete the sentences below.",
        "questions": [
            {
                "question_id": "4314",
                "adapted_text": "1 'Where is David?' 'He is relaxing in _____ garden.'",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 1},
                    {"text": "–", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["the", "a"],
            },
            {
                "question_id": "4315",
                "adapted_text": "2 Would you like to have _____ breakfast together tomorrow?",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "–", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["have", "lunch", "breakfast"],
            },
            {
                "question_id": "4316",
                "adapted_text": "3 Where do you plan to travel _____ next month?",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "–", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["next"],
            },
            {
                "question_id": "4319",
                "adapted_text": "4 My younger brother is learning to play _____ guitar.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 1},
                    {"text": "–", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["play", "the"],
            },
            {
                "question_id": "4321",
                "adapted_text": "5 My sister hopes to buy _____ modern laptop for college.",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "the", "is_correct": 0},
                    {"text": "–", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["buy", "a"],
            },
            {
                "question_id": "4317",
                "adapted_text": "6 Her favorite academic subject is _____ biology.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "–", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["favorite", "subject"],
            },
            {
                "question_id": "4320",
                "adapted_text": "7 _____ musicians in this orchestra are world-famous.",
                "options": [
                    {"text": "A", "is_correct": 0},
                    {"text": "The", "is_correct": 1},
                    {"text": "–", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["the"],
            },
            {
                "question_id": "4318",
                "adapted_text": "8 Aviation technology will evolve dramatically by _____ 2045.",
                "options": [
                    {"text": "the", "is_correct": 0},
                    {"text": "a", "is_correct": 0},
                    {"text": "–", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["by", "in"],
            },
            {
                "question_id": "4322",
                "adapted_text": "9 Young children are often fascinated by _____ wild animals.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "–", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["interested", "fascinated"],
            },
            {
                "question_id": "4323",
                "adapted_text": "10 A stranger entered the studio and borrowed _____ cameras without permission.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 1},
                    {"text": "–", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["the"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 7: quiz-445 (A1) At, in, on: Prepositions of place
    # =========================================================================
    "quiz-445": {
        "title": "Exercise 2",
        "instruction": "Choose the correct prepositions of place (at, in, on) to complete the sentences.",
        "questions": [
            {
                "question_id": "3870",
                "adapted_text": "1 The pharmacy is located _____ the corner of the avenue.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3871",
                "adapted_text": "2 Emily conducts research _____ Oxford University.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3872",
                "adapted_text": "3 There is a wonderful theatrical play performing _____ the opera house.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3873",
                "adapted_text": "4 'Where is Robert?' 'He is working _____ the basement.'",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3874",
                "adapted_text": "5 Employees often feel excited during their initial morning _____ school.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3875",
                "adapted_text": "6 Could you hand me the ceramic vase _____ the kitchen counter?",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3876",
                "adapted_text": "7 The meeting room is the third entrance _____ the left.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3877",
                "adapted_text": "8 The essays published _____ the magazine explore modern art.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3878",
                "adapted_text": "9 My cousin lived _____ Canada during winter.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3879",
                "adapted_text": "10 Passengers usually listen to music while travelling _____ the plane.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 8: quiz-442 (A1) At, in, on: Prepositions of time
    # =========================================================================
    "quiz-442": {
        "title": "Exercise 2",
        "instruction": "Choose the correct prepositions of time (at, in, on) to complete the sentences.",
        "questions": [
            {
                "question_id": "3840",
                "adapted_text": "1 The team must submit the report _____ sunset.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3841",
                "adapted_text": "2 Digital cameras gained widespread popularity _____ the 1990s.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3842",
                "adapted_text": "3 They plan to visit the gallery _____ Sunday afternoon.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3843",
                "adapted_text": "4 Farmers harvest ripe apples _____ the autumn.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3844",
                "adapted_text": "5 The downtown streets become peaceful _____ night.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3845",
                "adapted_text": "6 Our company will open a branch in Tokyo _____ 2028.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3846",
                "adapted_text": "7 The cultural festival begins _____ the 15th of March.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3847",
                "adapted_text": "8 The city buses stop running _____ midnight.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3848",
                "adapted_text": "9 Most governmental offices close _____ New Year's Day.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3849",
                "adapted_text": "10 Families gather together for dinner _____ Thanksgiving.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["at", "in", "on"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 9: quiz-713 (A1) Basic word order in English
    # =========================================================================
    "quiz-713": {
        "title": "Exercise 2",
        "instruction": "Choose the correct options to complete the sentences.",
        "questions": [
            {
                "question_id": "6091",
                "adapted_text": "1 Maria exercises _____.",
                "options": [
                    {"text": "her puppy by the lake every afternoon", "is_correct": 1},
                    {"text": "her puppy every afternoon by the lake", "is_correct": 0},
                    {"text": "every afternoon her puppy by the lake", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["every", "day", "afternoon"],
            },
            {
                "question_id": "6094",
                "adapted_text": "2 Jonathan accompanied _____.",
                "options": [
                    {"text": "his daughter to school this morning", "is_correct": 1},
                    {"text": "to school his daughter this morning", "is_correct": 0},
                    {"text": "this morning his daughter to school", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["this", "morning"],
            },
            {
                "question_id": "6095",
                "adapted_text": "3 Could you escort _____?",
                "options": [
                    {"text": "to the station the guest after the conference", "is_correct": 0},
                    {"text": "the guest after the conference to the station", "is_correct": 0},
                    {"text": "the guest to the station after the conference", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["after", "the"],
            },
            {
                "question_id": "6102",
                "adapted_text": "4 The tourists ______.",
                "options": [
                    {"text": "appreciated immensely the guided excursion", "is_correct": 0},
                    {"text": "appreciated the guided excursion immensely", "is_correct": 1},
                    {"text": "immensely appreciated the guided excursion", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["very", "much", "immensely"],
            },
            {
                "question_id": "6103",
                "adapted_text": "5 Clara _____.",
                "options": [
                    {"text": "purchased in Florence this painting last spring", "is_correct": 0},
                    {"text": "purchased this painting last spring in Florence", "is_correct": 0},
                    {"text": "purchased this painting in Florence last spring", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["last", "year", "spring"],
            },
            {
                "question_id": "6107",
                "adapted_text": "6 The technician ______.",
                "options": [
                    {"text": "will inform the supervisor promptly", "is_correct": 1},
                    {"text": "will inform promptly the supervisor", "is_correct": 0},
                    {"text": "promptly will inform the supervisor", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["promptly", "immediately"],
            },
            {
                "question_id": "6108",
                "adapted_text": "7 Elena ________.",
                "options": [
                    {"text": "deeply respects her colleagues", "is_correct": 0},
                    {"text": "respects her colleagues deeply", "is_correct": 1},
                    {"text": "respects deeply her colleagues", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["deeply", "very", "much"],
            },
            {
                "question_id": "6110",
                "adapted_text": "8 Samuel studied ______.",
                "options": [
                    {"text": "Spanish in Madrid during a university semester", "is_correct": 1},
                    {"text": "Spanish during a university semester in Madrid", "is_correct": 0},
                    {"text": "in Madrid Spanish during a university semester", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["during", "student", "program", "semester"],
            },
            {
                "question_id": "6112",
                "adapted_text": "9 The bank clerks ______.",
                "options": [
                    {"text": "always conclude work at 5.00 pm", "is_correct": 1},
                    {"text": "conclude always work at 5.00 pm", "is_correct": 0},
                    {"text": "conclude work at 5.00 pm always", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["always", "finish", "conclude"],
            },
            {
                "question_id": "6113",
                "adapted_text": "10 Oliver _____.",
                "options": [
                    {"text": "does not play very often basketball", "is_correct": 0},
                    {"text": "does not enjoy basketball very much", "is_correct": 1},
                    {"text": "does not enjoy very much basketball", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["very", "much", "often"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 10: quiz-490 (A1) Adverbs of manner or adjectives
    # =========================================================================
    "quiz-490": {
        "title": "Exercise 2",
        "instruction": "Complete the following sentences with the correct adjectives or adverbs of manner.",
        "questions": [
            {
                "question_id": "4284",
                "adapted_text": "1 The courier cyclist navigates through traffic very _____.",
                "options": [
                    {"text": "slow", "is_correct": 0},
                    {"text": "fastly", "is_correct": 0},
                    {"text": "fast", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["fast", "slow"],
            },
            {
                "question_id": "4285",
                "adapted_text": "2 The candidate completed _____.",
                "options": [
                    {"text": "successfully the interview", "is_correct": 0},
                    {"text": "the interview successfully", "is_correct": 1},
                    {"text": "successful the interview", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["easily", "successfully"],
            },
            {
                "question_id": "4286",
                "adapted_text": "3 The medical staff in the clinic labor very _____.",
                "options": [
                    {"text": "hard", "is_correct": 1},
                    {"text": "hardly", "is_correct": 0},
                    {"text": "good", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["hard", "hardly"],
            },
            {
                "question_id": "4287",
                "adapted_text": "4 Mr. Henderson is an extremely _____ architect.",
                "options": [
                    {"text": "well", "is_correct": 0},
                    {"text": "good", "is_correct": 1},
                    {"text": "goodly", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["good", "well"],
            },
            {
                "question_id": "4288",
                "adapted_text": "5 The orchestra violinist plays Mozart very _____.",
                "options": [
                    {"text": "good", "is_correct": 0},
                    {"text": "goodly", "is_correct": 0},
                    {"text": "well", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["well", "good"],
            },
            {
                "question_id": "4290",
                "adapted_text": "6 The witness explained _____.",
                "options": [
                    {"text": "accurately the incident", "is_correct": 0},
                    {"text": "the incident accurately", "is_correct": 1},
                    {"text": "the incident accurate", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["correctly", "accurately"],
            },
            {
                "question_id": "4289",
                "adapted_text": "7 The professor summarized the theory quite _____.",
                "options": [
                    {"text": "simple", "is_correct": 0},
                    {"text": "simplely", "is_correct": 0},
                    {"text": "simply", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["simply", "simple"],
            },
            {
                "question_id": "4292",
                "adapted_text": "8 The newlyweds reside _____ in Vienna.",
                "options": [
                    {"text": "happy", "is_correct": 0},
                    {"text": "happyly", "is_correct": 0},
                    {"text": "happily", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["happily", "happy"],
            },
            {
                "question_id": "4291",
                "adapted_text": "9 Following lunch, the programmers _____.",
                "options": [
                    {"text": "resolved the issue smoothly", "is_correct": 1},
                    {"text": "smoothly resolved the issue", "is_correct": 0},
                    {"text": "resolved the issue smooth", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["easily", "smoothly"],
            },
            {
                "question_id": "4293",
                "adapted_text": "10 The announcement was not delivered in _____ Spanish.",
                "options": [
                    {"text": "clearly", "is_correct": 0},
                    {"text": "clear", "is_correct": 1},
                    {"text": "well", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["clear", "clearly"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 11: quiz-481 (A1) Comparative adjectives
    # =========================================================================
    "quiz-481": {
        "title": "Exercise 2",
        "instruction": "Choose the correct comparative adjectives to complete these sentences.",
        "questions": [
            {
                "question_id": "4203",
                "adapted_text": "1 During the heavy storm, all the other passengers were far calmer than _____.",
                "options": [
                    {"text": "me", "is_correct": 1},
                    {"text": "mine", "is_correct": 0},
                    {"text": "my", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["than", "me"],
            },
            {
                "question_id": "4204",
                "adapted_text": "2 Our squad is quicker _____.",
                "options": [
                    {"text": "than them", "is_correct": 1},
                    {"text": "than their", "is_correct": 0},
                    {"text": "that them", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["than", "them"],
            },
            {
                "question_id": "4205",
                "adapted_text": "3 Travelling by express train is _____ flying by commercial plane.",
                "options": [
                    {"text": "relaxinger than", "is_correct": 0},
                    {"text": "more relaxing that", "is_correct": 0},
                    {"text": "more relaxing than", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["more", "than"],
            },
            {
                "question_id": "4207",
                "adapted_text": "4 The morning exam was more stressful than the afternoon quiz. The afternoon quiz is _____.",
                "options": [
                    {"text": "less stressful", "is_correct": 1},
                    {"text": "stressfulless", "is_correct": 0},
                    {"text": "less stressful than", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["less"],
            },
            {
                "question_id": "4206",
                "adapted_text": "5 The new assignment proved _____ the previous task.",
                "options": [
                    {"text": "more simple", "is_correct": 0},
                    {"text": "simpler than", "is_correct": 1},
                    {"text": "more simpler than", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["simpler", "than"],
            },
            {
                "question_id": "4208",
                "adapted_text": "6 The athlete is _____ than the challenger.",
                "options": [
                    {"text": "very faster", "is_correct": 0},
                    {"text": "much fast", "is_correct": 0},
                    {"text": "much faster", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["much", "faster"],
            },
            {
                "question_id": "4209",
                "adapted_text": "7 Liam is energetic, but Ethan is ____.",
                "options": [
                    {"text": "more energetic than", "is_correct": 0},
                    {"text": "more energetic", "is_correct": 1},
                    {"text": "energeticker", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["more", "energetic"],
            },
            {
                "question_id": "4210",
                "adapted_text": "8 The port is distant, but the airport is _____.",
                "options": [
                    {"text": "more far", "is_correct": 0},
                    {"text": "farer", "is_correct": 0},
                    {"text": "further", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["further"],
            },
            {
                "question_id": "4211",
                "adapted_text": "9 During the lunch break, the school cafeteria is always far _____ than the library.",
                "options": [
                    {"text": "noisy", "is_correct": 0},
                    {"text": "noisier", "is_correct": 1},
                    {"text": "more noisier", "is_correct": 0},
                ],
                "gaps": [],
                "target_tokens": ["noisier", "than"],
            },
            {
                "question_id": "4212",
                "adapted_text": "10 The critic provoked outrage when he claimed older artists are _____ younger creators.",
                "options": [
                    {"text": "creativeless than", "is_correct": 0},
                    {"text": "less creative that", "is_correct": 0},
                    {"text": "less creative than", "is_correct": 1},
                ],
                "gaps": [],
                "target_tokens": ["less", "creative", "than"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 12: quiz-424 (A1) A/an, plurals: Singular and plural forms
    # =========================================================================
    "quiz-424": {
        "title": "Exercise 1",
        "instruction": "Choose a/an for the following words.",
        "questions": [
            {
                "question_id": "3666",
                "adapted_text": "1 Look over there, it is {{gap_1}} eagle.",
                "options": [
                    {"text": "an", "is_correct": 1},
                    {"text": "a", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "a"],
            },
            {
                "question_id": "3667",
                "adapted_text": "2 We should buy {{gap_1}} wooden desk.",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "an"],
            },
            {
                "question_id": "3668",
                "adapted_text": "3 A smartphone is {{gap_1}} useful tool.",
                "options": [
                    {"text": "an", "is_correct": 0},
                    {"text": "a", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "an", "useful"],
            },
            {
                "question_id": "3669",
                "adapted_text": "4 My uncle works as {{gap_1}} plumber.",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "an"],
            },
            {
                "question_id": "3670",
                "adapted_text": "5 Did you pack {{gap_1}} extra umbrella?",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "an", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "a", "umbrella"],
            },
            {
                "question_id": "3671",
                "adapted_text": "6 She wants to be {{gap_1}} Italian chef.",
                "options": [
                    {"text": "an", "is_correct": 1},
                    {"text": "a", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "a"],
            },
            {
                "question_id": "3672",
                "adapted_text": "7 He bought {{gap_1}} warm scarf for winter.",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "an"],
            },
            {
                "question_id": "3673",
                "adapted_text": "8 Is your brother {{gap_1}} pilot?",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "an"],
            },
            {
                "question_id": "3674",
                "adapted_text": "9 There is {{gap_1}} unusual bird in the tree.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "an", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "a"],
            },
            {
                "question_id": "3675",
                "adapted_text": "10 The doctor requested {{gap_1}} honest explanation.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "an", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "a"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 13: quiz-471 (A1) A, some, any: Countable and uncountable nouns
    # =========================================================================
    "quiz-471": {
        "title": "Exercise 1",
        "instruction": "Choose a, some, any to complete the sentences below.",
        "questions": [
            {
                "question_id": "4112",
                "adapted_text": "1 The tourist asked for {{gap_1}} guidance regarding train departures.",
                "options": [
                    {"text": "some", "is_correct": 1},
                    {"text": "any", "is_correct": 0},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "some", "accepted_answers": ["some"]}],
                "target_tokens": ["some", "any", "an"],
            },
            {
                "question_id": "4114",
                "adapted_text": "2 Benjamin eats {{gap_1}} orange every morning.",
                "options": [
                    {"text": "some", "is_correct": 0},
                    {"text": "an", "is_correct": 1},
                    {"text": "any", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "some", "any"],
            },
            {
                "question_id": "4113",
                "adapted_text": "3 Could you spare a moment? I require {{gap_1}} assistance with the software.",
                "options": [
                    {"text": "an", "is_correct": 0},
                    {"text": "some", "is_correct": 1},
                    {"text": "any", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "some", "accepted_answers": ["some"]}],
                "target_tokens": ["some", "an", "any"],
            },
            {
                "question_id": "4116",
                "adapted_text": "4 The travelers do not possess {{gap_1}} local currency.",
                "options": [
                    {"text": "some", "is_correct": 0},
                    {"text": "any", "is_correct": 1},
                    {"text": "a", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "any", "accepted_answers": ["any"]}],
                "target_tokens": ["any", "some", "a"],
            },
            {
                "question_id": "4118",
                "adapted_text": "5 Could the barista add {{gap_1}} sugar to my tea, please?",
                "options": [
                    {"text": "any", "is_correct": 0},
                    {"text": "a", "is_correct": 0},
                    {"text": "some", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "some", "accepted_answers": ["some"]}],
                "target_tokens": ["some", "any", "a"],
            },
            {
                "question_id": "4115",
                "adapted_text": "6 Do you carry {{gap_1}} notebook in your bag?",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "any", "is_correct": 0},
                    {"text": "some", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "any", "some"],
            },
            {
                "question_id": "4117",
                "adapted_text": "7 They did not notice {{gap_1}} cars on the country road.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "some", "is_correct": 0},
                    {"text": "any", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "any", "accepted_answers": ["any"]}],
                "target_tokens": ["any", "some", "a"],
            },
            {
                "question_id": "4119",
                "adapted_text": "8 Does the librarian store {{gap_1}} historical newspapers in the reading room?",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "any", "is_correct": 1},
                    {"text": "some", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "any", "accepted_answers": ["any"]}],
                "target_tokens": ["any", "some", "a"],
            },
            {
                "question_id": "4120",
                "adapted_text": "9 Would the children enjoy {{gap_1}} biscuits with dessert?",
                "options": [
                    {"text": "any", "is_correct": 0},
                    {"text": "a", "is_correct": 0},
                    {"text": "some", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "some", "accepted_answers": ["some"]}],
                "target_tokens": ["some", "any", "a"],
            },
            {
                "question_id": "4121",
                "adapted_text": "10 Our tenant does not wish to keep {{gap_1}} cat in the apartment.",
                "options": [
                    {"text": "any", "is_correct": 0},
                    {"text": "a", "is_correct": 1},
                    {"text": "some", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "any", "some"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 14: quiz-492 (A1) A/an, the, no article: The use of articles
    # =========================================================================
    "quiz-492": {
        "title": "Exercise 1",
        "instruction": "Choose a/an, the or no article to complete the following sentences.",
        "questions": [
            {
                "question_id": "4308",
                "adapted_text": "1 Lucas baked bread and soup. {{gap_1}} soup was wonderfully fragrant.",
                "options": [
                    {"text": "A", "is_correct": 0},
                    {"text": "The", "is_correct": 1},
                    {"text": "-", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "The", "accepted_answers": ["The", "the"]}],
                "target_tokens": ["the", "a"],
            },
            {
                "question_id": "4305",
                "adapted_text": "2 That documentary is {{gap_1}} exciting film.",
                "options": [
                    {"text": "an", "is_correct": 1},
                    {"text": "the", "is_correct": 0},
                    {"text": "-", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "an", "accepted_answers": ["an"]}],
                "target_tokens": ["an", "the"],
            },
            {
                "question_id": "4307",
                "adapted_text": "3 We discovered {{gap_1}} wooden chest under the floorboards.",
                "options": [
                    {"text": "a", "is_correct": 1},
                    {"text": "the", "is_correct": 0},
                    {"text": "-", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "the"],
            },
            {
                "question_id": "4312",
                "adapted_text": "4 Nutritionists believe that {{gap_1}} green tea improves concentration.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "-", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "-", "accepted_answers": ["-", "no article"]}],
                "target_tokens": ["-", "the", "a"],
            },
            {
                "question_id": "4304",
                "adapted_text": "5 Daniel does not own {{gap_1}} bicycle.",
                "options": [
                    {"text": "the", "is_correct": 0},
                    {"text": "a", "is_correct": 1},
                    {"text": "-", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "the"],
            },
            {
                "question_id": "4309",
                "adapted_text": "6 Could you reach for {{gap_1}} salt on the counter?",
                "options": [
                    {"text": "the", "is_correct": 1},
                    {"text": "a", "is_correct": 0},
                    {"text": "-", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "the", "accepted_answers": ["the"]}],
                "target_tokens": ["the", "a"],
            },
            {
                "question_id": "4310",
                "adapted_text": "7 {{gap_1}} mayor greeted the citizens at the festival.",
                "options": [
                    {"text": "-", "is_correct": 0},
                    {"text": "A", "is_correct": 0},
                    {"text": "The", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "The", "accepted_answers": ["The", "the"]}],
                "target_tokens": ["the", "a"],
            },
            {
                "question_id": "4306",
                "adapted_text": "8 Her older cousin is {{gap_1}} civil engineer.",
                "options": [
                    {"text": "-", "is_correct": 0},
                    {"text": "a", "is_correct": 1},
                    {"text": "the", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "a", "accepted_answers": ["a"]}],
                "target_tokens": ["a", "the"],
            },
            {
                "question_id": "4313",
                "adapted_text": "9 Zoologists note that {{gap_1}} wolves live in organized packs.",
                "options": [
                    {"text": "a", "is_correct": 0},
                    {"text": "the", "is_correct": 0},
                    {"text": "-", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "-", "accepted_answers": ["-", "no article"]}],
                "target_tokens": ["-", "the", "a"],
            },
            {
                "question_id": "4311",
                "adapted_text": "10 The taxi dropped the passengers off at {{gap_1}} railway terminal.",
                "options": [
                    {"text": "-", "is_correct": 0},
                    {"text": "the", "is_correct": 1},
                    {"text": "an", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "the", "accepted_answers": ["the"]}],
                "target_tokens": ["the", "an"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 15: quiz-427 (A1) Adjectives: Old, interesting, expensive, etc.
    # =========================================================================
    "quiz-427": {
        "title": "Exercise 1",
        "instruction": "Choose the correct forms with adjectives to complete the following sentences.",
        "questions": [
            {
                "question_id": "3696",
                "adapted_text": "1 In that bright lighting, your portraits {{gap_1}}.",
                "options": [
                    {"text": "look fantastic", "is_correct": 1},
                    {"text": "fantastic look", "is_correct": 0},
                    {"text": "look fantastics", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "look fantastic", "accepted_answers": ["look fantastic"]}],
                "target_tokens": ["look", "fantastic"],
            },
            {
                "question_id": "3697",
                "adapted_text": "2 Those artifacts are {{gap_1}}.",
                "options": [
                    {"text": "valuable treasures", "is_correct": 1},
                    {"text": "treasures valuables", "is_correct": 0},
                    {"text": "treasures valuable", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "valuable treasures", "accepted_answers": ["valuable treasures"]}],
                "target_tokens": ["valuable", "treasures"],
            },
            {
                "question_id": "3698",
                "adapted_text": "3 {{gap_1}} about the recent promotion?",
                "options": [
                    {"text": "Is satisfied he", "is_correct": 0},
                    {"text": "Is he satisfied", "is_correct": 1},
                    {"text": "Is he satisfieds", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "Is he satisfied", "accepted_answers": ["Is he satisfied"]}],
                "target_tokens": ["is", "he", "satisfied"],
            },
            {
                "question_id": "3699",
                "adapted_text": "4 Maria obtained {{gap_1}}.",
                "options": [
                    {"text": "a career exciting", "is_correct": 0},
                    {"text": "an exciting career", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "an exciting career", "accepted_answers": ["an exciting career"]}],
                "target_tokens": ["exciting", "career"],
            },
            {
                "question_id": "3700",
                "adapted_text": "5 Take a short break. You {{gap_1}}.",
                "options": [
                    {"text": "appear exhausted", "is_correct": 1},
                    {"text": "exhausted appear", "is_correct": 0},
                    {"text": "taste exhausted", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "appear exhausted", "accepted_answers": ["appear exhausted"]}],
                "target_tokens": ["appear", "exhausted", "look"],
            },
            {
                "question_id": "3701",
                "adapted_text": "6 The weekend performances {{gap_1}}.",
                "options": [
                    {"text": "extraordinary were", "is_correct": 0},
                    {"text": "were extraordinary", "is_correct": 1},
                    {"text": "were extraordinaries", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "were extraordinary", "accepted_answers": ["were extraordinary"]}],
                "target_tokens": ["were", "extraordinary", "are"],
            },
            {
                "question_id": "3702",
                "adapted_text": "7 Sarah faces difficulties at work. {{gap_1}}?",
                "options": [
                    {"text": "Are acceptables her results", "is_correct": 0},
                    {"text": "Are her results acceptable", "is_correct": 1},
                    {"text": "Are acceptable her results", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "Are her results acceptable", "accepted_answers": ["Are her results acceptable"]}],
                "target_tokens": ["are", "her", "results", "acceptable"],
            },
            {
                "question_id": "3703",
                "adapted_text": "8 The architect's proposal {{gap_1}}.",
                "options": [
                    {"text": "practical sounds", "is_correct": 0},
                    {"text": "smells practical", "is_correct": 0},
                    {"text": "sounds practical", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "sounds practical", "accepted_answers": ["sounds practical"]}],
                "target_tokens": ["sounds", "practical"],
            },
            {
                "question_id": "3704",
                "adapted_text": "9 The freshly baked pastries {{gap_1}}.",
                "options": [
                    {"text": "are delicious", "is_correct": 1},
                    {"text": "are deliciouses", "is_correct": 0},
                    {"text": "delicious are", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "are delicious", "accepted_answers": ["are delicious"]}],
                "target_tokens": ["are", "delicious"],
            },
            {
                "question_id": "3705",
                "adapted_text": "10 The autumn leaves {{gap_1}}.",
                "options": [
                    {"text": "golden are", "is_correct": 0},
                    {"text": "are goldens", "is_correct": 0},
                    {"text": "are golden", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "are golden", "accepted_answers": ["are golden"]}],
                "target_tokens": ["are", "golden"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 16: quiz-444 (A1) At, in, on: Prepositions of place
    # =========================================================================
    "quiz-444": {
        "title": "Exercise 1",
        "instruction": "Choose at, in, on to complete the sentences.",
        "questions": [
            {
                "question_id": "3860",
                "adapted_text": "1 The committee gathered {{gap_1}} the conference desk.",
                "options": [
                    {"text": "in", "is_correct": 0},
                    {"text": "at", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3861",
                "adapted_text": "2 Liam plans to study for six months {{gap_1}} Lisbon.",
                "options": [
                    {"text": "on", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "at", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3862",
                "adapted_text": "3 The butter is not {{gap_1}} the cupboard. Where did you place it?",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                ],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3863",
                "adapted_text": "4 Is the dentistry suite situated {{gap_1}} the fourth floor?",
                "options": [
                    {"text": "on", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                    {"text": "at", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3864",
                "adapted_text": "5 Why did someone leave those documents {{gap_1}} the dining table?",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                    {"text": "in", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3865",
                "adapted_text": "6 Kindly store the winter blankets {{gap_1}} the wooden chest.",
                "options": [
                    {"text": "at", "is_correct": 0},
                    {"text": "in", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3866",
                "adapted_text": "7 Will the doctor be {{gap_1}} the clinic this afternoon?",
                "options": [
                    {"text": "at the", "is_correct": 0},
                    {"text": "at", "is_correct": 1},
                    {"text": "in the", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3867",
                "adapted_text": "8 The director spoke to the attendees {{gap_1}} the reception yesterday.",
                "options": [
                    {"text": "at", "is_correct": 1},
                    {"text": "on", "is_correct": 0},
                    {"text": "in", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3868",
                "adapted_text": "9 We enjoy hiking in mountains, but we prefer relaxing {{gap_1}} a hot bath.",
                "options": [
                    {"text": "in", "is_correct": 1},
                    {"text": "at", "is_correct": 0},
                    {"text": "on", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3869",
                "adapted_text": "10 Text me when your group gets {{gap_1}} the morning ferry.",
                "options": [
                    {"text": "in", "is_correct": 0},
                    {"text": "on", "is_correct": 1},
                    {"text": "at", "is_correct": 0},
                ],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 17: quiz-425 (A1) A/an, plurals: Singular and plural forms
    # =========================================================================
    "quiz-425": {
        "title": "Exercise 2",
        "instruction": "Write the plurals of the following singular words.",
        "questions": [
            {
                "question_id": "3676",
                "adapted_text": "1 a dictionary ⇒ {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "dictionaries", "accepted_answers": ["dictionaries"]}],
                "target_tokens": ["dictionaries"],
            },
            {
                "question_id": "3677",
                "adapted_text": "2 a beach ⇒ {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "beaches", "accepted_answers": ["beaches"]}],
                "target_tokens": ["beaches"],
            },
            {
                "question_id": "3678",
                "adapted_text": "3 a bridge ⇒ {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "bridges", "accepted_answers": ["bridges"]}],
                "target_tokens": ["bridges"],
            },
            {
                "question_id": "3679",
                "adapted_text": "4 a brave woman ⇒ brave {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "women", "accepted_answers": ["women"]}],
                "target_tokens": ["women"],
            },
            {
                "question_id": "3680",
                "adapted_text": "5 one tooth ⇒ two {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "teeth", "accepted_answers": ["teeth"]}],
                "target_tokens": ["teeth"],
            },
            {
                "question_id": "3681",
                "adapted_text": "6 a wooden box ⇒ wooden {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "boxes", "accepted_answers": ["boxes"]}],
                "target_tokens": ["boxes"],
            },
            {
                "question_id": "3682",
                "adapted_text": "7 a silver match ⇒ silver {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "matches", "accepted_answers": ["matches"]}],
                "target_tokens": ["matches"],
            },
            {
                "question_id": "3683",
                "adapted_text": "8 a fast laptop ⇒ fast {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "laptops", "accepted_answers": ["laptops"]}],
                "target_tokens": ["laptops"],
            },
            {
                "question_id": "3684",
                "adapted_text": "9 a beautiful painting ⇒ beautiful {{gap_1}}",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "paintings", "accepted_answers": ["paintings"]}],
                "target_tokens": ["paintings"],
            },
            {
                "question_id": "3685",
                "adapted_text": "10 One bottle of water ⇒ two {{gap_1}} of water",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "bottles", "accepted_answers": ["bottles"]}],
                "target_tokens": ["bottles"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 18: quiz-473 (A1) A, some, any: Countable and uncountable nouns
    # =========================================================================
    "quiz-473": {
        "title": "Exercise 3",
        "instruction": "Complete the sentences using a, some, any and the words in the box.",
        "questions": [
            {
                "question_id": "4132",
                "adapted_text": "1 The historians explored {{gap_1}} along the coast of Greece.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "some ancient temples", "accepted_answers": ["some ancient temples"]}],
                "target_tokens": ["some"],
            },
            {
                "question_id": "4133",
                "adapted_text": "2 Arthur owns a modern camera, but he does not possess {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "any lenses", "accepted_answers": ["any lenses"]}],
                "target_tokens": ["any"],
            },
            {
                "question_id": "4134",
                "adapted_text": "3 I am struggling with the application. Could you offer me {{gap_1}}?",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "some assistance", "accepted_answers": ["some assistance"]}],
                "target_tokens": ["some"],
            },
            {
                "question_id": "4135",
                "adapted_text": "4 The guests ordered fresh pasta and {{gap_1}} for supper.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "some soup", "accepted_answers": ["some soup"]}],
                "target_tokens": ["some"],
            },
            {
                "question_id": "4136",
                "adapted_text": "5 The speaker paused for the audience. Are there {{gap_1}}?",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "any comments", "accepted_answers": ["any comments"]}],
                "target_tokens": ["any"],
            },
            {
                "question_id": "4137",
                "adapted_text": "6 The driver experienced {{gap_1}} with the engine on the motorway.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "a breakdown", "accepted_answers": ["a breakdown"]}],
                "target_tokens": ["a"],
            },
            {
                "question_id": "4139",
                "adapted_text": "7 The runners were thirsty after the marathon. They requested {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "some juice", "accepted_answers": ["some juice"]}],
                "target_tokens": ["some"],
            },
            {
                "question_id": "4138",
                "adapted_text": "8 Do you have {{gap_1}}? The bus ticket machine requires metal coins.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "any change", "accepted_answers": ["any change"]}],
                "target_tokens": ["any", "change"],
            },
            {
                "question_id": "4140",
                "adapted_text": "9 The chef wanted to bake a fruit cake, but the pantry lacked {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "any flour", "accepted_answers": ["any flour"]}],
                "target_tokens": ["any"],
            },
            {
                "question_id": "4141",
                "adapted_text": "10 Can the receptionist communicate in {{gap_1}}?",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "any European languages", "accepted_answers": ["any European languages"]}],
                "target_tokens": ["any"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 19: quiz-446 (A1) At, in, on: Prepositions of place
    # =========================================================================
    "quiz-446": {
        "title": "Exercise 3",
        "instruction": "Complete the sentences using the correct prepositions of place: at, in, on.",
        "questions": [
            {
                "question_id": "3880",
                "adapted_text": "1 I am waiting {{gap_1}} the pharmacy counter. Can I pick up anything for you?",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3881",
                "adapted_text": "2 Oliver placed the smartphone {{gap_1}} the dining room table.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3882",
                "adapted_text": "3 The jeweler stores valuable diamonds {{gap_1}} a secure safe.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3883",
                "adapted_text": "4 The family arranged an afternoon celebration {{gap_1}} the river bank.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3884",
                "adapted_text": "5 Who is the guard standing {{gap_1}} the entrance?",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "at", "accepted_answers": ["at"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3885",
                "adapted_text": "6 The fresh strawberries are stored {{gap_1}} the refrigerator.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3886",
                "adapted_text": "7 Most passengers find it difficult to concentrate while {{gap_1}} the subway.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3887",
                "adapted_text": "8 The lecture hall is located {{gap_1}} the third floor.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "on", "accepted_answers": ["on"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3888",
                "adapted_text": "9 Several delegates {{gap_1}} the auditorium raised objections.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
            {
                "question_id": "3889",
                "adapted_text": "10 Agricultural exports {{gap_1}} South America continue to expand.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "in", "accepted_answers": ["in"]}],
                "target_tokens": ["at", "in", "on"],
            },
        ],
    },

    # =========================================================================
    # EXERCISE 20: quiz-714 (A1) Basic word order in English
    # =========================================================================
    "quiz-714": {
        "title": "Exercise 3",
        "instruction": "Write sentences using the words in the correct position.",
        "questions": [
            {
                "question_id": "6097",
                "adapted_text": "1 a delicious dinner / cooked / yesterday / they / at home ⇒ They {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "cooked a delicious dinner at home yesterday", "accepted_answers": ["cooked a delicious dinner at home yesterday"]}],
                "target_tokens": ["at", "home", "yesterday"],
            },
            {
                "question_id": "6098",
                "adapted_text": "2 the briefcase / this morning / on the train / left / She ⇒ She {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "left the briefcase on the train this morning", "accepted_answers": ["left the briefcase on the train this morning"]}],
                "target_tokens": ["this", "morning"],
            },
            {
                "question_id": "6099",
                "adapted_text": "3 regularly / Thomas / rides / to the campus / a bicycle ⇒ Thomas {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "regularly rides a bicycle to the campus", "accepted_answers": ["regularly rides a bicycle to the campus"]}],
                "target_tokens": ["regularly"],
            },
            {
                "question_id": "6100",
                "adapted_text": "4 must deliver / we / the package / to the post office / before noon ⇒ We {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "must deliver the package to the post office before noon", "accepted_answers": ["must deliver the package to the post office before noon"]}],
                "target_tokens": ["to", "the"],
            },
            {
                "question_id": "6101",
                "adapted_text": "5 are / rarely / on weekends / the engineers / in the workshop ⇒ The engineers {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "are rarely in the workshop on weekends", "accepted_answers": ["are rarely in the workshop on weekends"]}],
                "target_tokens": ["are", "rarely"],
            },
            {
                "question_id": "6104",
                "adapted_text": "6 It / consistently / very windy / near the coast / in November / is ⇒ It {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "is consistently very windy near the coast in November", "accepted_answers": ["is consistently very windy near the coast in November"]}],
                "target_tokens": ["is", "very"],
            },
            {
                "question_id": "6105",
                "adapted_text": "7 practice / basketball / after classes / in the gym / They ⇒ They {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "practice basketball in the gym after classes", "accepted_answers": ["practice basketball in the gym after classes"]}],
                "target_tokens": ["after"],
            },
            {
                "question_id": "6106",
                "adapted_text": "8 frequently / He / green tea / drinks / in the morning ⇒ He {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "frequently drinks green tea in the morning", "accepted_answers": ["frequently drinks green tea in the morning"]}],
                "target_tokens": ["in", "the", "morning"],
            },
            {
                "question_id": "6109",
                "adapted_text": "9 encountered / at a conference / in 2015 / Robert / his business partner ⇒ Robert {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "encountered his business partner at a conference in 2015", "accepted_answers": ["encountered his business partner at a conference in 2015"]}],
                "target_tokens": ["at", "in"],
            },
            {
                "question_id": "6111",
                "adapted_text": "10 usually / We / online seminars / attend / on Thursdays ⇒ We {{gap_1}}.",
                "options": [],
                "gaps": [{"order": 1, "correct_answer": "usually attend online seminars on Thursdays", "accepted_answers": ["usually attend online seminars on Thursdays"]}],
                "target_tokens": ["on"],
            },
        ],
    },
}

