import anthropic
from config import ANTHROPIC_API_KEY, QUIZ_URL, PEPTI_VOICE_RULES

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def determine_mode(post):
    body = (post.get("body", "") + " " + post.get("title", "")).lower()
    explicit_resource = any(phrase in body for phrase in [
        "where can i find", "any resources", "any tools",
        "recommend a site", "good website", "where to learn",
        "any apps", "quiz", "recommend something",
    ])
    if explicit_resource:
        return "C"
    score = post.get("score", 0)
    if score >= 9:
        return "B"
    return "A"

def generate_responses(post):
    mode = determine_mode(post)
    title = post.get("title", "")
    body = post.get("body", "")
    subreddit = post.get("subreddit", "")
    matched = post.get("matched_keywords", [])

    mode_instructions = {
        "A": "Provide pure value. Be the most helpful response in the thread. Do NOT mention Pepti or any quiz. Just be genuinely knowledgeable.",
        "B": f"Provide excellent value first. At the very end, casually mention you used a quiz to find your stack and offer to share it if they want. The quiz URL is {QUIZ_URL}. Keep it natural — one sentence max.",
        "C": f"Be helpful and direct. You can mention Pepti as a resource. Drop the quiz link naturally: {QUIZ_URL}. Keep the pitch one sentence.",
    }

    prompt = f"""
{PEPTI_VOICE_RULES}

You are responding to a Reddit post in r/{subreddit}.

POST TITLE: {title}
POST BODY: {body}
KEYWORDS THAT TRIGGERED THIS: {matched}
RESPONSE MODE: {mode} — {mode_instructions[mode]}

Generate 3 different response options. Each should feel distinct in approach but all follow the voice rules.
Format exactly like this:

OPTION_1:
[response text]

OPTION_2:
[response text]

OPTION_3:
[response text]

RECOMMENDED_MODE: {mode}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text
        options = parse_options(raw)
        return {
            "mode": mode,
            "options": options,
            "raw": raw,
        }
    except Exception as e:
        print(f"[Generator] Error generating response: {e}")
        return {"mode": mode, "options": [], "raw": ""}

def parse_options(raw):
    options = []
    for i in range(1, 4):
        tag = f"OPTION_{i}:"
        next_tag = f"OPTION_{i+1}:" if i < 3 else "RECOMMENDED_MODE:"
        if tag in raw:
            start = raw.index(tag) + len(tag)
            end = raw.index(next_tag) if next_tag in raw else len(raw)
            options.append(raw[start:end].strip())
    return options
