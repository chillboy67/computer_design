from zhipuai import ZhipuAI

api_key = '817be447d3b5470ba10349dde056a376.wN79bG2OhaUU2Cg3'


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