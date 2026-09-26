"""Distinguish transport/output failures from actual model answers."""
from .common import InvalidExperiment

class ResponseFailure(InvalidExperiment):
    def __init__(self, kind, metadata):
        self.kind=kind
        self.metadata=metadata
        super().__init__(kind)

def response_text(raw):
    raw=raw if isinstance(raw,dict) else {}
    choices=raw.get('choices')
    choice=choices[0] if isinstance(choices,list) and choices and isinstance(choices[0],dict) else {}
    message=choice.get('message') if isinstance(choice.get('message'),dict) else {}
    content=message.get('content')
    usage=raw.get('usage') if isinstance(raw.get('usage'),dict) else {}
    details=usage.get('completion_tokens_details') if isinstance(usage.get('completion_tokens_details'),dict) else {}
    finish=choice.get('finish_reason')
    # Whitelist metadata rather than persist arbitrary server bodies or reasoning text.
    metadata={'finish_reason':finish if finish in ['stop','length','content_filter','tool_calls','function_call'] else 'unknown',
              'content_chars':len(content) if isinstance(content,str) else 0,
              'has_reasoning_content':bool(message.get('reasoning_content')),
              'has_refusal':bool(message.get('refusal')),
              'prompt_tokens':usage.get('prompt_tokens') if isinstance(usage.get('prompt_tokens'),int) else None,
              'completion_tokens':usage.get('completion_tokens') if isinstance(usage.get('completion_tokens'),int) else None,
              'reasoning_tokens':details.get('reasoning_tokens') if isinstance(details.get('reasoning_tokens'),int) else None}
    if finish=='length':raise ResponseFailure('truncated_response',metadata)
    if not isinstance(content,str) or not content.strip():raise ResponseFailure('empty_response',metadata)
    return content
