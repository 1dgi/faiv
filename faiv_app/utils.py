import tiktoken  # OpenAI's actual token counter

def optimize_tokens(input_text: str, max_tokens=800):
    """Trims input_text to stay within max_tokens before API call."""
    
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 token encoding
    tokens = encoding.encode(input_text)
    
    # Trim excess tokens if over limit
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    
    return encoding.decode(tokens)  # Convert back to string
