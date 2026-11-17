"""State -> district -> hospital directory used for tap-to-select locations (bot + web).

Districts are complete for the listed states. Hospitals are a curated starter list for major
districts; any district without a list offers its government district hospital, and every
picker also allows typing another name. Extend freely: order is preserved, and the bot
addresses entries by index, so append new states/districts/hospitals rather than reordering
while the bot has open menus.
"""

LOCATIONS: dict[str, dict[str, list[str]]] = {
    "Karnataka": {
        "Bagalkot": [], "Ballari": [], "Belagavi": ["KLE Dr. Prabhakar Kore Hospital", "BIMS Hospital, Belagavi"],
        "Bengaluru Rural": [],
        "Bengaluru Urban": [
            "Victoria Hospital", "Bowring & Lady Curzon Hospital", "St. John's Medical College Hospital",
            "Manipal Hospital, Old Airport Road", "Narayana Health City", "Apollo Hospital, Bannerghatta Road",
            "Fortis Hospital, Bannerghatta Road", "Kidwai Memorial Institute of Oncology",
        ],
        "Bidar": [], "Chamarajanagar": [], "Chikkaballapur": [], "Chikkamagaluru": [], "Chitradurga": [],
        "Dakshina Kannada": [
            "Wenlock District Hospital", "KMC Hospital, Attavar", "Father Muller Medical College Hospital",
            "A.J. Hospital", "Yenepoya Medical College Hospital", "Indiana Hospital",
        ],
        "Davanagere": [], "Dharwad": ["KIMS Hubballi", "SDM College of Medical Sciences Hospital"],
        "Gadag": [], "Hassan": [], "Haveri": [],
        "Kalaburagi": ["GIMS Hospital, Kalaburagi", "Basaveshwar Teaching & General Hospital"],
        "Kodagu": [], "Kolar": [], "Koppal": [], "Mandya": [],
        "Mysuru": ["K.R. Hospital", "JSS Hospital", "Apollo BGS Hospital", "Manipal Hospital, Mysuru"],
        "Raichur": [], "Ramanagara": [], "Shivamogga": ["McGann District Hospital"], "Tumakuru": [],
        "Udupi": ["Kasturba Hospital, Manipal", "District Hospital, Udupi", "Adarsha Hospital"],
        "Uttara Kannada": [], "Vijayapura": [], "Vijayanagara": [], "Yadgir": [],
    },
    "Kerala": {
        "Alappuzha": [],
        "Ernakulam": ["Amrita Hospital, Kochi", "Aster Medcity", "VPS Lakeshore Hospital", "General Hospital, Ernakulam"],
        "Idukki": [], "Kannur": [], "Kasaragod": ["General Hospital, Kasaragod"], "Kollam": [], "Kottayam": [],
        "Kozhikode": ["Govt. Medical College Hospital, Kozhikode", "Aster MIMS Calicut", "Baby Memorial Hospital"],
        "Malappuram": [], "Palakkad": [], "Pathanamthitta": [],
        "Thiruvananthapuram": ["Govt. Medical College Hospital, Thiruvananthapuram", "KIMSHEALTH",
                               "Sree Chitra Tirunal Institute"],
        "Thrissur": ["Govt. Medical College Hospital, Thrissur", "Jubilee Mission Medical College Hospital"],
        "Wayanad": [],
    },
    "Tamil Nadu": {
        "Ariyalur": [], "Chengalpattu": [],
        "Chennai": ["Rajiv Gandhi Govt. General Hospital", "Govt. Stanley Hospital", "Apollo Hospitals, Greams Road",
                    "MIOT International", "Sri Ramachandra Medical Centre"],
        "Coimbatore": ["Coimbatore Medical College Hospital", "PSG Hospitals", "KMCH"],
        "Cuddalore": [], "Dharmapuri": [], "Dindigul": [], "Erode": [], "Kallakurichi": [], "Kancheepuram": [],
        "Kanniyakumari": [], "Karur": [], "Krishnagiri": [],
        "Madurai": ["Govt. Rajaji Hospital", "Meenakshi Mission Hospital"],
        "Mayiladuthurai": [], "Nagapattinam": [], "Namakkal": [], "Nilgiris": [], "Perambalur": [],
        "Pudukkottai": [], "Ramanathapuram": [], "Ranipet": [], "Salem": [], "Sivaganga": [], "Tenkasi": [],
        "Thanjavur": [], "Theni": [], "Thoothukudi": [], "Tiruchirappalli": [], "Tirunelveli": [], "Tirupathur": [],
        "Tiruppur": [], "Tiruvallur": [], "Tiruvannamalai": [], "Tiruvarur": [],
        "Vellore": ["CMC Vellore", "Govt. Vellore Medical College Hospital"],
        "Viluppuram": [], "Virudhunagar": [],
    },
    "Maharashtra": {
        "Ahilyanagar": [], "Akola": [], "Amravati": [], "Beed": [], "Bhandara": [], "Buldhana": [],
        "Chandrapur": [], "Chhatrapati Sambhajinagar": [], "Dharashiv": [], "Dhule": [], "Gadchiroli": [],
        "Gondia": [], "Hingoli": [], "Jalgaon": [], "Jalna": [], "Kolhapur": [], "Latur": [],
        "Mumbai City": ["KEM Hospital", "Sir J.J. Hospital", "Tata Memorial Hospital", "LTMG (Sion) Hospital"],
        "Mumbai Suburban": ["Kokilaben Dhirubhai Ambani Hospital", "Lilavati Hospital", "Nanavati Max Hospital",
                            "Cooper Hospital"],
        "Nagpur": ["Govt. Medical College Hospital, Nagpur", "AIIMS Nagpur"],
        "Nanded": [], "Nandurbar": [], "Nashik": [], "Palghar": [], "Parbhani": [],
        "Pune": ["Sassoon General Hospital", "Ruby Hall Clinic", "Jehangir Hospital", "Deenanath Mangeshkar Hospital"],
        "Raigad": [], "Ratnagiri": [], "Sangli": [], "Satara": [], "Sindhudurg": [], "Solapur": [], "Thane": [],
        "Wardha": [], "Washim": [], "Yavatmal": [],
    },
    "Delhi": {
        "Central Delhi": ["Lok Nayak Hospital", "G.B. Pant Hospital"],
        "East Delhi": [],
        "New Delhi": ["AIIMS New Delhi", "Safdarjung Hospital", "Dr. Ram Manohar Lohia Hospital", "Sir Ganga Ram Hospital"],
        "North Delhi": [], "North East Delhi": [], "North West Delhi": [], "Shahdara": [],
        "South Delhi": ["Max Super Speciality Hospital, Saket"],
        "South East Delhi": ["Indraprastha Apollo Hospital"],
        "South West Delhi": [], "West Delhi": [],
    },
    "Goa": {
        "North Goa": ["Goa Medical College, Bambolim", "Manipal Hospital, Goa"],
        "South Goa": ["Hospicio Hospital, Margao"],
    },
}

# Common city names -> (state, district), so typed or legacy values line up with the picker.
CITY_ALIASES = {
    "bangalore": ("Karnataka", "Bengaluru Urban"), "bengaluru": ("Karnataka", "Bengaluru Urban"),
    "mangalore": ("Karnataka", "Dakshina Kannada"), "mangaluru": ("Karnataka", "Dakshina Kannada"),
    "mysore": ("Karnataka", "Mysuru"), "hubli": ("Karnataka", "Dharwad"), "hubballi": ("Karnataka", "Dharwad"),
    "belgaum": ("Karnataka", "Belagavi"), "gulbarga": ("Karnataka", "Kalaburagi"),
    "shimoga": ("Karnataka", "Shivamogga"), "manipal": ("Karnataka", "Udupi"), "tumkur": ("Karnataka", "Tumakuru"),
    "moodbidri": ("Karnataka", "Dakshina Kannada"), "moodabidri": ("Karnataka", "Dakshina Kannada"),
    "mudbidri": ("Karnataka", "Dakshina Kannada"), "puttur": ("Karnataka", "Dakshina Kannada"),
    "bantwal": ("Karnataka", "Dakshina Kannada"), "ullal": ("Karnataka", "Dakshina Kannada"),
    "surathkal": ("Karnataka", "Dakshina Kannada"), "belthangady": ("Karnataka", "Dakshina Kannada"),
    "sullia": ("Karnataka", "Dakshina Kannada"), "karkala": ("Karnataka", "Udupi"),
    "kundapura": ("Karnataka", "Udupi"), "kundapur": ("Karnataka", "Udupi"), "brahmavar": ("Karnataka", "Udupi"),
    "delhi": ("Delhi", "New Delhi"), "mumbai": ("Maharashtra", "Mumbai City"), "bombay": ("Maharashtra", "Mumbai City"),
    "madras": ("Tamil Nadu", "Chennai"), "trichy": ("Tamil Nadu", "Tiruchirappalli"),
    "kochi": ("Kerala", "Ernakulam"), "cochin": ("Kerala", "Ernakulam"),
    "trivandrum": ("Kerala", "Thiruvananthapuram"), "calicut": ("Kerala", "Kozhikode"),
    "panaji": ("Goa", "North Goa"), "panjim": ("Goa", "North Goa"), "margao": ("Goa", "South Goa"),
}
for _state, _districts in LOCATIONS.items():
    for _district in _districts:
        CITY_ALIASES.setdefault(_district.lower(), (_state, _district))


def hospitals_for(state: str, district: str) -> list[str]:
    listed = LOCATIONS.get(state, {}).get(district)
    if listed is None:
        return []
    return listed or [f"Govt. District Hospital, {district}"]


def normalize(city: str | None, state: str | None = None) -> tuple[str | None, str]:
    """Map a typed/legacy city to (state, district) when we know it; else keep it title-cased."""
    raw = (city or "").strip()
    known = CITY_ALIASES.get(raw.lower())
    if known and (not state or state == known[0]):
        return known
    return (state or None), raw.title() if raw.islower() or raw.isupper() else raw


def as_tree() -> list[dict]:
    return [
        {"name": s, "districts": [{"name": d, "hospitals": hospitals_for(s, d)} for d in districts]}
        for s, districts in LOCATIONS.items()
    ]
