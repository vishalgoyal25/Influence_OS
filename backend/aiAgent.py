# from transformers import pipeline
from backend.database import SessionLocal, GeneratedLinkedinPost

# print("Loading AI model... Please wait.")
# generator = pipeline("text-generation", model="distilgpt2")  # Smaller & faster model

import requests

def Generate_Linkedin_Post(prompt:str, max_length: int = 200):

    # outputs= generator(prompt, max_new_tokens = max_length, num_return_sequences= 1,
    #                    truncation=True,  pad_token_id= generator.model.config.eos_token_id,
    #                    temperature=0.7, top_p=0.9,
    #                    repetition_penalty=1.2, do_sample=True)

    # post_content = outputs[0]['generated_text']

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "max_tokens": max_length,
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()

    post_content = result.get("response", "")

    # Save to DB
    db= SessionLocal()
    newPost = GeneratedLinkedinPost(content= post_content)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    db.close()

    return post_content


# Optional standalone test mode-->>

# if __name__=="__main__":

#     sample_prompt = "Write a short LinkedIn post about AI trends in 2025 for fintech professionals."
#     print("Generating post...\n")

#     post = Generate_Linkedin_Post(sample_prompt)
#     print("Generated Post:-", post)

