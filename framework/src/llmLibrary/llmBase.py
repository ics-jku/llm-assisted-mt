from transformers import pipeline
import torch
import gc

class LLMBase:
    def __init__(self, model, access_token, task, reproducible, max_new_tokens, temperature, top_p, reload_after):
        self.model = model
        self.accessToken = access_token
        self.task = task
        self.reproducible = reproducible
        self.maxNewTokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.realoadAfter = reload_after

        if self.temperature != 1.0 or self.top_p != 1.0:
            self.doSample = True
        else:
            self.doSample = False

        self.internalCount = 0

        self.LoadModel()

    def LoadModel(self):
        self.internalCount = 0
        if self.accessToken != "":
            self.pipe = pipeline(self.task, model=self.model, model_kwargs={"torch_dtype": torch.bfloat16}, device="cuda:0", token=self.accessToken)
        else:
            self.pipe = pipeline(self.task, model=self.model, model_kwargs={"torch_dtype": torch.bfloat16}, device="cuda:0")
        self.terminators = [self.pipe.tokenizer.eos_token_id, self.pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")]

    def SendPrompt(self, prompt):
        if self.reproducible:
            torch.manual_seed(42)
        else:
            torch.manual_seed(-1)

        with torch.no_grad():
            outputs = self.pipe(prompt, max_new_tokens=self.maxNewTokens, eos_token_id=self.terminators, pad_token_id=self.pipe.tokenizer.eos_token_id, do_sample=self.doSample, temperature=self.temperature, top_p = self.top_p)
            if self.realoadAfter == self.internalCount:
                self.pipe = None
                gc.collect()
                torch.cuda.empty_cache()
                self.LoadModel()
            else:
                self.internalCount += 1
            return outputs[0]["generated_text"][-1]["content"]

            
        