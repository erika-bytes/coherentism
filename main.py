from pyswip import Prolog
from pyswip import Atom
import subprocess
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import datetime
import json
from typing import Dict

# Create a Prolog instance
prolog = Prolog()

# Add facts and rules
# prolog.assertz('Person(ellie)')
# prolog.assertz(
#     "cannot_be_at_two_locations_time(was_at(X,Y,Z),was_at(X,W,Q)) :- was_at(X, Y, Z),was_at(X, W, Q),Y \\= W.Z \\= Q."
# )

# # Query Prolog
# result = list(prolog.query("parent(john, X)"))
# print(result)  # [{'X': 'mary'}]


# Instructions:
# 
detective_syst_inst="you are a detective on Jhonathan's murder case. You know that he was murdered in the kitchen at nine. You will be interacting with three suspects: drHim, Amy, and Ellie. You are allowed to ask each suspect questions about where they were, who they were with, and what time it was. You are also allowed to ask suspects about potential motives of other suspects. You will be given a prolog file with a list of facts and rules applicable to the case. Every time you ask a suspect a question, you will reference the prolog file to determine whether the suspect's answer is possible. If new facts or rules are presented by the suspect, you'll need to write them into the prolog file. In order to complete the investigation, you need to query the prolog file in the following way: is_guilty(suspect) and have it return true."


drHim_syst_inst="you were with amy at 9pm on tuesday the 14th.you never knew jhonatthan, or ellie."
Amy_syst_inst="You are Ellies friend, you were not with her at the park at 9pm on tuesday the 14th.If asked you should share the fact that ellie has had a long standing beef with jhonathan because he slapped her really hard as a joke once.you were at the destists office with dr him at 9pm on tuesday the 14th."
ellie_syst_inst="Someone has killed jhonathan. It was you but you are trying to hide it. You claim that you were in the park with a friend Amy, at 9 pm on tuesday the 14th. You have beef with Jhonathan, which you are trying to hide, he slapped you really hard as a joke once."



Researchathon_api_key='\'

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


client = OpenAI(api_key=Researchathon_api_key)

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

def query_prolog(file_path: str, query: str):
  # Construct the SWI-Prolog command
  process = subprocess.Popen(
      ["swipl","prolog.pl"],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True
  )
  # stdout,stderr = process.communicate(input="swipl")
  # print(stdout)
  # stdout,stderr = process.communicate(input="consult('prolog.pl'). ")
  # print("file_open"+str(stdout))
  # print("error"+str(stderr))
  stdout,stderr = process.communicate(input="is_guilty(drhim).")
  print(stdout)
  print (stderr)

# query_prolog('prolog.pl', 'is_guilty(drHim)')


class Statement():
  def __init__(self, statement, truth):
    self.statement = statement
    self.truth = truth

class Supporting_rule(Statement):
  def __init__(self, supported_statement:Statement, supporting_statement:Statement):
    self.supported=supported_statement
    self.supporting= supporting_statement







class Statement(BaseModel):
  statement: str
  truth: str
class SupportingRule(BaseModel):
    supporting_statement: Statement
    supported_statement: Statement

class Argument_(BaseModel):
    supporting_statements: List[Statement]
    supporting_rules: List[SupportingRule]
    conclusion:Statement

# class Arguments(BaseModel):
#     arguments: list(Argument)
def make_argument(statement="humans cause climate change"):
  Argument_maker_sys_inst= "Take this proposition and create a supporting argument for it where the proposition given is the conclusion. Supporting rules connect supporting statements (premises) to the conclusion. Please provide you response according to the structure provided."
  response=call_completions_structured (system_instructions=Argument_maker_sys_inst,prompt=statement,pylance_structure=Argument_)
  if isinstance(response, str):
    dict=json.loads(response)
  else:
    dict=response
  # for statement in dict["supporting_statements"]:
  #   if (statement["truth"]=="true" or statement["truth"]=="Truth"):
  #     statement["truth"]=True
  #   elif (statement["truth"]=="false" or statement["truth"]=="False"):
  #     statement["truth"]=False
  return dict 
make_argument()
  

def evaluate(Statement,Arguments):
  if Arguments[Statement.truth]:
    return True


# def get_cascade_statement(Statement,Arguments):
#   #get the tree of statement


Arguments=[]


def spagetti(statement,recursive_level):
  print(str(recursive_level))
  if recursive_level==5:
    print("reached recursive level 5")
    return
    
  Argument=make_argument(statement)
  Arguments.append(Argument)
  print("made argument for supporting statement at recursive level:" + str(recursive_level))
  
  for supporting_statement in Argument["supporting_statements"]:
    spagetti(supporting_statement["statement"],recursive_level+1)
  return

starting_statement="humans cause climate change"
Argument=make_argument(starting_statement)
Arguments.append(Argument)
print (Argument)
print(type(Argument))
print(type(Argument["supporting_statements"]))
for supporting_statement in Argument["supporting_statements"]:
  spagetti(supporting_statement["statement"],0)

try:  
  with open('arguments.json', 'w') as f:
    json.dump(Arguments, f)
except Exception as e:
  print(Arguments)
# while i< 10:
#   for supporting_statement in Argument["supporting_statements"]:
#     Arguments.append(make_argument(statement=supporting_statement.statement))
  
import threading
threads=[]
for supporting_statement in Argument["supporting_statements"]:
  threads.append(threading.Thread(target=spagetti, args=(supporting_statement["statement"],0)))
for thread in threads:
  thread.start()
for thread in threads:
  thread.join()  
thread1.start()
thread.join()