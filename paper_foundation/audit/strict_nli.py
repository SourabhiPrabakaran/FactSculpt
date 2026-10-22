"""Audit-only fail-closed NLI adapter. No mock/lexical replacement is permitted."""
from dataclasses import dataclass
from typing import Dict

def label_mapping(id2label: Dict) -> Dict[int,str]:
    mapping={}
    for key,value in id2label.items():
        label=str(value).strip().lower()
        if label not in {'entailment','neutral','contradiction'}:
            raise ValueError(f'Ambiguous NLI label {value!r}; supply a documented explicit mapping.')
        mapping[int(key)]=label
    if set(mapping.values())!={'entailment','neutral','contradiction'} or len(mapping)!=3:
        raise ValueError('Expected exactly three distinct semantic NLI labels.')
    return mapping

@dataclass
class StrictNLI:
    model_name: str
    revision: str
    local_files_only: bool = True
    def __post_init__(self):
        if not self.revision or len(self.revision)!=40 or any(c not in '0123456789abcdef' for c in self.revision.lower()):
            raise ValueError('Pin an actual 40-character model commit SHA; do not use main.')
        import torch
        from transformers import AutoTokenizer,AutoModelForSequenceClassification
        self.torch=torch
        self.tokenizer=AutoTokenizer.from_pretrained(self.model_name,revision=self.revision,local_files_only=self.local_files_only)
        self.model=AutoModelForSequenceClassification.from_pretrained(self.model_name,revision=self.revision,local_files_only=self.local_files_only)
        self.mapping=label_mapping(self.model.config.id2label)
        self.model.eval()
    def predict(self,premise,hypothesis):
        inputs=self.tokenizer(premise,hypothesis,return_tensors='pt',truncation=True)
        with self.torch.no_grad():
            probabilities=self.model(**inputs).logits[0].softmax(-1).tolist()
        scores={self.mapping[i]:float(v) for i,v in enumerate(probabilities)}
        return dict(backend='huggingface_pretrained',model=self.model_name,revision=self.revision,premise=premise,hypothesis=hypothesis,scores=scores,label=max(scores,key=scores.get))
