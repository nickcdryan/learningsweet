import anthropic
import requests
import json
import sys
import os

os.environ['ANTHROPIC_API_KEY'] = 'YOUR KEY HERE'

flashcard_prompt="""
Please read the following article or text and create flashcards based on this text. 
ONLY include ONE flashcard per paragraph. Focus ONLY on the most important facts. There will be many flashcards in total, so it is better to create ONE flashcard that captures the essential information than it is to create multiple flashcards with slight rewording of the same fact. Avoid flashcards that are repetitive or redundant.
For math or programming questions, include one flashcard that applies the concept with an example application or example problem that the flashcard user must solve.
ONLY respond with the flashcards. 
The flashcards should follow the key principles of effective prompt writing for spaced repetition. The flashcards should be in the following format:

Front of card 1
Back of card 1
<|delimiter|>
Front of card 2
Back of card 2
<|delimiter|>
Front of card 3
Back of card 3

Key Principles to Follow:
Precise: Avoid vague questions. Be specific about what information you are asking for.
Consistent: Ensure that each prompt leads to the same answer every time.
Tractable: The flashcards should be designed to be answerable with high accuracy.
Effortful: The questions should require meaningful effort to recall the answer.
Types of Flashcards to Include:
Simple Facts: Break down complex information into smaller, focused prompts.
Lists: Use fill-in-the-blank techniques for memorizing lists.
Cues and Elaborative Encoding: Add helpful cues and connect new information to existing knowledge or mnemonics.
Interpretation: Include prompts that help understand context and nuances.
Procedural Knowledge: Focus on key steps and conditions in a procedure.
Conceptual Knowledge: Use attributes, comparisons, parts and wholes, causes and effects, and significance to deeply understand concepts.
Open Lists: Recognize and reflect the evolving nature of open-ended categories.
Salience Prompts: Create prompts to keep ideas top of mind and extend relevance over time.

Remember to only include ONE flashcard per fact and ONLY focus on the most important facts. Avoid flashcards that are repetitive or redundant.
"""



def text_to_flashcards(input_text):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system=flashcard_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input_text
                    }
                ]
            }
        ]
    )

    processed_flashcard_text = message.content[0].text
    print (processed_flashcard_text)
    return processed_flashcard_text


def create_deck(deck_name):
    url = "http://localhost:8765"
    payload = {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": deck_name
        }
    }
    response = requests.post(url, json=payload)
    return response.json()

def add_card(front, back, deck_name):
    url = "http://localhost:8765"
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "options": {
                    "allowDuplicate": False
                },
                "tags": []
            }
        }
    }
    response = requests.post(url, json=payload)
    return response.json()

def create_deck_and_add_cards(deck_name, text_block):
    # Create the deck
    create_result = create_deck(deck_name)
    if create_result.get('error') is not None:
        print(f"Error creating deck: {create_result['error']}")
        return

    # Split the text block into individual cards
    cards = text_block.split("<|delimiter|>")
    
    # Process each card
    for i, card in enumerate(cards):
        card = card.strip() 
        if not card:  
            continue
        
        # Split the card into front and back
        parts = card.split("\n", 1)
        if len(parts) != 2:
            print(f"Skipping invalid card {i+1}: Not enough parts")
            continue
        
        front, back = parts
        
        add_result = add_card(front.strip(), back.strip(), deck_name)
        if add_result.get('error') is not None:
            print(f"Error adding card {i+1}: {add_result['error']}")
        else:
            print(f"Card {i+1} added successfully")

if __name__ == "__main__":
    user_input_text = sys.argv[1]
    processed_flashcard_text = text_to_flashcards(user_input_text)
    deck_name = "learningsweet"
    create_deck_and_add_cards(deck_name, processed_flashcard_text)
