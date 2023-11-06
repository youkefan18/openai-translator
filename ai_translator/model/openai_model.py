import sys
import time
from pathlib import Path

import openai
import requests
from model import Model
from openai import error
from simplejson import errors as se
from typing_extensions import override

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import LOG


class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str):
        self.model = model
        openai.api_key = api_key
        
    @override
    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo":
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message['content'].strip() # type: ignore
                else:
                    response = openai.Completion.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip() # type: ignore

                return translation, True
            except error.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except requests.exceptions.Timeout as e:
                raise Exception(f"请求超时：{e}")
            except requests.exceptions.RequestException as e:
                raise Exception(f"请求异常：{e}")
            except se.JSONDecodeError :
                raise Exception("Error: response is not valid JSON format.")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
