# Experiment Design

The purpose of this study is to answer the research question:

*Under what conditions does the competition of Pdn and GbPdn interfere with the anti-inflammatory effect of Pdn?*

It is impossible to give a complete answer to this question.
Not only is the question rather difficult
(or even impossible, since it requires missing empirical data),
but a complete answer would probably fill books.

The implemented Petri-Net provides a very crude approximation
of the system, but it has many unknown parameters.
One can estimate whether competition occurred by measuring
the amount of neutrophils recruited after a given amount of time
(not too far in the future, the model only models
the first few hours after a wound was made).

To simplify things, one can use the context of the problem: drug design.
It would seem safe to
assume that the most interesting conditions are the parameters
that can be influenced when administered a drug.

## Tokens as percentages
All values are relative and unit-less.
Tokens represent an amount relative to the starting
value of the molecules/neutrophils represented by a certain place.
So one can set 1000 tokens initially in a place,
and interpret 1 token as 0.1% of the initial amount
of the elements. 
To scale the strength and absolute differences
between 


## Main variables of interest
The following parameters should be the independent
variables in the experiments, whose influence
on simulation outcomes is to be plotted/reported.
1. **$x_1$: Initial concentration of GbPdn**
    This variable can be directly influenced by changing
    the medicine dose. Maybe a too-high dose
    would cause sufficient binding of GbPdn with
    Gr to prevent Pdn from activating Gr.
    Also, a too low dose would not produce sufficient
    Pdn to recruit sufficient Gr to inhibit the
    inflammation in time, even when abundant Gr is available.
2. **$x_2$: The strength of Gba2**
    The conversion speed of GbPdn to Pdn by Gba2
    is unknown. However, if this parameter is important,
    then experimental biologists may be interesting
    in determining it experimentally in a wet-lab.
3. **$x_3 \& x_4$: Unbind rates of GrPdn and GrGbPdn**
    If GrGbPdn falls apart into Gr and GbPdn
    very quickly, but GrPdn much slower,
    then the interference would probably be negligible,
    regardless of the other variables.
    Hence these variables are important.
    Initial experiments can start with both set to 0,
    but it would be interesting to make a plot
    with the unbind rates on the horizontal and vertical axis,
    and a heatmap of the inhibitory effect.

## Other parameters of interest
Technically, these are also unknown, and some can
only be treated as variables.
However, in order to keep the search space
of the experiments feasible, only a few values
for the following will be tried;
not to quantify their importance accurately,
but mostly to see if it is relevant.

* **Natural decay of Pdn and GbPdn**
    Although certainly not sure, these effects
    are probably not every significant in the time-span of
    a few hours.
    These decay rates can be set to 0 during the first
    round of experiments. If time allows,
    they can be added to later experiments.
* **Decay of Gba2 by Gr\***
    Also the biological significance of this effect seems
    worth doubting. But it should certainly be investigated
    at which decay rate it would be significant.
* **Neutrophil attraction**
    Does the amount of recruited neutrophils reduce
    the rate at which new neutrophils are attracted?
    The model can support both.
    It is probably best to start with the simplest model,
    in which only the amount of free neutrophils
    and the amount of inflammation-signals influences
    the neutrophil-attraction rate.



## Eliminable parameters
* **Gr initial concentration**
    It would seem useful to specify the amount of Pdn
    administered as relative to the initial amount
    of free Gr.
    So if we set the initial $[Gr] = x_1 \in \N$,
    then we can specify the amount of Pdn as $\cdot x$
    for some $n \in \N$.
    Then we can set $x := 1000$, and report $n$ in the plots.
    This is -- hopefully -- easier to interpret.
* **Initial concentration Gba2**
    The model has both a parameter for the rate-constant $c_1$
    and the initial amount of Gba2 $[Gba2]$. 
    However, since all numbers are relative and unit-less,
    and in combination with the mass-action model,
    these two parameters can be seen as one parameter.
    This changes when the decay of Gba2 is considered,
    as $[Gba2]$ would start to change over time, while $c_1$ not.
* **Repression strength Gr\* on inflammation signals**
    The rate constant at which Gr* reduces the inflammation
    signals is an important parameter.
    However, it seems safe to assume that a cell has sufficient
    Gr-enzymes to provoke a strong inhibition when all activated,
    given that this is the purpose of Gr.
    Since we specify Gr unit-less as a relative amount,
    **this value should be tuned such that a very**
    **strong repression occurs when the initial amount of Gr\***
    **is 100% the amount of any form of Gr.**
    Simply set the initial tokens to $[Gr*] = 1000$, $[Gr] = 0$
    $[Pdn] = [GbPdn] = 0$.
    Hence tuning be done experimentally; 
    one less parameter to guess!
* **Initial concentrations**
    One can start with 1000 tokens
    for the initial concentrations of:
    * Free neutrophils
    * Inflammation signals
    * Gba2
    * Gr

## Baseline for inhibitory effect
The dependent variable is the inhibitory effect
of Pdn on the inflammation, measured in amount
of neutrophils attracted.
To measure whether or not inhibition occurs,
one can first run an experiment with $[Pdn] = [GbPdn] = 0$,
and measure the amount of simulated time $t$
until the amount of recruited neutrophils is 80%
(on average over many runs).
Then for the actual experiments, with Pdn/GbPdn present,
one can measure the amount of recruited neutrophils
at time $t$ (approximately, e.g., in the same time-box).
If this value is significantly smaller than 80%,
then we can conclude that inhibition occurred.
Note that the distribution of recruited neutrophils
after a fixes amount of time $t$ appeared normal,
from the pre-study of the distribution of neutrophils,
so a t-test can be used for **statistical** significance. 
However, with many runs
79% may be statistically different, 
but is not of **biological** significance!
**Both types of significance should be taken into account.**
(The statistical one to ensure it is not a result
by chance, and the biological one to see if there
actually was a medically useful amount of suppression.)


# Experiment Planning

0. Normality of the distribution of Neutrophils 
    (already completed before writing this planning).
1. Tuning of the Gr*-inflammation signals repression rate.
2. Measure different combinations of $x_1$ and $x_2$ for
    $x_3 = x_4 = 0$. Create a plot.
3. Repeat experiment 2. for different values of $(x_3, x_4)$.
    This will be a large grid-search, so reduce the amount
    of values for $x_1$ and $x_2$ to try.
    Create a table.
4. Fix $(x_1, x_2)$ and make a plot for the effects of $(x_3, x_4)$.
5. Perform an experiment in which Gba2 decays.
6. [if time] run an experiment Pdn/GbPdn decays, 
    or with a different neutrophil-attraction-rate-function.
