from .common import require

class Counter:
    def __init__(self,spec):
        self.spec=dict(spec);self.kind=spec['kind']
        if self.kind=='utf8_smoke':self.encode=lambda s:list(s.encode('utf-8'))
        elif self.kind=='tiktoken':
            import tiktoken
            self.tk=tiktoken.get_encoding(spec['encoding']);self.encode=lambda s:self.tk.encode(s,disallowed_special=())
        elif self.kind=='hf':
            from transformers import AutoTokenizer
            require(spec.get('model') and spec.get('revision'),'Pin tokenizer model and revision')
            self.tk=AutoTokenizer.from_pretrained(spec['model'],revision=spec['revision'],trust_remote_code=False)
            self.encode=lambda s:self.tk.encode(s,add_special_tokens=False)
        else:raise ValueError('Tokenizer kind must be hf, tiktoken, or utf8_smoke')
    def count(self,text):return len(self.encode(text))
