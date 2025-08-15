import os
import google.generativeai as genai
from dotenv import load_dotenv
from parse_youtube import get_youtube_transcript
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def initialize_langchain():
    """
    Initialize LangChain LLM
    
    Returns:
        GoogleGenerativeAI: Configured LLM instance
    """
    return GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv('GEMINI_API_KEY'))

def get_title(llm, transcript_text):
    """
    Generate YouTube title using LangChain
    
    Args:
        llm: LangChain LLM instance
        transcript_text (str): Video transcript
        
    Returns:
        str: Generated title
    """
    title_prompt = PromptTemplate(
        input_variables=["transcript"],
        template="Can you create a Youtube title for this video PICK BEST ONE DON'T GIVE OPTIONS -- response no more than 15 words: {transcript}"
    )
    
    title_chain = LLMChain(llm=llm, prompt=title_prompt)
    result = title_chain.run(transcript=transcript_text)
    return result

def get_description(llm, transcript_text):
    """
    Generate YouTube description using LangChain
    
    Args:
        llm: LangChain LLM instance
        transcript_text (str): Video transcript
        
    Returns:
        str: Generated description
    """
    description_prompt = PromptTemplate(
        input_variables=["transcript"],
        template="Can you create a Youtube description for this video PICK BEST ONE DON'T GIVE OPTIONS -- response no more than 300 words don't include your thought process either just the end result: {transcript}"
    )
    
    description_chain = LLMChain(llm=llm, prompt=description_prompt)
    result = description_chain.run(transcript=transcript_text)
    return result

if __name__ == "__main__":
    # Test the functions
    test_url = "https://www.youtube.com/watch?v=qw9W6gA81eo&list=PLqMymTkulLcK_gXfkH94oNH0xLfW9W935&index=5&t=26s"
    
    print("🚀 Starting content generation process...")
    print(f"📹 Test URL: {test_url}")
    
    # Get transcript
    try:
        print("\n📝 Step 0: Getting transcript from YouTube...")
        transcript_text = get_youtube_transcript(test_url)
        
        if transcript_text:
            print("✅ Transcript retrieved successfully")
            print(f"📄 Transcript length: {len(transcript_text)} characters")
            
            # 1. Initialize LangChain
            try:
                print("\n🔧 Step 1: Initializing LangChain...")
                llm = initialize_langchain()
                print("✅ LangChain initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing LangChain: {e}")
                exit(1)
            
            # 2. Get title
            try:
                print("\n📝 Step 2: Generating title...")
                title = get_title(llm, transcript_text)
                print("✅ Title generated successfully")
                print(f"🏷️ Generated Title: {title}")
            except Exception as e:
                print(f"❌ Error generating title: {e}")
                title = "Failed to generate title"
            
            # 3. Get description
            try:
                print("\n📄 Step 3: Generating description...")
                description = get_description(llm, transcript_text)
                print("✅ Description generated successfully")
                print(f"📋 Generated Description: {description}")
            except Exception as e:
                print(f"❌ Error generating description: {e}")
                description = "Failed to generate description"            
        else:
            print("❌ Failed to get transcript - cannot proceed with content generation")
            
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()