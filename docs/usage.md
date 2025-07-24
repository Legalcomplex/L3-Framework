**Overview**

The codebase is written to be ran locally, via cloning. It is in its early stages, with roadmap planned (see roadmap for more information).


**How to run**
* pip install requirements.txt
* have your router api key in your env
* run code
```
s3_eval(
    {
        "prompt" : ["list of string prompts"],
        "model" : ["list of models"]
    }
)

reset_log_number() # for log monitoring

```

s3_eval api requires the dictionary input, optional country for legal assessment (str), and optional run times (int). 
