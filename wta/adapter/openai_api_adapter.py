from miniagent.adapter import Adapter
import openai

class OpenAiApiCaller(Adapter):

    def get_response(self, param:dict) -> tuple[int, dict]:

        system_content = param['system_content']
        user_content = param['user_content']
        openai.api_key = param['api_key']

        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )

        result = chat_completion['choices'][0]['message']['content']

        return 1, {"result":result}

    def get_status(self) -> int:
        return 1
    
if __name__ == '__main__':
    o = OpenAiApiCaller()
    system_content = \
    """
    python code.

    def f(a:int, b:int, c:int, d:int):
        //code to generate
        return rtn
    """
    user_content = \
    """
    rtn can't be larger than d.
    if b + c > a then rtn must be less than d/2.
    complete "code to generate" area as you want to compose.

    answer only code.
    """
    prompt = dict(
        system_content = system_content,
        user_content = user_content
    )
    print(o.get_response(prompt))