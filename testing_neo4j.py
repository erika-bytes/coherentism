# Import statements

import subprocess
import pydantic
from typing import List
import openai 
from datetime import datetime
import json
from typing import Dict
import random
import threading
import os
import neo4j
#import datetime
from copy import deepcopy
import time
from datetime import timedelta, datetime
from collections import deque

lock = threading.Lock()

Researchathon_api_key='/'

# Setup OpenAI stuff

client = openai.OpenAI(api_key=Researchathon_api_key)

class RateLimiter:
  def __init__(self,requests_per_minute):
    self.requests_per_minute=requests_per_minute
    self.window=60
    self.requests=deque()
    self.lock=threading.Lock()
    self.monitor_thread=threading.Thread(target=self.monitor)
    self.monitor_thread.daemon=True
    self.monitor_thread.start()
  def monitor(self):
    while True:
      time.sleep(60)
      with self.lock:
        print(f"Number of requests in the last {self.window} seconds: {len(self.requests)}",flush=True,end=" ")
  def aquire(self):
     with self.lock:
        now=datetime.now()
        # remove requests that are older than the window
        while self.requests and self.requests[0]< now-timedelta(seconds=self.window):
          self.requests.popleft()
        # if the number of requests in the current window is greater than the limit, sleep until the next window
        if len(self.requests)>= self.requests_per_minute:
           sleep_time= (self.requests[0]+timedelta(seconds=self.window)-now).total_seconds()
           if sleep_time>0:
              time.sleep(sleep_time)
        self.requests.append(now)

rate_limiter=RateLimiter(requests_per_minute=5000)

def call_completions_structured(prompt,system_instructions="You are a helpful assistant.",model="gpt-4o-mini",pylance_structure=None,debug=False,temperature=1.0,eval_response=False):
  global client
  if pylance_structure=="":
    print("No structure provided",end="",flush=True)
    return ''
  try:
    start=datetime.now()
    rate_limiter.aquire()
    completion = client.beta.chat.completions.parse(
      model=model,
      messages=[
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": prompt}
    ],
      response_format=pylance_structure)
    if debug:
      print(f"Time taken for completion: {datetime.now()-start}",flush=True)
  except Exception as e:
    print(f"Error in call_completions_structured when calling the API" ,e)
    return 
  # string_formatted_response = remove_special_characters(completion.choices[0].message.content)
  response_content=completion.choices[0].message.content
  dict=json.loads(response_content)
  return dict

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

class Arguments_(pydantic.BaseModel):
    Arguments: List[Argument_]

def make_argument(statement="humans cause climate change"):
  Argument_maker_sys_inst= "Take this proposition and create a supporting argument for it where the proposition given is the conclusion. Statements are the premises of the argument, they must be reasonable atomic statements where the meaning is clear and the statement is not a compound sentence. Avoid creating statements that could be broken down into separate sentences, for example instead of creating a statement like ' x is caused by a,b,c' create separate statements 'x is caused is caused by a', 'x is caused by b' , 'x is caused by c' instead. Supporting rules connect supporting statements (premises) to the conclusion. Please provide you response according to the structure provided."
  response=call_completions_structured(system_instructions=Argument_maker_sys_inst,prompt=statement,pylance_structure=Argument_)
  if isinstance(response, str):
    dict=json.loads(response)
  else:
    dict=response
  return dict 
# print (make_argument("Ultraprocessed foods are responsible for obesity."))

# Set up neo4j driver stuff

uri = "bolt://localhost:7687"
username = "neo4j"
password = "m@k3!tf)k!ngCon$isten-t"

driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

# Create nodes, edges in DB. Node creation uses merge to avoid node duplication (including in successive recursive runs lol), and edge creation matches on node text

def create_supporting_statement( _text):
    with driver.session() as session:
        q1 = "MERGE (s:Statement {text: $_text}) RETURN s"
        nodes = session.run(q1, _text=_text)
        add_similarity_edges(target_node=_text)
        # find_duplicates(0.5,_text)
        # add_source(_text, session)

# def add_unique(queue):
#     for node in queue:
#         create_supporting_statement(node)
#         add_edge(node._supporting_statement, node.conclusion)

# queue = []

# def add_to_queue():
#     queue.append()


def add_edge(_supporting_statement, _conclusion):
   with driver.session() as session:
       q2 = "MATCH (s1:Statement {text: $_supporting_statement}) MATCH (s2:Statement {text: $_conclusion}) CREATE (s1)-[:supports]->(s2)"
       nodes = session.run(q2, _supporting_statement = _supporting_statement, _conclusion = _conclusion)

def clean_db():
    """clear database contents"""
    with driver.session() as session:
        query = """
            MATCH (n) DETACH DELETE n;
        """
        session.run(query)

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

def add_similarity_edges(target_node):
    query = """
    MATCH (n1:Statement {text: $target_node})
    MATCH (n2)
    WHERE n1<>n2
    WITH n1, n2, apoc.text.sorensenDiceSimilarity(n1.text, n2.text) AS similarity
    WHERE similarity > 0
    MERGE (n1)-[r:SIMILARITY]->(n2)
    SET r.weight = similarity;
    """

    with driver.session() as session:
        session.run(query, target_node=target_node)

# IN PROGRESS - identify edges with sd similarity above a certain threshold
statement1="God exists."
statement2="Quarter buttoned waffle shirts are cozy."
def campare_meanings(node1, node2):
  class Statement(pydantic.BaseModel):
    evaluation: bool
    explanation: str
  
  system_inst="You are a philosopher experienced in formal logic. You are given two statements and must determine with a high lever of rigour whether they have the same meaning. When avaluating two statemens A and B first ask yourself could there be any statements that lead to B that do not lead to A. If there is any statement that could lead to one of the given statements and not the other they do not have the same meaning. Provide your response in the structure provided, where evaluation is true if the statements have the same meaning and false otherwise, also provide an explanation for your evaluation in a few sentences."
  response=call_completions_structured(system_instructions=system_inst,prompt=(str(node1)+" "+str(node2)),pylance_structure=Statement,eval_response=True)
  return response
# for i in range(10):
#   print(campare_meanings(statement1,statement2)["evaluation"],end=" ")


def do_merge(node, session):
    text_1 = node["target"]['text']
    text_2 = node["b"]['text']
    if campare_meanings(text_1,text_2)["evaluation"]:
        query_merge = """

            MATCH (s1:Statement {text: $text_1}), (s2:Statement {text: $text_2})
            WITH s1, s2
            MATCH (s2)-[r:supports]->(other)
            MERGE (s1)-[r_new:supports]->(other) 
            SET r_new += properties(r)

            WITH s1, s2
            MATCH (other)-[r:supports]->(s2)
            MERGE (other)-[r_new:supports]->(s1)
            SET r_new += properties(r)

            DETACH DELETE s2
            RETURN s1;
        
        """
        with lock:
            merge_nodes = session.run(query_merge, text_1 = text_1, text_2 = text_2)
        print(text_1, end=' ', flush=True)
        print("merged with", end=' ', flush=True)
        print(text_2, end=' ', flush=True)
    print(".", end=' ', flush=True)
    

def find_all_duplicates():
    """run find duplicates for every node in the database"""

    # get all db nodes
    query = """
    MATCH (n)
    RETURN DISTINCT n;
    """
    with driver.session() as session:
        nodes = session.run(query)
        # deduplicate each nodes
        for node in nodes:
            print(node["n"]["text"])
            find_duplicates(0.5,node["n"]["text"])

def refine_argument(statement, depth):
    decompose_argument(statement, depth)
    find_all_duplicates()


def find_duplicates(threshold,target_node_text):    
    query = """
    MATCH (target:Statement {text: $target_node_text})
    MATCH (target)-[r:SIMILARITY]->(b)
    WHERE r.weight > $threshold
    RETURN target, r, b;
    """

    with driver.session() as session:
      nodes = session.run(query, threshold=threshold, target_node_text=target_node_text)
      threads = [] 
      for node in nodes:
        thread=threading.Thread(target=do_merge,args=(node, session))
        threads.append(thread)
      for thread in threads:
        thread.start()
      for thread in threads:
        thread.join()
        # text_1 = node["target"]['text']
        # text_2 = node["b"]['text']
        # if campare_meanings(text_1,text_2)["evaluation"]:
        #         candidates.append(text_2)
        #         query_merge = """

        #             MATCH (s1:Statement {text: $text_1}), (s2:Statement {text: $text_2})
        #             WITH s1, s2
        #             MATCH (s2)-[r:supports]->(other)
        #             MERGE (s1)-[r_new:supports]->(other) 
        #             SET r_new += properties(r)

        #             WITH s1, s2
        #             MATCH (other)-[r:supports]->(s2)
        #             MERGE (other)-[r_new:supports]->(s1)
        #             SET r_new += properties(r)

        #             DETACH DELETE s2
        #             RETURN s1;
                
        #         """
        #         merge_nodes = session.run(query_merge, text_1 = text_1, text_2 = text_2)
        #         print(text_1)
        #         print("merged with")
        #         print(text_2)
                # print("merged nodes with statements: {text_1}, {text_2}")

        # print(f"found {len(candidates)} candidates")
        # print (candidates)

# def add_source(text, session):
#     class Source(pydantic.BaseModel):
#         link: str
  
#     system_inst="For the given claim, please find a real, reputable source that supports it and provide an active link to it. Please make sure the URL does not lead to a 404 page."
#     response=call_completions_structured(system_instructions=system_inst,prompt=(text),pylance_structure=Source)
#     # print(type(response))
#     link = response["link"]
#     query = """
#         MATCH (s1:Statement {text: $text})
#         SET s1.source = $link 
#     """
#     session.run(query, text = text, link = link)
    
def hypothesize(nodes: list):
    """ creates a possible parent statement for a given set of nodes """
    Argument_maker_sys_inst= "Take this list of supporting statements and find a conclusion for which the group of statements provides sufficient justification. Please make sure that all of the supporting statements contribute to the justification of the conclusion you've created. Avoid creating a conclusion that could be broken down into separate sentences if possible. Supporting rules connect the supporting statements (premises) you've been given to the conclusion you've created. Please provide you response according to the structure provided."
    response=call_completions_structured(system_instructions=Argument_maker_sys_inst,prompt=nodes,pylance_structure=Argument_)
    if isinstance(response, str):
        dict=json.loads(response)
    else:
        dict=response
    #create new potential conclusion node
    conclusion = response["conclusion"].get("statement")
    conclusion_node = create_supporting_statement(conclusion)
    #create edges from original statements to new node differentiated as may support
    with driver.session() as session:
        for supporting_statement in response["supporting_statements"]:
            statement = supporting_statement["statement"]
            q2 = "MATCH (s1:Statement {text: $supporting_statement}) MATCH (s2:Statement {text: $conclusion}) CREATE (s1)-[:maysupport]->(s2)"
            nodes = session.run(q2, supporting_statement = statement, conclusion = conclusion)

def trace_path(node1: str, node2: str):
    """traces the path from one statement to another, returns an ordered list of statements in the path"""
    with driver.session() as session:
        query = """
            MATCH (start {text: $node1}), (end {text: $node2})
            CALL apoc.path.expandConfig(start, {endNodes: [end], uniqueness: "NODE_GLOBAL", relationshipFilter: ">", bfs: true}) 
            YIELD path
            RETURN [node IN nodes(path) | node.text] AS texts
        """
        path = session.run(query, node1 = node1, node2 = node2)
        print(path.single()["texts"])

#### TESTINGGGG

#clean_db()
start = datetime.now()
#decompose_argument(statement2, 3)
#print(datetime.datetime.now() - start)
refine_argument(statement2, 3)
# testing_statement_list = [
#  ,,,
# ]
# hypothesize(str(testing_statement_list))
#find_all_duplicates()
#trace_path(,)
print(datetime.now() - start)
#print (find_duplicates(0.5,))


# decompose_argument("Ultraprocessed foods are responsible for obseity.", 3)

# uncomment this if you want to add similarity edges
# add_similarity_edges()
   
driver.close()