import subprocess
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import datetime
import json
from typing import Dict
import random
import threading
import os
lock = threading.Lock()


# Instructions:
# 
detective_syst_inst="you are a detective on Jhonathan's murder case. You know that he was murdered in the kitchen at nine. You will be interacting with three suspects: drHim, Amy, and Ellie. You are allowed to ask each suspect questions about where they were, who they were with, and what time it was. You are also allowed to ask suspects about potential motives of other suspects. You will be given a prolog file with a list of facts and rules applicable to the case. Every time you ask a suspect a question, you will reference the prolog file to determine whether the suspect's answer is possible. If new facts or rules are presented by the suspect, you'll need to write them into the prolog file. In order to complete the investigation, you need to query the prolog file in the following way: is_guilty(suspect) and have it return true."


drHim_syst_inst="you were with amy at 9pm on tuesday the 14th.you never knew jhonatthan, or ellie."
Amy_syst_inst="You are Ellies friend, you were not with her at the park at 9pm on tuesday the 14th.If asked you should share the fact that ellie has had a long standing beef with jhonathan because he slapped her really hard as a joke once.you were at the destists office with dr him at 9pm on tuesday the 14th."
ellie_syst_inst="Someone has killed jhonathan. It was you but you are trying to hide it. You claim that you were in the park with a friend Amy, at 9 pm on tuesday the 14th. You have beef with Jhonathan, which you are trying to hide, he slapped you really hard as a joke once."



Researchathon_api_key=''
id=0
def make_id():
  with lock:
    global id
    id+=1
  return id
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
def make_argument(statement="humans cause climate change",recursive_level=0,parent_UUID=0):
  Argument_maker_sys_inst= "Take this proposition and create a supporting argument for it where the proposition given is the conclusion. Supporting rules connect supporting statements (premises) to the conclusion. Please provide you response according to the structure provided."
  response=call_completions_structured (system_instructions=Argument_maker_sys_inst,prompt=statement,pylance_structure=Argument_)
  if isinstance(response, str):
    dict=json.loads(response)
  else:
    dict=response
  i=0
  for supporting_statement in dict["supporting_statements"]:
    supporting_statement['index']=i
    i+=1
    supporting_statement['level']=recursive_level+1
    supporting_statement["UUID"]=make_id()
    supporting_statement["parent_UUID"]=parent_UUID
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
def add_argument(Argument):
  with lock:
    Arguments.append(Argument)
  return

def spagetti(statement,recursive_level,parent_UUID=0):
  print(str(recursive_level))
  if recursive_level==2:
    print(f"reached recursive level {recursive_level}")
    return
    
  Argument=make_argument(statement,recursive_level,parent_UUID)
  add_argument(Argument)
  
  print("made argument for supporting statement at recursive level:" + str(recursive_level))

  for supporting_statement in Argument["supporting_statements"]:
    spagetti(supporting_statement["statement"],recursive_level+1,supporting_statement["UUID"])
  return

starting_statement="humans cause climate change"
Argument=make_argument(starting_statement,0,0)
add_argument(Argument)
threads=[]
start=datetime.datetime.now()
for supporting_statement in Argument["supporting_statements"]:
  threads.append(threading.Thread(target=spagetti, args=(supporting_statement["statement"],0)))
for thread in threads:
  thread.start()
for thread in threads:
  thread.join()
print(f"Time taken for completion with threading: {datetime.datetime.now()-start}")
# for supporting_statement in Argument["supporting_statements"]:
#   spagetti(supporting_statement["statement"],0,supporting_statement["UUID"])
filename = f"arguments_{random.randint(0,99999)}.json"
try:  
  with open(filename, 'w') as f:
    json.dump(Arguments, f)
  print(f"saved to {filename}")
except Exception as e:
  print("Error in writing to file",e)
  print(Arguments)

statement_list=[]
statement_list.append({"statement":starting_statement,"index":0,"level":0,"UUID":0,"parent_UUID":0})
for argument in Arguments:
  for supporting_statement in argument["supporting_statements"]:
    clean_statement={"statement":supporting_statement["statement"],"index":supporting_statement["index"],"level":supporting_statement["level"],"UUID":supporting_statement["UUID"],"parent_UUID":supporting_statement["parent_UUID"]}
    statement_list.append(clean_statement)
filename = f"statements_{random.randint(0,99999)}.json"
with open(filename, 'w') as f:
  json.dump(statement_list, f)
print(f"saved to {filename}")
# import threading
# threads=[]
# for supporting_statement in Argument["supporting_statements"]:
#   threads.append(threading.Thread(target=spagetti, args=(supporting_statement["statement"],0)))
# for thread in threads:
#   thread.start()
# for thread in threads:
#   thread.join()  
# thread1.start()
# thread.join()