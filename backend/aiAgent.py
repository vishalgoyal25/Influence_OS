from transformers import pipeline
from database import sessionLocal, GeneratedLinkedinPost

generator = pipeline("text-generation", model="gpt2")


def Generate_Linkedin_Post(prompt:str, max_length= 200):

    outputs= generator(prompt, max_length=max_length)
    post_content = outputs[0]['generated_text']

    db= sessionLocal()
    newPost = GeneratedLinkedinPost(content= post_content)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    db.close()

    return post_content


if __name__=="__main__":

    sample_prompt = "Write a short LinkedIn post about AI trends in 2025 for fintech professionals."
    print("Generating post...\n")

    post = Generate_Linkedin_Post(sample_prompt)
    print("Generated Post:-", post)

