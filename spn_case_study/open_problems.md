# Still open

## Delayed effects Gr*
In model Version 5, the effects of Gr* are directly caused
by the concentration Gr*. This prevents any momentum from building up.
However, literature tells that Gr* also triggers transcription
of anti-inflammatory genes, which could be a stable buildup
even when the concentration of Gr* heavily fluctuates!

## Cleavage
Gba2 catalyzes the reaction $GbPdn \rightarrow Pdn$.
But does this use Michealis-Menten or just 
the Mass-action Law?

# More or less resolved

## Interaction Gr* on Gba2
(**More or less resolved in version 4/5**)
Gr* inhibits Gba2, right now Gr* has an
inhibition arc to the Gba2 production.
However, I do not how describe the inhibition quantitatively.

The book *Modeling in Systems Biology - The Petri Net Approach* 
(ch8 by Jörg Ackermann and Ina Koch)
described the inhibition of enzymes as follows:
the inhibitor either binds to the enzyme or to
the enzyme-substrate complex. 
This requires additional places and transitions
(which can of course easily be added).

**Does the inhibition disable present Gba2,**
**or does it slow down the Gba2 production rate?**


## Neutrophil recruitment
(**More or less resolved in version 4/5**)
Does the quantity of recruited neutrophils
increase linearly, or decaying-exponentially?
Does the amount of previously-recruited neutrophils
influence the rate at which new neutrophils are recruited?