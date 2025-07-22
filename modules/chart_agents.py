import pandas as pd
import re
from pandasql import sqldf
from openai import OpenAI
import plotly.express as px
import json
import difflib
import plotly.graph_objs as go
from sentence_transformers import SentenceTransformer
import numpy as np
import google.generativeai as genai
from modules.prompts import CHART_PROMPT_TEMPLATE
from modules.data_processing import add_datetime_column, add_time_features
from modules.entity_mapping import map_location_name, embedding_map_value, build_column_embeddings, normalize_vn, fuzzy_match_location, map_sql_values

import toml

secrets = toml.load("modules/secrets.toml")
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]



client = OpenAI(api_key=OPENAI_API_KEY)

class ChartAgent:
    def __init__(self, df, openai_client):
        self.df = df
        self.client = openai_client

    def build_prompt(self, user_request):
        columns = ", ".join([f"{col} ({str(dtype)})" for col, dtype in self.df.dtypes.items()])
        prompt = CHART_PROMPT_TEMPLATE.format(columns=columns, user_request=user_request)
        return prompt
    
    def generate_sql_and_schema(self, user_request):
        """
        Phase 1: Sinh SQL và chart schema từ AI.
        """
        prompt = self.build_prompt(user_request)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = response.choices[0].message.content
        clean_text = re.sub(r"^```json\s*", "", text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        parsed = json.loads(clean_text.strip())
        sql_query = parsed["sql"]
        chart_schema = parsed["chartSchema"]
        sql_query = map_sql_values(sql_query, self.df, user_request)
        print("Mapped response:", sql_query) #Đoạn sinh SQL query
        print("Chart schema:", chart_schema) #Đoạn sinh Schema JSON
        return sql_query, chart_schema
    


def gemini_generate(prompt, model="gemini-1.5-flash", api_key=None, **kwargs): #Có thể sử dụng 2.5 flash
    """
    Gửi prompt tới Google Generative AI (Gemini) và trả về kết quả.
    """
    api_key = api_key  or GOOGLE_API_KEY
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt, **kwargs)
    return response.text

class ChartAgentGemini:
    def __init__(self, df, api_key=None):
        self.df = df
        self.api_key = api_key

    def build_prompt(self, user_request):
        columns = ", ".join([f"{col} ({str(dtype)})" for col, dtype in self.df.dtypes.items()])
        prompt = CHART_PROMPT_TEMPLATE.format(columns=columns, user_request=user_request)
        return prompt

    def generate_sql_and_schema(self, user_request):
        """
        Phase 1: Sinh SQL và chart schema từ AI.
        """
        prompt = self.build_prompt(user_request)
        response = gemini_generate(prompt, api_key=self.api_key)
        text = response
        clean_text = re.sub(r"^```json\s*", "", text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        parsed = json.loads(clean_text.strip())
        sql_query = parsed["sql"]
        chart_schema = parsed["chartSchema"]
        sql_query = map_sql_values(sql_query, self.df, user_request)
        print("Mapped response:", sql_query) #Đoạn sinh SQL query
        print("Chart schema:", chart_schema) #Đoạn sinh Schema JSON
        return sql_query, chart_schema

