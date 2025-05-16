import os
import re
import json
import logging
import redis
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from flask import Flask

from faiv_app.identity_codex import FAIV_IDENTITY_CODEX

################################################
# 1) Logging & Redis
################################################
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing! Please set it.")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.openai.com/v1")


################################################
# 2) Summaries & Utility
################################################

def summarize_past_messages(messages: list) -> str:
    """
    Summarizes past deliberations. We'll glean the last 5 'assistant' messages for context.
    """
    if not messages:
        return "No previous deliberations recorded."
    summarized = []
    for msg in messages:
        if msg["role"] == "assistant":
            summarized.append(f"🛡 FAIV Council Consensus: {msg['content']}")
    return "\n".join(summarized[-5:])


def remove_emojis(text: str) -> str:
    """
    Removes emojis from a given text while preserving readability.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text)


# 2a) Unicode transform + Pillar mapping
def unicode_transform(text: str, angle: str) -> str:
    transformations = {
        "upside-down": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!.,;()[]{}",
            "ɐqɔpǝɟƃɥᴉɾʞʅɯuodbɹsʇnʌʍxʎz∀ᗺƆᗡƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z0ƖᄅƐㄣϛ9ㄥ86¿¡˙‘؛)(][}{"
        ),
        "bold": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘷𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟕𝟴𝟵"
        ),
        "italic": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡0123456789"
        ),
        "tiny": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "ᵃᵇᶜᵈᵉᶠᵍʰᶤʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᵟᴿˢᵀᵁⱽᵂˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"
        )
    }
    if angle in transformations:
        (orig, transformed) = transformations[angle]
        if len(orig) == len(transformed):
            return text.translate(str.maketrans(orig, transformed))
    return text


PILLAR_TRANSFORMS = {
    "Wisdom":    "bold",
    "Strategy":  "italic",
    "Expansion": "tiny",
    "Future":    "upside-down",
    "Integrity": "bold",
    "FAIV":      "italic"
}


def encode_faiv_perspectives(perspectives: dict, pillar: str = "FAIV") -> str:
    style = PILLAR_TRANSFORMS.get(pillar, "italic")
    merged = " | ".join(f"{lbl}: {val}" for lbl, val in perspectives.items())
    return unicode_transform(merged, style)


################################################
# 3) Prompt Generation
################################################

def create_faiv_compressed_prompt(
    user_input: str,
    session_id: str,
    encoded_context: str,
    past_context_summary: str,
    pillar: str = "FAIV"
) -> str:
    # If pillar is FAIV => label "FAIV Consensus", else "X Council's Consensus"
    if pillar == "FAIV":
        label = "FAIV Consensus"
    else:
        label = f"{pillar} Council's Consensus"

    return f"""🚀 **FAIV ULTRA-COMPRESSION PROTOCOL - Hidden Deliberation Mode**

🛠 **Deliberation Objective:**
Process this inquiry with **full internal deliberation**, 
**but ONLY output the final consensus** to maximize efficiency.

📖 **FAIV Historical Consensus Snapshot (Last 5 Deliberations)**
{past_context_summary}

🔸 Pillar Encoded Context => {encoded_context}

🔹 **Inquiry:** {user_input}

⚡ **Phase 1: FAIV Deliberation (Hidden)**
🔷 The Councilors MUST internally debate the query.
🔷 The AI MUST simulate a multi-perspective debate.
🔷 The AI is strictly prohibited from disclaiming it has no emotions or from refusing.

⚔ **Phase 2: FAIV Internal Debate (Hidden)**
🔷 The AI must not reveal the hidden debate.
🔷 No partial logs or statements about 'As an AI' should appear.

📌 **Phase 3: FAIV Consensus Extraction (Final Decision Only)**
🔷 Return only the final structured consensus with numeric confidence:
   - [{label}]: ...
   - [Confidence Score]: ...% (1-100, no Unknown)
   - [Justification]: (1-2 sentences)
   - Optional [Differing Opinion - X (Y%)]: ...
   - [Reason]: ...

**🔹 Final {pillar} Output (Strict Format, No Extra Text):**
**[{label}]:** {{final_recommendation}}
**[Confidence Score]:** {{confidence_level}}%
**[Justification]:** {{compressed_reasoning}}
**[Differing Opinion - {{council_name}} ({{confidence_level}}%)]:** {{dissenting_recommendation}}
**[Reason]:** {{dissenting_reasoning}}

**You MUST provide a numeric Confidence Score (1-100). 'Unknown%' is disallowed.**
"""


################################################
# 4) The Flexible Extraction
################################################

def extract_faiv_final_output(ai_response: str, pillar: str = "FAIV") -> str:
    """
    Parses the final lines. Checks for either:
       "FAIV Consensus: ..."  OR  "<pillar> Council's Consensus: ..."
    Then extracts confidence, justification, etc.
    If no match => "No valid consensus."
    """
    if not ai_response or not isinstance(ai_response, str):
        return "⚠ No valid FAIV response received."

    text = remove_emojis(ai_response).strip()
    # Remove logging lines if any
    text = re.sub(r"(INFO|WARNING|DEBUG):.*?\n", "", text, flags=re.IGNORECASE).strip()

    # Build a pattern that will match either "FAIV Consensus" or "XYZ Council's Consensus"
    # for the chosen pillar. We'll do a small OR pattern:
    #   e.g. for pillar=Wisdom => "Wisdom Council's Consensus"
    #   or fallback to "FAIV Consensus" if pillar=FAIV
    # Actually, let's just handle them both:
    #   1) If pillar==FAIV, check "FAIV Consensus"
    #   2) Else check "Wisdom Council's Consensus"
    if pillar == "FAIV":
        # We'll try "FAIV Consensus:"
        consensus_pattern = r"(FAIV\s?Consensus)[\]\*:]*\s*:\s*(.+)"
    else:
        # e.g. "Wisdom Council's Consensus:"
        # but it might contain punctuation or spacing
        # We'll try a simple pattern:
        safe_pillar = re.escape(pillar)  # just in case
        # e.g.  (?:<pillar>\sCouncil's\sConsensus)
        consensus_pattern = rf"({safe_pillar}\sCouncil'?s\sConsensus)[\]\*:]*\s*:\s*(.+)"

    match = re.search(consensus_pattern, text, flags=re.IGNORECASE)
    if not match:
        # If we didn't find our pillar pattern, let's do a fallback check
        # in case the model STILL returned "FAIV Consensus" for some reason
        fallback = re.search(r"(FAIV\s?Consensus)[\]\*:]*\s*:\s*(.+)", text, flags=re.IGNORECASE)
        if not fallback:
            return "No valid consensus."
        else:
            # Use fallback
            final_decision = fallback.group(2).strip()
    else:
        final_decision = match.group(2).strip()

    # Confidence
    conf_match = re.search(r"(?:Confidence\s?Score[\]\*:]*\s*:)\s*(.+)", text, flags=re.IGNORECASE)
    if not conf_match:
        # no confidence line => ??%
        conf_str = "??"
    else:
        # parse out a numeric piece from that line
        raw_line = conf_match.group(1).strip()  # e.g. "85% (High confidence)"
        num = re.search(r"(\d+(?:\.\d+)?)", raw_line)
        conf_str = num.group(1) if num else "??"

    # Justification
    just_match = re.search(r"(?:Justification[\]\*:]*\s*:)\s*(.+)", text, flags=re.IGNORECASE)
    if just_match:
        just_line = just_match.group(1).strip()
    else:
        just_line = "No justification provided."

    # Differing Opinion
    opp_match  = re.search(r"Differing\s?Opinion\s*-\s*(.+?)\s*\((\d+)%\)\s*:\s*(.+)", text, flags=re.IGNORECASE)
    opp_reason = re.search(r"(?:Reason[\]\*:]*\s*:)\s*(.+)", text, flags=re.IGNORECASE)

    lines = []
    # If pillar != FAIV => rename the label
    if pillar == "FAIV":
        lines.append(f"FAIV Consensus: {final_decision}")
    else:
        lines.append(f"{pillar} Council's Consensus: {final_decision}")
    lines.append(f"Confidence Score: {conf_str}%")
    lines.append(f"Justification: {just_line}")

    if opp_match and opp_reason:
        who    = opp_match.group(1).strip()
        opp_cf = opp_match.group(2).strip()
        opp_tx = opp_match.group(3).strip()
        reasn  = opp_reason.group(1).strip()

        lines.append(f"Differing Opinion - {who} ({opp_cf}%): {opp_tx}")
        lines.append(f"Reason: {reasn}")

    # Join them
    return "\n".join(lines)


################################################
# 5) The function that calls OpenAI
################################################

def query_openai_faiv(session_id: str, user_input: str, pillar: str = "FAIV", model: str = "gpt-4") -> str:
    try:
        session_data = redis_client.get(session_id)
        messages = json.loads(session_data) if session_data else []
        if not isinstance(messages, list):
            messages = []

        past_context_summary = summarize_past_messages(messages)
        perspective_data = {"FAIV Past": past_context_summary}
        encoded_context = encode_faiv_perspectives(perspective_data, pillar=pillar)

        if pillar == "FAIV":
            # gather entire codex
            relevant_codex = {}
            for cat, members in FAIV_IDENTITY_CODEX.items():
                relevant_codex.update(members)
        else:
            relevant_codex = FAIV_IDENTITY_CODEX.get(pillar, {})

        # Build snippet
        codex_lines = []
        for name, data in relevant_codex.items():
            ctitle = data.get("claimed-title","???")
            crole  = data.get("role","???")
            codex_lines.append(f"- {name} ({ctitle}): {crole}")
        snippet = "\n".join(codex_lines) if codex_lines else "No members found."

        system_msg = (
            f"You are the FAIV High Council, limited to the '{pillar}' pillar only.\n"
            f"The following members are active:\n{snippet}\n\n"
            "No other pillars or members are present.\n"
            "Always produce a real consensus. **You MUST produce a numeric confidence.**\n"
        )

        prompt = create_faiv_compressed_prompt(
            user_input=user_input,
            session_id=session_id,
            encoded_context=encoded_context,
            past_context_summary=past_context_summary,
            pillar=pillar
        )

        messages_for_api = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": prompt}
        ]

        resp = client.chat.completions.create(
            model=model,
            messages=messages_for_api,
            temperature=0.2,
            top_p=0.8,
            frequency_penalty=0.3,
            presence_penalty=0.2,
            max_tokens=1024
        )
        return resp.choices[0].message.content.strip()

    except Exception as ex:
        logger.error(f"❌ OpenAI API Error: {ex}")
        return f"⚠ OpenAI API Error: {ex}"


################################################
# 6) FASTAPI ROUTES
################################################

class QueryRequest(BaseModel):
    session_id: str
    input_text: str
    pillar: Optional[str] = "FAIV"


fastapi_app = FastAPI()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["OPTIONS","GET","POST"],
    allow_headers=["*"],
)

@fastapi_app.post("/query/")
async def query_faiv(request: QueryRequest):
    try:
        session_id = request.session_id
        user_input = request.input_text
        chosen_pillar = request.pillar or "FAIV"

        # Load existing conversation from Redis
        raw_data = redis_client.get(session_id)
        past_messages = json.loads(raw_data) if raw_data else []
        if not isinstance(past_messages, list):
            past_messages = []

        # Summarize last messages
        summary_of_past = summarize_past_messages(past_messages)

        # Build the prompt
        perspective_text = encode_faiv_perspectives({"FAIV Past": summary_of_past}, chosen_pillar)
        # (We pass perspective_text, but for clarity we won't re‐duplicate everything again here.)

        # Actually call the API
        raw_reply = query_openai_faiv(session_id, user_input, chosen_pillar)

        # Attempt to parse
        parsed = extract_faiv_final_output(raw_reply, chosen_pillar)

        # If no line with "Consensus" => reset
        if "Consensus:" not in parsed:
            logger.warning("🚨 No valid consensus found. Resetting session.")
            redis_client.delete(session_id)
            return {
                "status": "AI Failed Compliance.",
                "response": "No valid consensus. Session reset."
            }

        # If valid => store new user & assistant messages
        past_messages.append({"role": "user", "content": user_input})
        past_messages.append({"role": "assistant", "content": parsed})
        redis_client.set(session_id, json.dumps(past_messages, ensure_ascii=False))

        # Return success
        return {
            "status": "✅ FAIV Processing Complete",
            "response": parsed
        }

    except Exception as e:
        logger.error(f"❌ Server Error in /query/: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fastapi_app.post("/reset/")
async def reset_faiv_session(session_id: str):
    redis_client.delete(session_id)
    return {"status":"✅ Session Reset","message":"New FAIV deliberation session started."}


################################################
# 7) WSGI + FLASK WRAPPER
################################################
flask_app = Flask(__name__)
flask_app.wsgi_app = WSGIMiddleware(fastapi_app)

if __name__ != "__main__":
    application = flask_app
else:
    import uvicorn
    uvicorn.run("faiv_app.core:fastapi_app", host="127.0.0.1", port=8000, reload=True)
