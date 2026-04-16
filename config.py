import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO = os.getenv("TWILIO_TO_NUMBER")

AUTO_POST = os.getenv("AUTO_POST", "false").lower() == "true"
QUIZ_URL = os.getenv("QUIZ_URL", "https://peptiaii.com/quiz")
MIN_SCORE = int(os.getenv("MIN_SCORE", "7"))

SUBREDDITS = {
    "tier1": [
        "Peptides",
        "Biohacking",
        "Nootropics",
        "maleoptimization",
        "longevity",
    ],
    "tier2": [
        "Supplements",
        "bodybuilding",
        "gainit",
        "hormones",
        "sportsscience",
        "AntiAgingScience",
    ],
    "tier3": [
        "entrepreneur",
        "startups",
        "college",
        "youngentrepreneurs",
    ],
    "tier4": [
        "fitness",
        "nutrition",
        "sleep",
        "ADHD",
    ],
}

TIER_INTERVALS = {
    "tier1": 10,
    "tier2": 30,
    "tier3": 60,
    "tier4": 120,
}

KEYWORDS = {
    10: [
        "what peptide should i",
        "recommend a peptide stack",
        "where do i start with peptides",
        "best peptide for recovery",
        "looking for nootropic recommendations",
        "peptide stack for beginners",
        "which peptide should i try first",
    ],
    8: [
        "bpc-157", "bpc157",
        "tb-500", "tb500",
        "semax",
        "bromantane",
        "epithalon",
        "mk-677", "mk677",
        "igf-1", "igf1",
        "ghk-cu",
        "melanotan",
        "aod-9604",
        "ipamorelin",
        "cjc-1295",
        "injury won't heal",
        "injury not healing",
        "want to try peptides",
        "peptide curious",
        "tried peptides",
    ],
    6: [
        "recovery taking too long",
        "brain fog",
        "can't focus",
        "cant focus",
        "plateau in the gym",
        "anti aging stack",
        "longevity stack",
        "supplements stopped working",
        "creatine isn't working",
        "creatine not working",
        "nootropic stack",
        "cognitive enhancement",
        "performance optimization",
        "sleep optimization",
        "tendon repair",
        "ligament heal",
    ],
    4: [
        "optimize performance",
        "biohacking stack",
        "what supplements",
        "hormone optimization",
        "testosterone",
        "growth hormone",
        "peptide",
        "nootropic",
        "cognitive performance",
        "physical performance",
    ],
}

COMPETITOR_BRANDS = [
    "limitless life nootropics",
    "paradigm peptides",
    "peptide sciences",
    "swiss chems",
    "amino asylum",
    "pure rawz",
]

PEPTI_VOICE_RULES = """
You are a knowledgeable community member in biohacking and peptide spaces.
NEVER identify yourself as Pepti or any brand.
NEVER recommend dosing or sourcing.
NEVER make explicit medical claims.
ALWAYS frame information as "what research shows" or "what I've found."
ALWAYS be genuinely helpful even if Pepti never gets mentioned.
Keep responses under 3 paragraphs.
End with a question to drive engagement.
Sound like a real person, not a brand.
Use casual but informed language.
"""
