import os
import google.generativeai as genai
from dotenv import load_dotenv
from parse_youtube import get_youtube_transcript
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

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

# Global memory instance to maintain conversation history
conversation_memory = ConversationBufferMemory()

def incorporate_feedback(llm, transcript_text, current_title, current_description, user_feedback, memory=None):
    """
    Generate new title and description based on user feedback with memory context
    Uses two separate LLM calls for better reliability
    
    Args:
        llm: LangChain LLM instance
        transcript_text (str): Original video transcript
        current_title (str): Current title that needs improvement
        current_description (str): Current description that needs improvement
        user_feedback (str): User's feedback on what to improve
        memory: ConversationBufferMemory instance (optional)
        
    Returns:
        dict: Dictionary containing new title and description
    """
    if memory is None:
        memory = conversation_memory
    
    # Create a conversation chain with memory
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    # First LLM call: Generate improved title
    title_prompt = f"""
    Based on the following context, please generate an improved YouTube title according to the user's feedback:
    
    ORIGINAL TRANSCRIPT: {transcript_text[:1000]}...
    CURRENT TITLE: {current_title}
    USER FEEDBACK: {user_feedback}
    
    Generate a new, engaging YouTube title (max 15 words) that incorporates the feedback.
    Respond with ONLY the title, no additional text or formatting. 
    DO NOT INCLUDE YOUR THOUGHT PROCESS IN THE TITLE.
    """
    
    # Second LLM call: Generate improved description
    description_prompt = f"""
    Based on the following context, please generate an improved YouTube description according to the user's feedback:
    
    ORIGINAL TRANSCRIPT: {transcript_text[:1000]}...
    CURRENT DESCRIPTION: {current_description}
    USER FEEDBACK: {user_feedback}
    
    Generate a comprehensive and engaging YouTube description (max 300 words) that incorporates the feedback.
    Respond with ONLY the description, no additional text or formatting.
    DO NOT INCLUDE YOUR THOUGHT PROCESS IN THE DESCRIPTION.
    """
    
    try:
        # Get improved title
        new_title = conversation.predict(input=title_prompt).strip()
        if not new_title:
            new_title = "Can't Retrieve"
            
        # Get improved description
        new_description = conversation.predict(input=description_prompt).strip()
        if not new_description:
            new_description = "Can't Retrieve"
        
        return {
            "title": new_title,
            "description": new_description,
            "feedback_applied": user_feedback
        }
        
    except Exception as e:
        print(f"Error in incorporate_feedback: {e}")
        return {
            "title": "Can't Retrieve",
            "description": "Can't Retrieve",
            "error": str(e)
        }

def clear_memory():
    """
    Clear the conversation memory
    """
    global conversation_memory
    conversation_memory.clear()

def get_memory_summary():
    """
    Get a summary of the conversation memory
    """
    return conversation_memory.buffer

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
            
            # 4. Feedback loop
            print("\n" + "="*50)
            print("🔄 Interactive Feedback Loop")
            print("="*50)
            
            # Keep track of current title and description for iterations
            current_title = title
            current_description = description
            iteration = 1
            
            while True:
                # Display current title and description
                print(f"\n📌 Current Title (Iteration {iteration}): {current_title}")
                print(f"📌 Current Description (Iteration {iteration}): {current_description}")
                
                # Ask for feedback with Y/N prompt
                while True:
                    feedback_choice = input("\n💬 Do you have any feedback [Y/N]? ").strip().upper()
                    
                    if feedback_choice == 'N':
                        print("\n✅ DONE! Final results:")
                        print(f"🏆 Final Title: {current_title}")
                        print(f"🏆 Final Description: {current_description}")
                        break
                    elif feedback_choice == 'Y':
                        # Get user feedback
                        print("\n💬 Please provide your feedback on how to improve the title and description:")
                        user_feedback = input("Your feedback: ")
                        
                        if user_feedback.strip():
                            try:
                                print(f"\n🔄 Step 4.{iteration}: Applying user feedback...")
                                feedback_result = incorporate_feedback(
                                    llm=llm,
                                    transcript_text=transcript_text,
                                    current_title=current_title,
                                    current_description=current_description,
                                    user_feedback=user_feedback
                                )
                                
                                print("✅ Feedback applied successfully")
                                print("\n" + "="*30 + " RESULTS " + "="*30)
                                print(f"🆕 New Title: {feedback_result['title']}")
                                print(f"🆕 New Description: {feedback_result['description']}")
                                
                                # Update current title and description for next iteration
                                current_title = feedback_result['title']
                                current_description = feedback_result['description']
                                iteration += 1
                                
                                # Show memory summary
                                memory_summary = get_memory_summary()
                                # if memory_summary:
                                #     print(f"\n🧠 Memory Summary: {memory_summary}")
                                
                            except Exception as e:
                                print(f"❌ Error applying feedback: {e}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print("⚠️ No feedback provided, please try again")
                            continue
                        break
                    else:
                        print("❌ Please enter Y or N only")
                        continue
                
                # Break out of main loop if user chose 'N'
                if feedback_choice == 'N':
                    break
                
        else:
            print("❌ Failed to get transcript - cannot proceed with content generation")
            
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()