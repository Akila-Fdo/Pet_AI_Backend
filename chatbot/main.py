import re
import os
import json
from pathlib import Path
from chatbot.agent import agent

# Keywords for intent detection
SKIN_KEYWORDS = [
    "skin", "rash", "itch", "fur", "hair loss", "scab", "wound",
    "dermatitis", "fungal", "ringworm", "mange", "scabies", "allergic",
    "infection", "lesion", "bump", "spot", "dry", "flaky", "irritation"
]

EYE_KEYWORDS = [
    "eye", "sight", "vision", "discharge", "redness", "cloudiness",
    "swelling", "inflammation", "keratitis", "blepharitis", "entropion",
    "eyelid", "tumor", "cornea", "conjunctive", "watery", "crusty"
]

def extract_image_path(user_input: str) -> str:
    """
    Extract image file path from user input.
    Supports formats like:
    - /path/to/image.jpg
    - image.jpg
    - ~/Documents/image.jpg
    """
    # Look for file paths (absolute or relative)
    path_patterns = [
        r'([/~][^\s]*\.(?:jpg|jpeg|png|gif|bmp))',  # Absolute or home paths
        r'([^/\s][^\s]*\.(?:jpg|jpeg|png|gif|bmp))'   # Relative paths
    ]
    
    for pattern in path_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            path = match.group(1)
            # Expand home directory
            if path.startswith("~"):
                path = os.path.expanduser(path)
            return path
    
    return None

def clean_agent_response(response: str) -> str:
    """
    Clean up the agent response by removing JSON formatting artifacts.
    Extracts the actual content from structured responses.
    """
    # If response contains JSON with action_input, extract that
    if '"action_input"' in response or "'action_input'" in response:
        try:
            # Try to parse as JSON
            if response.startswith('{'):
                data = json.loads(response)
                if 'action_input' in data:
                    return str(data['action_input'])
            elif '"action_input":' in response or "'action_input':" in response:
                # Extract the action_input value using regex
                match = re.search(r'"action_input":\s*"([^"]*)"', response)
                if not match:
                    match = re.search(r"'action_input':\s*'([^']*)'", response)
                if match:
                    return match.group(1)
        except:
            pass
    
    # If response contains "Action:" prefix, remove it
    if response.startswith("Action:"):
        response = response[7:].strip()
        if response.startswith("{"):
            try:
                data = json.loads(response)
                if 'action_input' in data:
                    return str(data['action_input'])
            except:
                pass
    
    # Otherwise return as-is
    return response

def detect_disease_type(user_input: str) -> str:
    """
    Detect if the user is asking about skin or eye disease.
    Returns 'skin', 'eye', or None
    """
    user_lower = user_input.lower()
    
    for keyword in SKIN_KEYWORDS:
        if keyword in user_lower:
            return "skin"
    
    for keyword in EYE_KEYWORDS:
        if keyword in user_lower:
            return "eye"
    
    return None

def run_chat():
    print("\n🐾 Pet AI Healthcare Chatbot Started")
    print("=" * 60)
    print("Welcome! I'm your veterinary assistant.")
    print("I can help with general pet health questions and diagnose")
    print("specific skin or eye issues with image analysis.\n")
    
    # Get pet type from user
    while True:
        animal = input("What type of pet do you have? (dog/cat): ").strip().lower()
        if animal in ["dog", "cat"]:
            break
        print("❌ Please enter 'dog' or 'cat'")
    
    print(f"\n✅ Great! I'll help you with your {animal.upper()}'s health.\n")
    
    # Track disease type across conversation turns
    current_disease_type = None
    
    conversation_active = True
    while conversation_active:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Bot: Goodbye! Take care of your pet! 🐾")
                conversation_active = False
                break
            
            # Detect disease type from current message
            detected_disease_type = detect_disease_type(user_input)
            
            # Update current disease type if a new one is detected
            # Otherwise, keep the previous disease type for context
            if detected_disease_type:
                current_disease_type = detected_disease_type
            
            disease_type = current_disease_type  # Use tracked disease type
            
            # Build context for the agent
            if disease_type:
                # Extract image path if provided
                image_path = extract_image_path(user_input)
                
                if image_path and os.path.isfile(image_path):
                    # SPECIAL CASE: User has skin/eye issue + provided image
                    # Call the tool directly to ensure we get the analysis
                    print("\n📸 Analyzing image with computer vision model...\n")
                    
                    from chatbot.tools import analyze_pet_image
                    try:
                        # Call the tool directly with the tracked disease type
                        tool_result = analyze_pet_image(
                            image_path=image_path,
                            animal=animal,
                            disease_type=disease_type
                        )
                        
                        # Check if tool returned an error
                        if isinstance(tool_result, dict) and "error" in tool_result:
                            enriched_input = f"""
                            The user provided an image for analysis, but there was an error:
                            Error: {tool_result['error']}
                            
                            User Message: {user_input}
                            
                            Please ask the user to try again with a valid image file.
                            """
                        else:
                            # Tool succeeded - pass the result to agent for explanation
                            enriched_input = f"""
                            DIAGNOSIS REPORT:
                            I have analyzed the {animal}'s {disease_type} using computer vision.
                            
                            Analysis Result:
                            - Disease Class: {tool_result.get('class', 'Unknown')}
                            - Confidence Score: {tool_result.get('confidence', 'N/A')}
                            
                            User's Description: {user_input}
                            
                            Please provide a detailed explanation of what this diagnosis means, including:
                            1. What the disease is
                            2. Common causes
                            3. Treatment options
                            4. When to seek veterinary care
                            5. Prevention tips if applicable
                            """
                    except Exception as e:
                        enriched_input = f"""
                        There was an error analyzing the image: {str(e)}
                        
                        User Message: {user_input}
                        
                        Please inform the user about the error and suggest they try again.
                        """
                else:
                    # User hasn't provided image yet for skin/eye issue
                    enriched_input = f"""
                    Pet Type: {animal}
                    Issue Type: {disease_type} disease
                    
                    User Query: {user_input}
                    
                    The user is asking about a {disease_type} issue. Ask them to upload a clear image
                    so you can provide a proper diagnosis. Guide them to provide the image file path.
                    Do NOT use the tool yet. Just ask for the image.
                    """
            else:
                # General health question
                enriched_input = f"""
                Pet Type: {animal}
                Issue Type: General health question
                
                User Query: {user_input}
                
                This is a general health question. Answer it directly with veterinary advice.
                Do NOT ask for images. Just provide helpful guidance.
                """
            
            # Get response from agent
            response = agent.run(enriched_input)
            
            # Clean up the response formatting
            clean_response = clean_agent_response(response)
            
            print(f"Bot: {clean_response}\n")
        
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! 🐾")
            conversation_active = False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    run_chat()