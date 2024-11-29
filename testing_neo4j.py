# create_supporting_statement(1, "statement that super supports human-caused climate changed.")

# driver.close()

########### Code to make our arguments network :) 

import subprocess
import pydantic
from typing import List
import openai 
import datetime
import json
from typing import Dict
import random
import threading
import os
#lock = threading.Lock()

Researchathon_api_key='/'

# OPENAI SETUP STUFF

def call_completions_string(prompt,system_instructions="You are a helpful assistant.",model="gpt-4o-mini"):
  openai.api_key = Researchathon_api_key
  response = openai.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": prompt}
    ]
  )
  return response.choices[0].message.content

client = openai.OpenAI(api_key=Researchathon_api_key)

def call_completions_structured(prompt,system_instructions="You are a helpful assistant.",model="gpt-4o-mini",pylance_structure=None,debug=False,temperature=1.0):
  global client
  if pylance_structure=="":
    print("No structure provided",end="",flush=True)
    return ''
  try:
    start=datetime.datetime.now()
    completion = client.beta.chat.completions.parse(
      model=model,
      messages=[
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": prompt}
    ],
      response_format=pylance_structure)
    if debug:
      print(f"Time taken for completion: {datetime.datetime.now()-start}",flush=True)
  except Exception as e:
    print(f"Error in call_completions_structured when calling the API" ,e)
    return 
  # string_formatted_response = remove_special_characters(completion.choices[0].message.content)
  response_content=completion.choices[0].message.content
  
  return response_content

######## LOGICCCCCC woooo

class Statement(pydantic.BaseModel):
  statement: str

class SupportingRule(pydantic.BaseModel):
    supporting_statement: Statement
    supported_statement: Statement

class Argument_(pydantic.BaseModel):
    supporting_statements: List[Statement]
    supporting_rules: List[SupportingRule]
    conclusion:Statement

def make_argument(statement="humans cause climate change"):
  Argument_maker_sys_inst= "Take this proposition and create a supporting argument for it where the proposition given is the conclusion. Supporting rules connect supporting statements (premises) to the conclusion. Please provide you response according to the structure provided."
  response=call_completions_structured(system_instructions=Argument_maker_sys_inst,prompt=statement,pylance_structure=Argument_)
  if isinstance(response, str):
    dict=json.loads(response)
  else:
    dict=response
  return dict 


######## simple node creation flow with neo4j python package 

import neo4j

uri = "bolt://localhost:7687"
username = "neo4j"
password = "m@k3!tf)k!ngCon$isten-t"

driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

def create_supporting_statement( _text):
    with driver.session() as session:
        q1 = "CREATE (s:Statement) SET s.text = $_text"
        nodes = session.run(q1, _text=_text)

def add_edge(_supporting_statement, _conclusion):
   with driver.session() as session:
       q2 = "MATCH (s1:Statement {text: $_supporting_statement}) MATCH (s2:Statement {text: $_conclusion}) CREATE (s1)-[:supports]->(s2)"
       nodes = session.run(q2, _supporting_statement = _supporting_statement, _conclusion = _conclusion)

#can I make some linked nodes?

test = make_argument()

conclusion = test["conclusion"].get("statement")
conclusion_node = create_supporting_statement(conclusion)

for supporting_statement in test["supporting_statements"]:
  
  _supporting_statement = supporting_statement.get("statement")
  create_supporting_statement(_supporting_statement)
  add_edge(_supporting_statement, conclusion)

driver.close()






