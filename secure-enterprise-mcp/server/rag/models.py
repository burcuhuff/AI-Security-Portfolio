"""Provider boundary. AWS credentials come from the SDK credential chain."""
from dataclasses import dataclass
import os
from typing import Protocol

@dataclass(frozen=True)
class ModelResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0

class LanguageModel(Protocol):
    model_id: str
    def generate(self, system: str, prompt: str) -> ModelResult: ...

class BedrockLanguageModel:
    def __init__(self, model_id: str, region: str, client=None):
        if not model_id or not region:
            raise ValueError('Set BEDROCK_MODEL_ID and AWS_REGION explicitly')
        self.model_id = model_id
        self.region = region
        self._client = client

    def generate(self, system: str, prompt: str) -> ModelResult:
        if self._client is None:
            import boto3
            from botocore.config import Config
            self._client = boto3.client(
                'bedrock-runtime', region_name=self.region,
                config=Config(connect_timeout=5, read_timeout=45,
                              retries={'mode': 'standard', 'total_max_attempts': 2}),
            )
        response = self._client.converse(
            modelId=self.model_id,
            system=[{'text': system}],
            messages=[{'role': 'user', 'content': [{'text': prompt}]}],
            inferenceConfig={'maxTokens': 600},
        )
        if response.get('stopReason') != 'end_turn':
            raise ValueError('Model did not complete a normal text response')
        blocks = response['output']['message']['content']
        text = ''.join(block['text'] for block in blocks if 'text' in block)
        usage = response.get('usage', {})
        return ModelResult(text, usage.get('inputTokens', 0), usage.get('outputTokens', 0))

def configured_model() -> LanguageModel:
    return BedrockLanguageModel(os.getenv('BEDROCK_MODEL_ID', ''), os.getenv('AWS_REGION', ''))
