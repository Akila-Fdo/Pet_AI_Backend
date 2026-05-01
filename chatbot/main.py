import re
import os
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
            
            # Detect disease type
            disease_type = detect_disease_type(user_input)
            
            # Build context for the agent
            if disease_type:
                # Extract image path if provided
                image_path = extract_image_path(user_input)
                
                if image_path and os.path.isfile(image_path):
                    # User provided image path, proceed with analysis
                    enriched_input = f"""
                    Pet Type: {animal}
                    Issue Type: {disease_type} disease
                    Image Path: {image_path}
                    
                    User Query: {user_input}
                    
                    Please analyze the pet image using the analyze_pet_image tool with:
                    - image_path: {image_path}
                    - animal: {animal}
                    - disease_type: {disease_type}
                    
                    Then explain the diagnosis in detail.
                    """
                else:
                    # Ask for image before proceeding
                    enriched_input = f"""
                    Pet Type: {animal}
                    Issue Type: {disease_type} disease
                    
                    User Query: {user_input}
                    
                    The user is asking about a {disease_type} issue. Ask them to upload an image
                    so you can provide a proper diagnosis. Guide them to provide the image path.
                    Do NOT call the analyze_pet_image tool yet. Wait for the image.
                    """
            else:
                # General health question
                enriched_input = f"""
                Pet Type: {animal}
                Issue Type: General health question
                
                User Query: {user_input}
                
                This is a general health question. Answer it directly with veterinary advice.
                Do NOT use the analyze_pet_image tool. Just provide helpful guidance.
                """
            
            # Get response from agent
            response = agent.run(enriched_input)
            
            print(f"Bot: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! 🐾")
            conversation_active = False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    run_chat()