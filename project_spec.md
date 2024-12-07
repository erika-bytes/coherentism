# Coherentism
## Argument Decomposer
### Description
Creates a coherent graphical argument decomposition for a given statement.
### Capabilities
- Define coherent argument model
- LLM create argument w/ argument model
- Create nodes for each statement within the argument
- Deduplicate nodes
    - Compare on exact match
    - Compare on semantic similarity
    - Compare on meaning
    - Merge where relevant, redirect relationships
    - TODO: contextual deduplication prior to node creation?
- Recursively construct arguments for supporting statements to specified depth level 
### Requirements
- Scales to at least 100 layers of tree depth 
- Produces maximally atomic statements at any given level of depth 
- Hallucinated results minimized
- Contextually 
- Produces logically consistent deconstructions
- Relies on a set of axioms
- Customizable elements
- Model used (?)
- Axioms supported
- Definite depth

## Argument Crawler
### Description
Generate insights from and performs modifications on the argument space.
### Capabilities
- Argument scoring
- Relevance score
    - Source assignment, source ranking
    - Longest path comparison
    - Starting argument % validity score?
    - Falsity tracing
    - Visualize upstream consequences of falsified dependency
- Recomposition
- Pruning
    - Statement quality evaluation, removal where relevant
- Decomposition comparison
    - Match inverse statements in the decomposition of two arguments, determine if they are logical opposites (?) 
- Argument-to-argument mapping (a la wikipedia game) 
- Extrapolation
- Write essay (ultimate cool usage - lol)
    - Take in an essay hypothesis, crawl relevant space on the tree, aggregate relevant sources, prune irrelevant statements, assign confidence measures (to help in qualifying language) - produce a coherent essay on the given topic!
### capabilities of exploring persistent db - continued brainstorm 
def add_node_uniquely(): 
  pass

def parse_through_db(function):
  def remove_unjustifiable_nodes():
    pass
  def identify_curcular_patterns():
    pass
  pass

def non_destructive_decompose_argument(argument):
  #for replacing a single argument with a decomposed set which preserving connections. 
  pass

#x is overweight 
#being overweight causes heart attacks

#x had a heart attack
#therefore x had a heart attacke because they are overweight.



def evaluate_truth_of_statement(statement):
  #function that takes a statement and adds external justification to it, where external is external to the DB.
  def find_citations(statement):
    #find external justification based on cited sources. 
    pass
  def find_experiences(statement):
    #find external justification based on personal experiences.
    pass
  pass

axiomiticity/atomicity as a dimension