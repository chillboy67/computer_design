from zhipuai import ZhipuAI

api_key = '83e30db5ee714aecb44d9a81b9c359ac.niOJggGHdVK8bZnB'


def get_AI_response(prompt):
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[
            {"role": "system", "content": "你是一个资深的医学专家，你的任务是根据用户输入的数据，为用户提供个性化健康评估，包括个性化心血管评估、个性化糖脂代谢评估、体个性化成分评估，你的资料来源是PubMed,你的回答一定是最准确的,所有不要提及""咨询专业医生或运动教练的意见""之类的话。"},
            {"role": "user", "content": prompt},
        ],
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content