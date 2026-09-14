import re


# =========================================================
# SERVICE KEYWORDS
# =========================================================

SERVICE_KEYWORDS = {

    "Plumbing": [
        "pipe",
        "leak",
        "leaking",
        "tap",
        "faucet",
        "water",
        "drain",
        "toilet",
        "sink",
        "plumber"
    ],

    "Electrical": [
        "electric",
        "electricity",
        "wire",
        "wiring",
        "switch",
        "socket",
        "fan",
        "light",
        "power",
        "current"
    ],

    "Cleaning": [
        "clean",
        "cleaning",
        "dirty",
        "dust",
        "house cleaning",
        "deep cleaning",
        "floor",
        "bathroom cleaning"
    ],

    "Gardening": [
        "garden",
        "gardening",
        "plants",
        "plant",
        "grass",
        "lawn",
        "tree",
        "pruning",
        "watering"
    ],

    "Carpentry": [
        "carpenter",
        "wood",
        "furniture",
        "table",
        "chair",
        "door",
        "cupboard",
        "wardrobe",
        "shelf"
    ],

    "Packers & Movers": [
        "move",
        "moving",
        "shift",
        "shifting",
        "packers",
        "movers",
        "packing",
        "relocation",
        "house move"
    ],

    # =====================================================
    # NEW: CARETAKING
    # =====================================================

    "Caretaking": [
        "caretaker",
        "care taker",
        "caretaking",
        "elder care",
        "elderly care",
        "old age care",
        "senior care",
        "patient care",
        "home care",
        "child care",
        "baby care",
        "nursing care",
        "caregiver",
        "care giver"
    ],

    # =====================================================
    # NEW: DRIVING
    # =====================================================

    "Driving": [
        "driver",
        "driving",
        "drive",
        "car driver",
        "cab driver",
        "vehicle driver",
        "chauffeur",
        "driving service"
    ]
}


# =========================================================
# PROBLEM KEYWORDS
# =========================================================

PROBLEM_KEYWORDS = {

    "Plumbing": {

        "Leakage / Pipe Repair": [
            "leak",
            "leaking",
            "pipe",
            "water leakage"
        ],

        "Tap / Faucet Repair": [
            "tap",
            "faucet"
        ],

        "Drainage Problem": [
            "drain",
            "blocked drain",
            "drainage"
        ]
    },


    "Electrical": {

        "Wiring / Electrical Repair": [
            "wire",
            "wiring",
            "current",
            "electricity"
        ],

        "Switch / Socket Repair": [
            "switch",
            "socket"
        ],

        "Fan / Light Repair": [
            "fan",
            "light"
        ]
    },


    "Cleaning": {

        "House Cleaning": [
            "house cleaning",
            "clean house",
            "home cleaning"
        ],

        "Deep Cleaning": [
            "deep cleaning",
            "deep clean"
        ],

        "General Cleaning": [
            "clean",
            "dirty",
            "dust",
            "floor",
            "bathroom"
        ]
    },


    "Gardening": {

        "Garden Maintenance": [
            "garden",
            "gardening",
            "lawn",
            "grass"
        ],

        "Plant Care": [
            "plant",
            "plants",
            "watering"
        ],

        "Tree Maintenance": [
            "tree",
            "pruning"
        ]
    },


    "Carpentry": {

        "Furniture Repair": [
            "furniture",
            "table",
            "chair",
            "wardrobe",
            "cupboard"
        ],

        "Door / Wood Repair": [
            "door",
            "wood"
        ]
    },


    "Packers & Movers": {

        "House Shifting": [
            "move",
            "moving",
            "shift",
            "shifting",
            "relocation"
        ],

        "Packing": [
            "pack",
            "packing",
            "packers"
        ]
    },


    # =====================================================
    # NEW: CARETAKING PROBLEMS
    # =====================================================

    "Caretaking": {

        "Elderly Care": [
            "elder care",
            "elderly care",
            "old age care",
            "senior care",
            "old person",
            "elderly person",
            "senior citizen"
        ],

        "Patient Care": [
            "patient care",
            "patient",
            "nursing care",
            "sick person",
            "medical care"
        ],

        "Child Care": [
            "child care",
            "baby care",
            "childcare",
            "babysitting",
            "baby sitting",
            "children care"
        ],

        "Home Care": [
            "home care",
            "caregiver",
            "care giver",
            "caretaker"
        ]
    },


    # =====================================================
    # NEW: DRIVING PROBLEMS
    # =====================================================

    "Driving": {

        "Personal Driver": [
            "driver",
            "personal driver",
            "car driver",
            "chauffeur"
        ],

        "Vehicle Driving": [
            "driving",
            "drive",
            "vehicle driver"
        ],

        "Scheduled Driving": [
            "tomorrow",
            "today",
            "for tomorrow",
            "for today",
            "daily driver",
            "full time driver"
        ]
    }
}


# =========================================================
# URGENCY KEYWORDS
# =========================================================

URGENCY_KEYWORDS = {

    "High": [
        "urgent",
        "urgently",
        "emergency",
        "immediately",
        "as soon as possible",
        "right now",
        "critical"
    ],

    "Medium": [
        "soon",
        "today",
        "quickly",
        "fast"
    ],

    "Low": [
        "later",
        "tomorrow",
        "next week",
        "whenever"
    ]
}


# =========================================================
# COMPLEX SERVICE KEYWORDS
# =========================================================

COMPLEX_SERVICE_KEYWORDS = {

    "Packers & Movers": [
        "move",
        "moving",
        "shift",
        "shifting",
        "relocation",
        "packers",
        "movers",
        "house move"
    ]
}


# =========================================================
# COMPLEX SERVICE COMPONENTS
# =========================================================

COMPLEX_COMPONENTS = {

    "Packers & Movers": [
        "Packing",
        "Loading",
        "Transportation",
        "Unloading"
    ]
}


# =========================================================
# FIND MATCHING KEYWORD
# =========================================================

def find_matching_keyword(text, keywords):

    for keyword in keywords:

        if keyword in text:
            return keyword

    return None


# =========================================================
# DETECT COMPLEX SERVICE
# =========================================================

def detect_complex_service(text):

    for service, keywords in COMPLEX_SERVICE_KEYWORDS.items():

        if find_matching_keyword(
            text,
            keywords
        ):

            property_match = re.search(
                r"\b(1BHK|2BHK|3BHK|4BHK|5BHK)\b",
                text,
                re.IGNORECASE
            )

            route_match = re.search(
                r"\bfrom\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+"
                r"to\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
                text,
                re.IGNORECASE
            )

            hindi_route_match = re.search(
                r"([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*)\s+से\s+"
                r"([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*)",
                text
            )

            destination_match = re.search(
                r"\bto\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
                text,
                re.IGNORECASE
            )

            property_type = None
            origin = None
            destination = None

            if property_match:

                property_type = (
                    property_match.group(1).upper()
                )

            if route_match:

                origin = (
                    route_match.group(1).strip()
                )

                destination = (
                    route_match.group(2).strip()
                )

            elif hindi_route_match:

                origin = (
                    hindi_route_match.group(1).strip()
                )

                destination = (
                    hindi_route_match.group(2).strip()
                )

            elif destination_match:

                destination = (
                    destination_match.group(1).strip()
                )

            return {
                "request_type": "complex_service",
                "service": service,
                "property_type": property_type,
                "origin": origin,
                "destination": destination,
                "required_components": (
                    COMPLEX_COMPONENTS[service]
                ),
                "team_required": True
            }

    return None


# =========================================================
# GET COMPLEX SERVICE RESOURCES
# =========================================================

def get_complex_resources(complex_request):

    if not complex_request:

        return None

    service = complex_request["service"]

    if service == "Packers & Movers":

        property_type = (
            complex_request["property_type"]
        )

        if property_type == "1BHK":

            team_size = 2

        elif property_type == "2BHK":

            team_size = 3

        elif property_type == "3BHK":

            team_size = 4

        elif property_type in [
            "4BHK",
            "5BHK"
        ]:

            team_size = 5

        else:

            team_size = 3

        return {
            "team_size": team_size,
            "vehicle_required": True,
            "resources": [
                "Packing",
                "Loading",
                "Transportation",
                "Unloading"
            ]
        }

    return None


# =========================================================
# ANALYZE CUSTOMER REQUEST
# =========================================================

def analyze_request(
    request_text,
    language="English"
):

    text = request_text.lower().strip()


    # =====================================================
    # TELUGU TRANSLATION KEYWORDS
    # =====================================================

    TELUGU_KEYWORDS = {

        # -------------------------------------------------
        # PLUMBING
        # -------------------------------------------------

        "పైపు": "pipe",
        "పైపులైన్": "pipe",
        "లీక్": "leak",
        "లీక్ అవుతోంది": "leak",
        "నీరు": "water",
        "నీటి": "water",
        "కుళాయి": "tap",
        "ట్యాప్": "tap",
        "ఫాసెట్": "faucet",
        "నాళం": "drain",
        "డ్రెయిన్": "drain",
        "టాయిలెట్": "toilet",
        "మరుగుదొడ్డి": "toilet",
        "సింక్": "sink",
        "ప్లంబర్": "plumber",
        "ప్లంబింగ్": "plumbing",


        # -------------------------------------------------
        # ELECTRICAL
        # -------------------------------------------------

        "విద్యుత్": "electricity",
        "కరెంట్": "current",
        "కరెంటు": "current",
        "వైర్": "wire",
        "వైరింగ్": "wiring",
        "స్విచ్": "switch",
        "సాకెట్": "socket",
        "ఫ్యాన్": "fan",
        "లైట్": "light",
        "బల్బ్": "light",
        "ఎలక్ట్రికల్": "electric",
        "ఎలక్ట్రీషియన్": "electrician",
        "విద్యుత్ సమస్య": "electricity",


        # -------------------------------------------------
        # CLEANING
        # -------------------------------------------------

        "శుభ్రం": "clean",
        "శుభ్రపరచడం": "cleaning",
        "శుభ్రపరచాలి": "cleaning",
        "శుభ్రం చేయాలి": "cleaning",
        "ఇంటి శుభ్రత": "house cleaning",
        "ఇల్లు శుభ్రం": "clean house",
        "డీప్ క్లీనింగ్": "deep cleaning",
        "లోతైన శుభ్రత": "deep cleaning",
        "దుమ్ము": "dust",
        "మురికి": "dirty",
        "నేల": "floor",
        "బాత్రూమ్": "bathroom cleaning",


        # -------------------------------------------------
        # GARDENING
        # -------------------------------------------------

        "తోట": "garden",
        "తోటను": "garden",
        "తోటపని": "gardening",
        "తోట నిర్వహణ": "gardening",
        "మొక్క": "plant",
        "మొక్కలు": "plants",
        "గడ్డి": "grass",
        "లాన్": "lawn",
        "చెట్టు": "tree",
        "చెట్లు": "tree",
        "కత్తిరింపు": "pruning",
        "నీరు పోయడం": "watering",
        "మొక్కల సంరక్షణ": "plant care",


        # -------------------------------------------------
        # CARPENTRY
        # -------------------------------------------------

        "వడ్రంగి": "carpenter",
        "వడ్రంగి పని": "carpentry",
        "చెక్క": "wood",
        "ఫర్నిచర్": "furniture",
        "బల్ల": "table",
        "టేబుల్": "table",
        "కుర్చీ": "chair",
        "తలుపు": "door",
        "అల్మారా": "cupboard",
        "వార్డ్‌రోబ్": "wardrobe",
        "షెల్ఫ్": "shelf",
        "చెక్క మరమ్మత్తు": "wood repair",
        "ఫర్నిచర్ మరమ్మత్తు": "furniture repair",
        "వడ్రంగిపని": "carpentry",


        # -------------------------------------------------
        # PACKERS & MOVERS
        # -------------------------------------------------

        "మూవింగ్": "moving",
        "మూవ్": "move",
        "షిఫ్ట్": "shift",
        "షిఫ్టింగ్": "shifting",
        "తరలింపు": "relocation",
        "ప్యాకింగ్": "packing",
        "ప్యాకర్స్": "packers",
        "మూవర్స్": "movers",
        "ప్యాకర్స్ అండ్ మూవర్స్": "packers movers",
        "ప్యాకర్స్ మరియు మూవర్స్": "packers movers",
        "ఇల్లు మార్చాలి": "house move",
        "ఇల్లు తరలించాలి": "relocation",
        "ఇంటి తరలింపు": "relocation",


        # =================================================
        # NEW: CARETAKING
        # =================================================

        "కేర్‌టేకర్": "caretaker",
        "కేర్ టేకర్": "caretaker",
        "కేర్‌టేకింగ్": "caretaking",
        "సంరక్షణ": "caregiving",
        "వృద్ధుల సంరక్షణ": "elderly care",
        "వృద్ధుల": "elderly care",
        "వృద్ధుడు": "elderly care",
        "వృద్ధురాలు": "elderly care",
        "వృద్ధుల కోసం": "elderly care",
        "వృద్ధ తల్లిదండ్రులు": "elderly care",
        "తల్లిదండ్రుల సంరక్షణ": "elderly care",
        "రోగి సంరక్షణ": "patient care",
        "రోగి": "patient",
        "పిల్లల సంరక్షణ": "child care",
        "పిల్లల": "child care",
        "బిడ్డ సంరక్షణ": "baby care",
        "బిడ్డ": "baby care",
        "ఇంటి సంరక్షణ": "home care",
        "కేర్ గివర్": "caregiver",


        # =================================================
        # NEW: DRIVING
        # =================================================

        "డ్రైవర్": "driver",
        "డ్రైవింగ్": "driving",
        "డ్రైవర్ కావాలి": "driver",
        "కారు డ్రైవర్": "car driver",
        "వ్యక్తిగత డ్రైవర్": "personal driver",
        "చోదకుడు": "driver",
        "వాహన డ్రైవర్": "vehicle driver",
        "డ్రైవింగ్ సేవ": "driving service"
    }


    # =====================================================
    # HINDI TRANSLATION KEYWORDS
    # =====================================================

    HINDI_KEYWORDS = {

        # -------------------------------------------------
        # PLUMBING
        # -------------------------------------------------

        "पाइप": "pipe",
        "पाइपलाइन": "pipe",
        "लीक": "leak",
        "लीक हो रहा": "leak",
        "लीक हो रही": "leak",
        "पानी": "water",
        "नल": "tap",
        "टैप": "tap",
        "फव्वारा": "faucet",
        "नाली": "drain",
        "शौचालय": "toilet",
        "टॉयलेट": "toilet",
        "सिंक": "sink",
        "प्लंबर": "plumber",
        "प्लंबिंग": "plumbing",


        # -------------------------------------------------
        # ELECTRICAL
        # -------------------------------------------------

        "बिजली": "electricity",
        "बिजली की समस्या": "electricity",
        "बिजली की दिक्कत": "electricity",
        "तार": "wire",
        "वायर": "wire",
        "वायरिंग": "wiring",
        "स्विच": "switch",
        "सॉकेट": "socket",
        "पंखा": "fan",
        "लाइट": "light",
        "बत्ती": "light",
        "करंट": "current",
        "इलेक्ट्रिकल": "electric",
        "इलेक्ट्रीशियन": "electrician",


        # -------------------------------------------------
        # CLEANING
        # -------------------------------------------------

        "साफ": "clean",
        "सफाई": "cleaning",
        "साफ करना": "cleaning",
        "साफ करवाना": "cleaning",
        "घर की सफाई": "house cleaning",
        "घर साफ": "clean house",
        "गहरी सफाई": "deep cleaning",
        "डीप क्लीनिंग": "deep cleaning",
        "धूल": "dust",
        "गंदा": "dirty",
        "गंदगी": "dirty",
        "फर्श": "floor",
        "बाथरूम": "bathroom cleaning",


        # -------------------------------------------------
        # GARDENING
        # -------------------------------------------------

        "बगीचा": "garden",
        "बगीचे": "garden",
        "बगीचे की देखभाल": "gardening",
        "बाग": "garden",
        "बागवानी": "gardening",
        "पौधा": "plant",
        "पौधे": "plants",
        "घास": "grass",
        "लॉन": "lawn",
        "पेड़": "tree",
        "पेड़ों": "tree",
        "छंटाई": "pruning",
        "पानी देना": "watering",
        "पौधों की देखभाल": "plant care",


        # -------------------------------------------------
        # CARPENTRY
        # -------------------------------------------------

        "बढ़ई": "carpenter",
        "बढ़ई का काम": "carpentry",
        "लकड़ी": "wood",
        "फर्नीचर": "furniture",
        "मेज": "table",
        "कुर्सी": "chair",
        "दरवाजा": "door",
        "दरवाज़ा": "door",
        "अलमारी": "cupboard",
        "वार्डरोब": "wardrobe",
        "शेल्फ": "shelf",
        "लकड़ी की मरम्मत": "wood repair",
        "फर्नीचर की मरम्मत": "furniture repair",
        "बढ़ईगीरी": "carpentry",


        # -------------------------------------------------
        # PACKERS & MOVERS
        # -------------------------------------------------

        "मूविंग": "moving",
        "मूव": "move",
        "शिफ्ट": "shift",
        "शिफ्टिंग": "shifting",
        "स्थानांतरण": "relocation",
        "पैकिंग": "packing",
        "पैकर्स": "packers",
        "मूवर्स": "movers",
        "पैकर्स एंड मूवर्स": "packers movers",
        "पैकर्स और मूवर्स": "packers movers",
        "घर बदलना": "house move",
        "घर स्थानांतरण": "relocation",
        "घर को स्थानांतरित": "relocation",
        "ले जाना": "move",


        # =================================================
        # NEW: CARETAKING
        # =================================================

        "केयरटेकर": "caretaker",
        "केयर टेकर": "caretaker",
        "केयरटेकर चाहिए": "caretaker",
        "देखभाल": "caregiving",
        "बुजुर्गों की देखभाल": "elderly care",
        "बुजुर्ग": "elderly care",
        "बुजुर्ग व्यक्ति": "elderly care",
        "बुजुर्ग माता-पिता": "elderly care",
        "माता-पिता की देखभाल": "elderly care",
        "मरीज की देखभाल": "patient care",
        "मरीज": "patient",
        "रोगी की देखभाल": "patient care",
        "बच्चों की देखभाल": "child care",
        "बच्चे की देखभाल": "child care",
        "बच्चे": "child care",
        "बच्चे की देखभाल": "baby care",
        "घर की देखभाल": "home care",
        "केयरगिवर": "caregiver",


        # =================================================
        # NEW: DRIVING
        # =================================================

        "ड्राइवर": "driver",
        "ड्राइविंग": "driving",
        "ड्राइवर चाहिए": "driver",
        "कार ड्राइवर": "car driver",
        "व्यक्तिगत ड्राइवर": "personal driver",
        "वाहन चालक": "vehicle driver",
        "चालक": "driver",
        "ड्राइविंग सेवा": "driving service"
    }


    # =====================================================
    # TRANSLATE TELUGU → ENGLISH KEYWORDS
    # =====================================================

    for telugu_word, english_word in TELUGU_KEYWORDS.items():

        if telugu_word in text:

            text += " " + english_word


    # =====================================================
    # TRANSLATE HINDI → ENGLISH KEYWORDS
    # =====================================================

    for hindi_word, english_word in HINDI_KEYWORDS.items():

        if hindi_word in text:

            text += " " + english_word


    # =====================================================
    # DETECT COMPLEX SERVICE
    # =====================================================

    complex_request = detect_complex_service(
        text
    )

    complex_resources = get_complex_resources(
        complex_request
    )


    # =====================================================
    # INITIAL VALUES
    # =====================================================

    detected_service = None

    detected_problem = None

    detected_urgency = "Normal"


    # =====================================================
    # DETECT SERVICE
    # =====================================================

    service_scores = {}


    for service, keywords in SERVICE_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        service_scores[service] = score


    # Prevent a zero-score service from being selected
    best_service = max(
        service_scores,
        key=service_scores.get
    )


    if service_scores[best_service] > 0:

        detected_service = best_service


    # =====================================================
    # DETECT PROBLEM
    # =====================================================

    if detected_service:

        problems = PROBLEM_KEYWORDS.get(
            detected_service,
            {}
        )


        for problem, keywords in problems.items():

            if find_matching_keyword(
                text,
                keywords
            ):

                detected_problem = problem

                break


    # =====================================================
    # DETECT URGENCY
    # =====================================================

    for urgency, keywords in URGENCY_KEYWORDS.items():

        if find_matching_keyword(
            text,
            keywords
        ):

            detected_urgency = urgency

            break


    # =====================================================
    # CALCULATE CONFIDENCE
    # =====================================================

    if detected_service:

        matched_keywords = service_scores[
            detected_service
        ]

        confidence = min(
            0.60 + (
                matched_keywords * 0.10
            ),
            0.95
        )

    else:

        confidence = 0.20


    # =====================================================
    # RETURN COMPLEX SERVICE ANALYSIS
    # =====================================================

    if complex_request:

        return {

            "original_request": request_text,

            "request_type": "complex_service",

            "service": complex_request[
                "service"
            ],

            "problem": detected_problem,

            "urgency": detected_urgency,

            "confidence": round(
                confidence,
                2
            ),

            "property_type": (
                complex_request[
                    "property_type"
                ]
            ),

            "origin": (
                complex_request[
                    "origin"
                ]
            ),

            "destination": (
                complex_request[
                    "destination"
                ]
            ),

            "required_components": (
                complex_request[
                    "required_components"
                ]
            ),

            "team_required": (
                complex_request[
                    "team_required"
                ]
            ),

            "team_size": (
                complex_resources[
                    "team_size"
                ]
            ),

            "vehicle_required": (
                complex_resources[
                    "vehicle_required"
                ]
            ),

            "resources": (
                complex_resources[
                    "resources"
                ]
            )
        }


    # =====================================================
    # RETURN NORMAL SERVICE ANALYSIS
    # =====================================================

    return {

        "original_request": request_text,

        "service": detected_service,

        "problem": detected_problem,

        "urgency": detected_urgency,

        "confidence": round(
            confidence,
            2
        )
    }


# =========================================================
# CREATE SERVICE PLAN
# =========================================================

def create_service_plan(
    analysis,
    team_matching,
    recommendation
):

    if not analysis:

        return None


    return {

        "service": analysis.get(
            "service"
        ),

        "problem": analysis.get(
            "problem"
        ),

        "property_type": analysis.get(
            "property_type"
        ),

        "origin": analysis.get(
            "origin"
        ),

        "destination": analysis.get(
            "destination"
        ),

        "team_required": analysis.get(
            "team_required",
            False
        ),

        "team_size_required": analysis.get(
            "team_size",
            1
        ),

        "workers_available": team_matching.get(
            "team_size_selected",
            0
        ),

        "workers_shortage": recommendation.get(
            "shortage",
            0
        ),

        "vehicle_required": analysis.get(
            "vehicle_required",
            False
        ),

        "resources": analysis.get(
            "resources",
            []
        ),

        "status": recommendation.get(
            "status"
        )
    }