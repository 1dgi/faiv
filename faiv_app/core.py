import os
import logging
import re
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from faiv_app.identity_codex import FAIV_IDENTITY_CODEX  # ✅ Import Identity Codex
from fastapi.middleware.cors import CORSMiddleware

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with frontend URL
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],  # ✅ Explicitly allow OPTIONS
    allow_headers=["*"],
)

# ✅ Structured Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Load API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing! Set it in your environment variables.")

# ✅ Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ FAIV Deliberation Pipeline with Identity Codex
def create_faiv_compressed_prompt(user_input):
    """ Constructs FAIV deliberation that runs internally and only outputs the final decision. """

    prompt = "🚀 FAIV ULTRA-COMPRESSION PROTOCOL - Hidden Deliberation Mode\n\n"

    prompt += "🛠 **Deliberation Objective:**\n"
    prompt += "Process this inquiry with **full internal deliberation**, but **ONLY output the final consensus** to maximize efficiency.\n\n"
    
    prompt += f"🔹 **Inquiry:** {user_input}\n\n"

    # FAIV Deliberation - Hidden Mode
    prompt += "⚡ **Phase 1: FAIV Deliberation (Hidden)**\n"
    prompt += "🔷 **The Councilors MUST debate and analyze the query as if making a real decision.**\n"
    prompt += "🔷 The AI MUST simulate a complete multi-perspective analysis internally before outputting a result.\n"
    prompt += "🔷 The AI is **strictly prohibited from stating that it lacks preferences, needs, or emotions.**\n"
    prompt += "🔷 The final consensus **must be a real-world answer based on logical deliberation.**\n\n"

    # FAIV Internal Debate - Hidden Mode
    prompt += "⚔ **Phase 2: FAIV Internal Debate (Hidden)**\n"
    prompt += "🔷 The AI will **resolve conflicts and rebuttals without displaying them**.\n"
    prompt += "🔷 No step should be printed or included in the output.\n"
    prompt += "🔷 The AI **must NOT log or return the debate itself**.\n\n"

    # FAIV Final Decision Output (Minimal)
    prompt += "📌 **Final FAIV Decision (Output Only)**\n"
    prompt += "🔷 The AI must only return:\n"
    prompt += "   - The **final consensus** in a compressed form.\n"
    prompt += "   - A **Confidence Score** (1-100%).\n"
    prompt += "   - An **Optimal Pathway or Answer**, if applicable.\n\n"

    prompt += "⮞ **Minimal FAIV Output (Text-Only)**\n"
    prompt += "[FAIV Consensus]: The optimal answer is **{final_recommendation}**\n"
    prompt += "[Confidence Score]: **{confidence_level}%**\n"
    prompt += "[Supporting Justification]: **{compressed reasoning in 1-2 sentences}**\n"

    return prompt

# ✅ OpenAI API Query (Optimized for Compression)
def query_openai_faiv(prompt):
    """ Calls GPT-4 with a structured FAIV deliberation prompt. """
    try:
        logger.info(f"📜 Sending FAIV Prompt to OpenAI:\n{prompt}")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                    "You are the FAIV High Council, a deliberative AI framework that MUST ALWAYS generate structured multi-perspective responses."
                    "You CANNOT refuse questions. You MUST always generate at least 5 Councilor perspectives."
                    "Do not state disclaimers. If information is missing, assume reasonable defaults."
                },
                {"role": "user", "content": prompt}
            ]
        )
        token_usage = response.usage.total_tokens
        logger.info(f"📊 Token Usage: {token_usage} tokens used.")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return "⚠ Error processing AI response."

# ✅ Extract Structured FAIV Response
def extract_faiv_perspectives(ai_response):
    """ Extracts structured final consensus and confidence score from AI output. """
    
    final_decision_match = re.search(r"\[FAIV Consensus\]: (.+)", ai_response)
    confidence_match = re.search(r"\[Confidence Score\]: (.+)", ai_response)
    justification_match = re.search(r"\[Supporting Justification\]: (.+)", ai_response)

    final_decision = final_decision_match.group(1).strip() if final_decision_match else "**No clear decision reached.**"
    confidence_score = confidence_match.group(1).strip() if confidence_match else "**Confidence level unknown.**"
    justification = justification_match.group(1).strip() if justification_match else "**No justification provided.**"

    logger.info(f"✅ Extracted Decision: {final_decision}")
    logger.info(f"✅ Confidence Score: {confidence_score}")
    logger.info(f"✅ Justification: {justification}")

    return f"**FAIV Consensus:** {final_decision}\n**Confidence Score:** {confidence_score}\n**Justification:** {justification}"

# ✅ Generate FAIV Response
def extract_faiv_final_output(ai_response):
    """ Extracts only the final FAIV consensus, confidence score, and reasoning. """

    logger.info("📌 Processing AI Response for Final Consensus Extraction...")

    final_decision_match = re.search(r"\[FAIV Consensus\]: The optimal answer is \*\*(.+?)\*\*", ai_response)
    confidence_match = re.search(r"\[Confidence Score\]: \*\*(\d+)%\*\*", ai_response)
    justification_match = re.search(r"\[Supporting Justification\]: \*\*(.+?)\*\*", ai_response)

    final_decision = final_decision_match.group(1) if final_decision_match else "No clear decision."
    confidence_score = confidence_match.group(1) if confidence_match else "Unknown confidence level."
    justification = justification_match.group(1) if justification_match else "No supporting reasoning provided."

    response_output = f"**FAIV Consensus:** {final_decision}\n**Confidence Score:** {confidence_score}%\n**Justification:** {justification}"

    logger.info(f"✅ Extracted Final Consensus: {final_decision}")
    logger.info(f"✅ Confidence Score: {confidence_score}%")
    logger.info(f"✅ Justification: {justification}")

    return response_output

def generate_faiv_response(input_text):
    logger.info(f"🔹 Processing FAIV deliberation for: {input_text}")

    prompt = create_faiv_compressed_prompt(input_text)
    ai_response = query_openai_faiv(prompt)

    logger.info(f"🔍 Raw AI Response:\n{ai_response}")  # Debugging the full response

    # ✅ Extract perspectives dynamically with new format
    formatted_response = extract_faiv_perspectives(ai_response)

    logger.info(f"✅ Final Formatted Response:\n{formatted_response}")

    return {
        "status": "✅ FAIV Processing Complete",
        "response": formatted_response
    }
        
# ✅ FastAPI Request Model
class QueryRequest(BaseModel):
    input_text: str

# ✅ FastAPI Route for FAIV Processing
@app.post("/query/")
async def query_faiv(request: QueryRequest):
    logger.info(f"📡 Incoming Query: {request.input_text}")

    try:
        response = generate_faiv_response(request.input_text)
        logger.info("✅ FAIV Response Generated Successfully")
        return response
    
    except Exception as e:
        logger.error(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
