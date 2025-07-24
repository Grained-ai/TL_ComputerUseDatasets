import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI

from configs.configs import DEFAULT_VENDOR, LLM_DEFAULT_MODEL_NAME, VLM_DEFAULT_MODEL_NAME
class LLMFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLMFactory, cls).__new__(cls)
            cls._instance.expense = {}
        return cls._instance

    @staticmethod
    def create_llm_instance(vendor=DEFAULT_VENDOR, model_name=LLM_DEFAULT_MODEL_NAME, temperature=0.95):
        with open(Path(__file__).parent.parent / 'configs' / 'configs.yaml', 'r') as f:
            config = yaml.safe_load(f)

        return ChatOpenAI(
            temperature=temperature,
            model=model_name,
            openai_api_key=config['LLM'][vendor]['api_key'],
            openai_api_base=config['LLM'][vendor]['endpoint']
        )

    @staticmethod
    def create_vllm_instance(vendor=DEFAULT_VENDOR, model_name=VLM_DEFAULT_MODEL_NAME, temperature=0.95):
        with open(Path(__file__).parent.parent / 'configs' / 'configs.yaml', 'r') as f:
            config = yaml.safe_load(f)

        return ChatOpenAI(
            model=model_name,
            openai_api_key=config['VLM'][vendor]['api_key'],
            openai_api_base=config['VLM'][vendor]['endpoint'],
            temperature=temperature
        )

if __name__ == "__main__":
    ins = LLMFactory()
    a = ins.create_llm_instance()
    print(a.predict("HI"))