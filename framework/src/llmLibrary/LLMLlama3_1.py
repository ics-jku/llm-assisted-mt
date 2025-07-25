from src.llmLibrary.llmBase import LLMBase

class LLMLlama3(LLMBase):
    def __init__(self, role, reproducible, temperature, top_p, reload_after ):
        super().__init__("meta-llama/Meta-Llama-3.1-8B-Instruct", <INSERT_TOKEN>, "text-generation", reproducible, 4096, temperature, top_p, reload_after)
        self.role = role

    def Prompt(self, prompt):
        messages = [{"role": "system", "content": self.role},
                    {"role": "user", "content": prompt}]
    
        return self.SendPrompt(messages)
    
    
