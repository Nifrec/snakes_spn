This file explains some of the decisions made in the modelling process.

## Gba2 reduction
It is known that the Gba2 concentration decreases
when active Gr inhibits the inflammation response.
However, it is not clear whether Gr binds to Gba2 directly,
whether Gr directly activates a signalling pathway inhibiting Gba2,
whether Gr causes the transcription of genes leading to Gba2 inhibitors,
or whether Gr inhibits the transcription of Gba2
(other mechanism are probably possible as well).
Quite possible multiple of these mechanism are at play,
and not all operating with the same strength.

Modelling these mechanism explicitly is problematic for the following reasons:
* It may introduce a significant bias in the model,
    for example when one well-known mechanism is included
    but an unknown or uncertain mechanism is left out.
* Each indirection adds more unknown parameters for the quantitative analysis,
    than cannot be estimated without data.
    Quite certainly there does not exist a quantitative dataset
    including all those mechanism for the same species (preferably zebrafish).
* The exact details of the Gba2 inhibition do not seem very important
    to answer the research question, in comparison with
    how time can be invested in other parts of the case study.
* According to the literature, not all mechanisms are clear.
    It is clear that active Gr inhibits transcription of pro-inflammatory genes,
    but it also uses less well-understood mechanisms
    such as transcription of anti-inflammatory genes.

It seems therefore justifiable, 
until better empirical insights become available,
to model the inhibition of Gba2 by active Gr directly.
This has a few advantages:
* It is the most parsimonic model given that my currently available
    knowledge of which I am certain is limited to:
    *t is known that the Gba2 concentration decreases*
    *when active Gr inhibits the inflammation response.*
* Less room for error. Adding more explicit mechanisms
    may result in a model not consistent with the above knowledge.
* Less unknown parameters. For the unknown parameters,
    the best we can do is to try many different values.
    The more parameters, the more combinations of possible
    values for them. This amount of combinations grows exponential,
    so it is important to limit the amount of parameters where possible.

## Neutrophil recruitment
Some facts from the literature:
1. Neutrophils are attracted only for a few hours, after which they
    undergo reverse migration or apoptosis.
2. Neutrophils are attracted by signalling molecules in inflamed cells,
    such as $H_2O_2$, Cxcl8a, Cxcl8b.1, etc.
From 1., it seems most practical to only model the first hours of
inflammation. Care should be taken not to run the model too long,
as in natural inflammation (without Gr inhibition) regulatory
processes (the 'resolution phase') will start.
This phase is not part of the model, since it is not a major interest
for the research questions.

I have not found any mentioning of anti-inflammatory signals that 
actively inform neutrophils *not* to become recruited.
For this reason, in combination with point 2,
it seems best for now to model neutrophil inhibition by Gr indirectly:
Gr reduces the attractors, and the concentration
of attractors determines the rate of neutrophil recruitment.
The exact types of attractors, with their different doses and
strengths, is not modelled: there is simply one place for '*attractors*'.
