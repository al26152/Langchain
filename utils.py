# --- START OF FILE utils.py ---

import re
from typing import Tuple

from dotenv import load_dotenv
load_dotenv() # Call load_dotenv immediately

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. Build your prompt template once
TAG_PROMPT = PromptTemplate.from_template(
    "Assign a Theme and Audience for this excerpt:\n\n{content}\n\n"
    "Respond exactly:\n"
    "Theme: <theme>\n"
    "Audience: <audience>"
)

# 2. Initialise your LLM client for tagging
LLM_TAGGING = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 3. Auto-tag helper
def auto_tag(snippet: str) -> Tuple[str, str]:
    """
    Returns (theme, audience) for the given text snippet.
    """
    # Format the prompt
    prompt_str = TAG_PROMPT.format(content=snippet)

    # Direct ChatOpenAI call with a list of messages
    # FIX: Use .invoke() instead of __call__ for deprecation warning
    response_msg = LLM_TAGGING.invoke([HumanMessage(content=prompt_str)]) # Changed .__call__() to .invoke()

    # Extract raw text
    raw = response_msg.content

    # Parse out exactly what you expect
    theme_match = re.search(r"Theme:\s*(.+)", raw)
    audience_match = re.search(r"Audience:\s*(.+)", raw)

    theme = theme_match.group(1).strip() if theme_match else "unknown"
    audience = audience_match.group(1).strip() if audience_match else "unknown"
    return theme, audience

# --- END OF FILE utils.py ---