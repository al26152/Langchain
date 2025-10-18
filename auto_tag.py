import re
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

# 1. Build your prompt template once
from langchain_core.prompts import PromptTemplate
TAG_PROMPT = PromptTemplate.from_template(
    "Assign a Theme and Audience for this excerpt:\n\n{content}\n\n"
    "Respond exactly:\n"
    "Theme: <theme>\n"
    "Audience: <audience>"
)

# 2. Initialise your LLM client
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 3. Auto-tag helper
def auto_tag(snippet: str) -> tuple[str, str]:
    """
    Returns (theme, audience) for the given text snippet.
    """
    # Format the prompt
    prompt_str = TAG_PROMPT.format(content=snippet)
    
    # Direct ChatOpenAI call with a list of messages
    response_msg = llm([HumanMessage(content=prompt_str)])
    
    # Extract raw text
    raw = response_msg.content
    
    # Parse out exactly what you expect
    theme    = re.search(r"Theme:\s*(.+)", raw).group(1).strip()
    audience = re.search(r"Audience:\s*(.+)", raw).group(1).strip()
    return theme, audience