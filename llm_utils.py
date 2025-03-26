from zhipuai import ZhipuAI

api_key = '817be447d3b5470ba10349dde056a376.wN79bG2OhaUU2Cg3'


def get_LLM_response(prompt):
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[
            {"role": "system", "content": "你是一个资深的医学专家，你的任务是根据用户输入的数据，为用户提供专业、准确的运动处方，包括运动项目、运动频率、运动强度，你将参考PubMed的资料。"},
            {"role": "user", "content": prompt},
        ],
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content