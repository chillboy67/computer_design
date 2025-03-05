from zhipuai import ZhipuAI

api_key = ''

def get_LLM_response(prompt):

    client = ZhipuAI(api_key=api_key)  
    response = client.chat.completions.create(
        model="glm-4-flash", 
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    
    print(response.choices[0].message.content)

    return response.choices[0].message.content