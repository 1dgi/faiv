import os
import logging
import re
import openai
import unicodedata

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from faiv_app.identity_codex import FAIV_IDENTITY_CODEX  # Imported for potential use
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from flask import Flask

import logging

def unicode_transform(text: str, angle: str) -> str:
    """
    Applies a transformation to the text based on the assigned encoding style.
    Ensures `maketrans()` arguments have equal lengths before applying.
    """

    transformations = {
        "upside-down": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!.,;()[]{}",
            "ɐqɔpǝɟƃɥᴉɾʞʅɯuodbɹsʇnʌʍxʎz∀ᗺƆᗡƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z0ƖᄅƐㄣϛ9ㄥ86¿¡˙‘؛)(][}{"
        ),
        "bold": (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘵𝘶𝘷𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟩𝟴𝟵"
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
        original_chars, transformed_chars = transformations[angle]

        # Ensure transformation length matches
        if len(original_chars) != len(transformed_chars):
            logging.error(f"❌ Transformation `{angle}` has mismatched translation lengths.")
            return text  # Return original text if there's an issue

        return text.translate(str.maketrans(original_chars, transformed_chars))

    return text  # Return original text if no transformation is applied

def encode_faiv_perspectives(perspectives: dict) -> str:
    """
    Encodes multiple FAIV Council perspectives in a compressed format
    using Unicode transformations.
    """

    transformation_types = ["upside-down", "bold", "italic", "tiny"]  # Rotation order
    encoded_output = []

    for idx, (council, text) in enumerate(perspectives.items()):
        # Cycle through transformations based on council order
        transformation = transformation_types[idx % len(transformation_types)]
        encoded_text = unicode_transform(text, transformation)        
        encoded_output.append(f"({council}): {encoded_text}")

    return "\n".join(encoded_output)


# ------------------------------------------------
# 1) Logging Configuration
# ------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------------------------
# 2) Load Environment Variable (OPENAI_API_KEY)
# ------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing! Please set it in your environment variables.")

# Initialize the OpenAI library with your key
openai.api_key = OPENAI_API_KEY

# ------------------------------------------------
# 3) Create the FastAPI App (for local development)
# ------------------------------------------------
fastapi_app = FastAPI()

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust if needed
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)

# ------------------------------------------------
# 4) FAIV Deliberation Logic (with Identity Codex Integration)
# ------------------------------------------------
def create_identity_summary() -> str:
    """Generates a structured breakdown of FAIV Council members and their roles."""
    summary_lines = ["🔷 **FAIV High Council** - A deliberation model integrating diverse AI perspectives:\n"]
    for category, members in FAIV_IDENTITY_CODEX.items():
        council_list = ", ".join(members.keys())
        summary_lines.append(f"  - **{category} Council** ({len(members)} members): {council_list}")
    return "\n".join(summary_lines)

def create_faiv_compressed_prompt(user_input: str) -> str:
    """
    Constructs the FAIV deliberation prompt while ensuring the output adheres
    to structured multi-perspective analysis.
    """

    # Generate FAIV Identity Codex summary for internal deliberation
    identity_summary = create_identity_summary()

    prompt = (
        "🚀 **FAIV HIGH COUNCIL DELIBERATION PROTOCOL**\n\n"
        "🛠 **Deliberation Objective:**\n"
        "Process this inquiry through full internal deliberation by consulting the FAIV High Council. "
        "Each councilor provides expert insights, debates conflicting viewpoints, and aligns toward an optimal decision.\n\n"
        
        f"🔹 **Inquiry:** {user_input}\n\n"
        
        "⚔ **Phase 1: Council Deliberation (Hidden)**\n"
        "🔷 The FAIV High Council consists of specialized members, each contributing expertise. "
        "Each councilor must analyze the query using their domain's specialized viewpoint.\n\n"
        f"🔹 Council Composition:\n{identity_summary}\n\n"
        "🔷 Each perspective must be represented by council members:\n"
        "   - **Wisdom Council**: Evaluates long-term implications, ethical concerns, and knowledge depth.\n"
        "   - **Strategy Council**: Analyzes tactical advantages, risk mitigation, and optimal approaches.\n"
        "   - **Expansion Council**: Examines global impact, adaptability, and frontier knowledge.\n"
        "   - **Future Council**: Predicts innovation, technology shifts, and cultural transformations.\n"
        "   - **Integrity Council**: Assesses fairness, truth, and overall balance of decision-making.\n"

        "🔷 Each councilor must analyze the inquiry from their domain’s perspective.\n"
        "🔷 The AI must conduct an internal debate, refining the decision through rebuttals and alignment.\n\n"
        
        "📌 **Phase 2: Consensus & Decision (Hidden)**\n"
        "🔷 The AI must determine the highest-confidence consensus while noting significant dissent (if applicable).\n"
        "🔷 The AI must NOT include any internal deliberation steps in the output.\n"
        "🔷 The AI must NOT state that it has no opinions—FAIV Councilors represent real-world expertise.\n\n"
        
        "🎯 **Final FAIV Decision (Output Only)**\n"
        "🔷 The AI must return:\n"
        "   - The **final consensus** (highest-confidence outcome).\n"
        "   - A **Confidence Score** (1-100%).\n"
        "   - A **Concise Justification** (1-2 sentences max).\n"
        "   - **If necessary**, dissenting opinions (if confidence is below 85%).\n\n"
        
        "✅ **Output Format (Strictly Follow This)**\n"
        "**FAIV Consensus:** {{final_recommendation}}\n"
        "**Confidence Score:** {{confidence_level}}%\n"
        "**Justification:** {{compressed_reasoning}}\n\n"
        
        "**Differing Opinion ({{council_name}} - {{confidence_level}}%)**: {{dissenting_recommendation}}\n"
        "**Reason:** {{dissenting_reasoning}}\n"
    )

    return prompt

def query_openai_faiv(prompt: str, council_name: str) -> str:
    """
    Calls GPT-4 for deliberation **for a specific FAIV Council**.
    Ensures **each council provides independent input before alignment.**
    """
    try:
        logger.info(f"📜 Sending FAIV Prompt for [{council_name}]:\n{prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are the {council_name} Council of the FAIV High Council. "
                               "Your role is to provide expert insights from your domain perspective. "
                               "Debate, analyze, and refine your recommendation before providing a final judgment."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"OpenAI API Error for {council_name}: {str(e)}"
        logger.error(f"❌ {error_message}")
        return f"⚠ OpenAI API Error: {error_message}"


def extract_faiv_perspectives(ai_responses: dict) -> str:
    """
    Extracts structured final consensus, confidence score, and justification 
    from each FAIV council’s AI output while ensuring proper formatting.
    """

    response_output = f"🔷 **FAIV High Council Final Decision** 🔷\n\n"
    
    final_consensus = None
    final_confidence = "Unknown"
    final_justification = "No justification provided."

    council_decisions = []  # Store per-council decisions

    for council, response in ai_responses.items():
        # Extract relevant data using regex
        matches = {
            "decision": re.search(r"\[FAIV Consensus\]: (.+)", response),
            "confidence": re.search(r"\[Confidence Score\]: (\d+)", response),
            "justification": re.search(r"\[Supporting Justification\]: (.+)", response),
        }

        # Assign extracted values or fallback defaults
        decision = matches["decision"].group(1).strip() if matches["decision"] else "No decision"
        confidence = matches["confidence"].group(1).strip() if matches["confidence"] else "Unknown"
        justification = matches["justification"].group(1).strip() if matches["justification"] else "No justification provided."

        # Log extraction results for debugging
        logger.info(f"🔍 Extracted Decision [{council}]: {decision} ({confidence}%)")
        
        # Append to council-specific decisions
        council_decisions.append({
            "council": council,
            "decision": decision,
            "confidence": confidence,
            "justification": justification
        })

    # Determine final consensus (Highest confidence score)
    if council_decisions:
        sorted_decisions = sorted(council_decisions, key=lambda x: int(x["confidence"]) if x["confidence"].isdigit() else 0, reverse=True)
        final_consensus = sorted_decisions[0]["decision"]
        final_confidence = sorted_decisions[0]["confidence"]
        final_justification = sorted_decisions[0]["justification"]

    # Construct the final response output
    response_output += f"🏛 **Final Consensus:** {final_consensus}\n"
    response_output += f"📊 **Confidence Score:** {final_confidence}%\n"
    response_output += f"💡 **Justification:** {final_justification}\n\n"

    response_output += "📜 **Council Deliberation Summary:**\n"

    # Append individual council responses to the final report
    for council_data in council_decisions:
        response_output += f"\n🔹 **{council_data['council']} Council:** {council_data['decision']} ({council_data['confidence']}%)\n"
        response_output += f"📌 Justification: {council_data['justification']}\n"

    return response_output.strip()

def extract_faiv_final_output(ai_response: str) -> str:
    """
    (Optional) Extracts only the final FAIV consensus, confidence score, and reasoning from bracketed sections.
    """
    logger.info("📌 Processing AI Response for Final Consensus Extraction...")

    final_decision_match = re.search(r"\[FAIV Consensus\]: The optimal answer is \*\*(.+?)\*\*", ai_response)
    confidence_match     = re.search(r"\[Confidence Score\]: \*\*(\d+)%\*\*", ai_response)
    justification_match  = re.search(r"\[Supporting Justification\]: \*\*(.+?)\*\*", ai_response)

    final_decision = remove_emojis(final_decision_match.group(1).strip()) if final_decision_match else "**No clear decision reached.**"
    confidence     = confidence_match.group(1).strip() if confidence_match else "**Confidence level unknown.**"
    justification  = remove_emojis(justification_match.group(1).strip()) if justification_match else "**No justification provided.**"

    response_output = (
        f"**FAIV Consensus:** {final_decision}\n"
        f"**Confidence Score:** {confidence_score}%\n"
        f"**Justification:** {justification}"
    )

    logger.info(f"✅ Extracted Final Consensus: {final_decision}")
    logger.info(f"✅ Confidence Score: {confidence_score}%")
    logger.info(f"✅ Justification: {justification}")
    response_output = remove_emojis(response_output)  # Apply emoji cleaning at the final stage

    return response_output

def generate_faiv_response(input_text: str) -> dict:
    """
    Builds the prompt (with Identity Codex summary), calls OpenAI, and extracts the final structured response.
    Returns a dictionary for the FastAPI endpoint.
    """
    logger.info(f"🔹 Processing FAIV deliberation for: {input_text}")
    prompt = create_faiv_compressed_prompt(input_text)
    ai_response = query_openai_faiv(prompt)
    logger.info(f"🔍 Raw AI Response:\n{ai_response}")
    formatted_response = extract_faiv_perspectives(ai_response)
    logger.info(f"✅ Final Formatted Response:\n{formatted_response}")
    # After we generate 'encoded_response'
    encoded_response = remove_emojis(encoded_response)
    return {
        "status": "✅ FAIV Processing Complete",
        "response": formatted_response
    }

def process_faiv_results(ai_responses):
    """
    Processes FAIV responses to ensure strict filtering:
    - Only extracts FINAL consensus, confidence score, and justification.
    - Only includes differing opinions if their confidence is below 70%.
    """
    consensus_results = []
    dissenting_views = []

    for council, response in ai_responses.items():
        final_decision_match = re.search(r"\*\*FAIV Consensus:\*\* (.+)", response)
        confidence_match = re.search(r"\*\*Confidence Score:\*\* (\d+)%", response)
        justification_match = re.search(r"\*\*Justification:\*\* (.+)", response)

        if not final_decision_match or not confidence_match:
            continue  # Skip malformed responses

        # Extract values
        final_decision = final_decision_match.group(1).strip()
        confidence = int(confidence_match.group(1))
        justification = justification_match.group(1).strip() if justification_match else "No justification provided."

        # Remove emojis (if any)
        final_decision = remove_emojis(final_decision)
        justification = remove_emojis(justification)

        consensus_results.append({
            "council": council,
            "decision": final_decision,
            "confidence": confidence,
            "justification": justification
        })

    # **Determine Final Consensus (Highest Confidence Take)**
    if not consensus_results:
        return "⚠ No valid FAIV consensus was reached."

    final_consensus = max(consensus_results, key=lambda x: x["confidence"])
    final_confidence = final_consensus["confidence"]

    # **Identify Differing Perspectives (Only Confidence < 85%)**
    dissenting_views = [
        result for result in consensus_results
        if result["decision"] != final_consensus["decision"] and result["confidence"] < 85
    ]

    # **Build Final Output**
    output = f"🏛 **FAIV Final Decision**\n"
    output += f"🔹 **Consensus:** {final_consensus['decision']}\n"
    output += f"📊 **Confidence Score:** {final_confidence}%\n"
    output += f"💡 **Justification:** {final_consensus['justification']}\n\n"

    # **Include Differing Opinions (if any)**
    if dissenting_views:
        output += "⚠ **Differing Outlooks:**\n"
        for dissent in dissenting_views:
            output += f"🔹 **{dissent['council']} Council ({dissent['confidence']}%)**: {dissent['decision']}\n"
            output += f"📌 **Reason:** {dissent['justification']}\n\n"

    return output.strip()

# ------------------------------------------------
# 5) FastAPI Route Definition
# ------------------------------------------------
class QueryRequest(BaseModel):
    input_text: str

@fastapi_app.post("/query/")
@fastapi_app.post("/query/")
async def query_faiv(request: QueryRequest):
    logger.info(f"📡 Incoming Query: {request.input_text}")

    try:
        # 1) Create a single combined prompt
        combined_prompt = create_faiv_compressed_prompt(request.input_text)
        # This prompt should mention all councils from the Identity Codex at once
        # so GPT knows it must simulate them internally, then produce a single final decision.

        # 2) Call GPT-4 once
        raw_ai_response = query_openai_faiv(combined_prompt, "FAIV High Council")

        logger.info(f"📜 Raw AI Response:\n{raw_ai_response}")

        # 3) If you want to remove emojis on the server side
        cleaned_response = remove_emojis(raw_ai_response)

        # 4) Return the cleaned response directly, or parse further if you like
        return {
            "status": "✅ FAIV Processing Complete",
            "response": cleaned_response
        }

    except Exception as e:
        logger.error(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def remove_emojis(text):
    """
    Removes emojis from a given text while preserving readability.
    """
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols & Others
        u"\U0001FA70-\U0001FAFF"  # Symbols for Legacy Computing
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed Characters
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', text)

# ------------------------------------------------
# 6) Wrap FastAPI with Flask + WSGI for Production
# ------------------------------------------------
# For production environments (e.g. Passenger), expose a WSGI callable.
flask_app = Flask(__name__)
flask_app.wsgi_app = WSGIMiddleware(fastapi_app)
# When running under a WSGI server (e.g. Passenger), use flask_app as the application.
if __name__ != "__main__":
    application = flask_app

# For local development, you can run the FastAPI app directly using uvicorn.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("faiv_app.core:fastapi_app", host="127.0.0.1", port=8000, reload=True)
