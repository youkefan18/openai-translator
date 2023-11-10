import sys
from inspect import ClassFoundException
from pathlib import Path
from typing import Dict

from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

sys.path.append(str(Path(__file__).resolve().parent.parent))
from langchain_model.api2d_model import Api2dLLM


class ModelFactory:
    
    @classmethod
    def get_model(cls, model:str, **kwargs) ->BaseLanguageModel:
        _model_map:Dict[str, type] = {"openai": type(ChatOpenAI), "api2d": type(Api2dLLM), "chatglm": type(ChatOpenAI)}
        model_class = model.split("-")[0]
        
        if _model_map.get(model_class) is None:
            raise ClassFoundException(f"Model class not found for key {model_class}")
        clz = _model_map.get(model_class, type(Api2dLLM))
        model_name = model.split(f"{model_class}-")[-1]
        llm = clz(model_name=model_name, *kwargs)

        if model_class == "chatglm":
            llm.openai_api_base = "http://localhost:8000/v1"

        return llm