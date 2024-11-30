# Import statements

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
import neo4j
#lock = threading.Lock()

Researchathon_api_key='/'

# Setup OpenAI stuff

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

# Argument structure and make argument fxn from OG script

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


# Set up neo4j driver stuff

uri = "bolt://localhost:7687"
username = "neo4j"
password = "m@k3!tf)k!ngCon$isten-t"

driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

# Create nodes, edges in DB. Node creation uses merge to avoid node duplication (including in successive recursive runs lol), and edge creation matches on node text

def create_supporting_statement( _text):
    with driver.session() as session:
        q1 = "MERGE (s:Statement {text: $_text})"
        nodes = session.run(q1, _text=_text)

def add_edge(_supporting_statement, _conclusion):
   with driver.session() as session:
       q2 = "MATCH (s1:Statement {text: $_supporting_statement}) MATCH (s2:Statement {text: $_conclusion}) CREATE (s1)-[:supports]->(s2)"
       nodes = session.run(q2, _supporting_statement = _supporting_statement, _conclusion = _conclusion)

# Decompose an argument into successive arguments until the specified depth level is achieved

def decompose_argument(statement="", depth=2):
    if depth == 0:
        return
    else:
        seed = make_argument(statement) 
        

        conclusion = seed["conclusion"].get("statement")
        conclusion_node = create_supporting_statement(conclusion)

        for supporting_statement in seed["supporting_statements"]:
            _supporting_statement = supporting_statement.get("statement")
            create_supporting_statement(_supporting_statement)
            add_edge(_supporting_statement, conclusion)
        
        depth-=1
        for supporting_statement in seed["supporting_statements"]:
            decompose_argument(supporting_statement.get("statement"),depth)


# decompose_argument("humans are not solely responsible for climate change.", 3)

# create new edges between all nodes in graph with weights calculated by sorensen dice similarity between nodes - ref: https://neo4j.com/labs/apoc/4.3/overview/apoc.text/apoc.text.sorensenDiceSimilarity/

def add_similarity_edges():
    query = """
    MATCH (n1), (n2)
    WHERE id(n1) < id(n2)
    WITH n1, n2, apoc.text.sorensenDiceSimilarity(n1.text, n2.text) AS similarity
    WHERE similarity > 0
    MERGE (n1)-[r:SIMILARITY]->(n2)
    SET r.weight = similarity;
    """

    with driver.session() as session:
        session.run(query)

# IN PROGRESS - identify edges with sd similarity above a certain threshold

def find_duplicates(threshold):
    query = """
    MATCH (a)-[r:SIMILARITY]->(b)
    WHERE r.weight > $threshold
    RETURN a, r, b;
    """
    with driver.session() as session:
        nodes = session.run(query, threshold)
    

# TODO: threading implementation (shawty slow where depth > 3 lmao)

#### TESTINGGGG

decompose_argument("Ultraprocessed foods are responsible for obseity.", 3)

# uncomment this if you want to add similarity edges
# add_similarity_edges()
driver.close()




