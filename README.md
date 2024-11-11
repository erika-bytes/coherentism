# Overview

This is a tool to graphically decompose a given proposition into a "fact tree" based on the philosophical truth-model of coherentism.

# Premise: Coherentism

As defined in the Stanford Plato Dictionary of Philosophy, Coherentism is a truth model wherein "a proposition coheres with a set of propositions if and only if it is entailed by members of the set."

As an example, we may consider the proposition: "human activities contribute to climate change."

In order to evaluate the truth of this proposition in adherence with the model, we first need to construct a 'sufficient' set of facts which justify it. The related set of facts for the above proposition, for example, may be as follows:

Human activities contribute to the release of greenhouse gases.
The greenhouse effect traps heat in the earth's atmosphere.
Global temperatures are increasing.
The rise of global temperatures is correlated with industrial activity.

Then, in order for us to consider our proposition justified, the individual relationships between each of these facts and our proposition must hold true.  

## Implementation: Argument

We have taken an instance this truth-model, call it an Argument, and constructured it programmatically as follows:

### Prolog

#### Facts (Premises)
fact_one.
fact_two.
fact_three.
fact_four.
fact_five.
...

#### Rules (Relationships between beliefs)
supports(proposition, fact_one).
supports(proposition, fact_two).
supports(proposition, fact_three).
supports(proposition, fact_four).
supports(proposition, fact_five).
...

#### Justified Belief (Conclusion)
justified_belief(proposition) :-
    fact_one,
    fact_two,
    fact_three,
    fact_four,
    fact_five,
    ...,
    supports(proposition, fact_one),
    supports(proposition, fact_two),
    supports(proposition, fact_three),
    supports(proposition, fact_four),
    supports(proposition, fact_five),
    ... .

### JSON

{
  "supporting_statements": [
    {
      "statement": 
      ...
    },
    ...
  ],
  "supporting_rules": [
    {
      "supporting_statement": {
        "statement": 
        ...
      },
      "supported_statement": {
        "statement": 
        ...
      }
    },
    ...
  ],
  "conclusion": { 
    "statement": 
    ...
  }
}

## Decomposition Process

Having constructed one Argument for a given proposition, we could easily imagine the construction of new arguments for every fact which supports that proposition, and so on, creating a "fact tree". 

Such a structure would allow us to visually observe the decomposition of a proposition and consider its credence increasing levels of atomicity, somewhat akin to a curious kid repeatedly asking "why?"

We implement this, invoking a large language model to generate Arguments at N levels of depth for a user-defined proposition.
