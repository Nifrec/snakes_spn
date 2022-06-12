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

## PetriNet v5
Version 4 included the ideas above,
but made the decay of Gba2 depend also on the concentration of Gba2,
and the inhibition of the Neutrophil attractors depend on their concentration.
However the inhibition of active Gr on both these places
seems (mostly) indirect by decreasing the production.
As a consequence, one would *not* expect a high concentration 
of Gba2/attractors to increase the rate of inhibition!
So in version 5, the rates of both inhibition transitions
only depend on the concentration of active Gr.

## PetriNet v6
This version made the decay of Gba2 and the inflammation signals
depend on their own concentrations again (and also still on Gr*).
Things decay faster when there is more of it.

It is an interesting question, though, whether
the concentration of Gr* and Gba2 are additive or multiplicative.
The SPN diagram now has:
$\frac{d[Gba2]}{dt} = -e^{x_2 \cdot [Gr^*] \cdot [Gba2]}$.
But perhaps it should be:
$\frac{d[Gba2]}{dt} = -e^{x_{2,1} \cdot [Gr^*] + x_{2,2}\cdot [Gba2]}$.
The latter is a bit problematic in the case
of the inflammation signals,
as repression would always occur
even when $[Gr^*] = 0$.
In the time scope that is being modelled,
this is not the case,
since we know that anti-inflammatory drugs
are needed and do have effect
(which would not be the case if
inflammations repressed themselves very quickly!).

Also, using 
$\frac{d[Infl.Sig.]}{dt} = -e^{c_1 \cdot [Gr^*]}$
and re-calibrating $c_1$ would
be equivalent to setting 
$c_1 = [Infl.Sig.]_0 \cdot c_{1, \mathit{old}}$.
This will, in no case, decrease the strength
of $Gr^*$'s repression, only increase it!

## Within and between cells
Some places of the Petri-Net (the concentrations Gba, Pdn, GbPdn,
Gr, etc.) refer to phenomena inside a cell,
while others (neutrophil attraction, inflammation signals)
are present on a higher abstraction level.
This is not problematic: all values are relative,
so one may consider the within-cell processes
to be the sum of many cells doing them in parallel.
The model would appear sufficiently crude and abstract
that there is no difference between modelling involved
inflamed cells as one big cell, 
or running many small cells in parallel.
For more accurate models this distinction would
probably be very relevant.