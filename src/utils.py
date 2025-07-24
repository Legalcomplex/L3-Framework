import json
import os
from openai import OpenAI

os.environ['ROUTER_API_KEY'] = ROUTER_API_KEY

def llm_model(prompt,model):
    client = OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key = os.getenv("ROUTER_API_KEY")
    )
    
    completion = client.chat.completions.create(
        model = model,
        messages = chat_messages(prompt)
    )

    try:
        prompt_result = completion.choices[0].message.content
        return prompt_result
    except Exception as e:
        return "" # not None

def chat_messages(prompt):
    messages = [
            {
                "role" : "user",
                "content" : prompt
            }
        ]
    return messages


def send_request(prompt,model):
    
    prompt_result = llm_model(prompt,model)
    print(f"""
          question: {prompt}
          model_result : {prompt_result}
          """)
    
    return(prompt_result)

    
def main_loop(model_list,prompt_var):
    each_model_result = {}
    for k in range(0,len(model_list)):
        # each model
        prompts_result_list = []
        model_name = model_list[k] + "_k"
        each_model_result[model_name] = []
        # create a dictionary for that model
        for i in range (0, len(prompt_var)):
            # each prompt
            prompt_list = send_request(prompt_var[i], model_list[k])
            prompts_result_list.append(prompt_list)
        each_model_result[model_name] = prompts_result_list
    
    return each_model_result

def log_num():
    with open("log_number.txt","r") as f:
        log_number = int(f.read())    
    return log_number

def log_number_loop():
    log_number = log_num() + 1
    with open("log_number.txt","w") as w:
        w.write(str(log_number))
    # print(f"LOGNUMBER: {log_number}")
        
    return log_number

def reset_log_number():
    with open("log_number.txt","w") as w:
        w.write(str(1))

def get_log_num():
    try:
        log_number = log_number_loop()
        return str(log_number)
    except FileNotFoundError:
        reset_log_number()
    
    
def jurisdiction_str (str_1,str_2 = None, str_3=None):
    if type(str_2) == str:
        str_2, str_3 = str_3, str_2
    elif type(str_3) == int:
        str_2, str_3 = str_3, str_2
    return str_2,str_3


def save_results_externally(jurisdiction,eval_result):
    log_number = get_log_num()
    try:
        try:
            try:
                os.makedirs("results")
            except (FileExistsError, PermissionError) as e: pass
            os.makedirs("results/" + jurisdiction)
        except (FileExistsError, PermissionError) as e: pass
        with open(f'results/{jurisdiction}/data_{log_number}.json', 'w', encoding='utf-8') as f: # creates a file
            eval_result = json.dumps(eval_result)
            f.write(eval_result)
    except Exception as e: pass
    
    
def s3_eval(dict_config,run_number = None,jurisdiction = None): # main()
    
    prompt_var = dict_config['prompt']
    model_list = dict_config['model']
    eval_result = {}
    
    run_number,jurisdiction = jurisdiction_str(dict_config,run_number,jurisdiction)
    
    if run_number == None:
        loop_number = "run_"+ str(0)
        loop_eval_result = main_loop(model_list,prompt_var)
        eval_result[loop_number] = loop_eval_result
    else:
        for g in range(0,run_number):
            loop_number = "run_"+ str(g)
            loop_eval_result = main_loop(model_list,prompt_var)
            eval_result[loop_number] = loop_eval_result
    
    
    save_results_externally(jurisdiction,eval_result)
    return eval_result
            
    