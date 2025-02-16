from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key="AIzaSyD5zflCCvz5dG6W-A-3SgZ-QSf-DNCdfjw"
)

# Get the result from LLM
result = llm.invoke("give deatail on kiit university")

# Convert content to Markdown
md_content = f"### Response\n\n{result.content}"

print(md_content)
