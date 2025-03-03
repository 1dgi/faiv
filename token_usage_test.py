import openai
import time
import pandas as pd

# ✅ Initialize OpenAI Client
client = openai.OpenAI()

# ✅ Define the prompts to test
prompts = [
    "What country should I visit and why?",
    "Explain quantum mechanics in simple terms.",
    "Summarize the plot of 'The Lord of the Rings'.",
    "Describe the process of photosynthesis.",
    "How does artificial intelligence impact the job market?"
]

# ✅ Function to measure token usage
def measure_tokens(prompt):
    """ Sends a request to OpenAI and measures token usage. """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        tokens_used = response.usage.total_tokens
        return tokens_used, response.choices[0].message.content

    except Exception as e:
        return None, f"Error: {str(e)}"

# ✅ Run the test and store results
results = []

for prompt in prompts:
    print(f"Testing: {prompt}")
    tokens, response = measure_tokens(prompt)
    
    if tokens is not None:
        print(f"Tokens Used: {tokens}")
    else:
        print("Failed to retrieve token usage.")

    results.append({"Prompt": prompt, "Tokens Used": tokens, "Response": response})
    
    # ✅ Rate limit handling
    time.sleep(1.5)  # Avoid hitting API rate limits

# ✅ Convert results to DataFrame
df = pd.DataFrame(results)

# ✅ Save results to CSV
df.to_csv("token_usage_results.csv", index=False)

# ✅ Display results
import ace_tools as tools
tools.display_dataframe_to_user(name="Token Usage Results", dataframe=df)
