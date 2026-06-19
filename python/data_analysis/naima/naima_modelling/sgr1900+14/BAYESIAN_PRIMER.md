# Bayesian statistics in a nutshell — a gentle primer

*Read this once before the fitting notebooks. It assumes **no** prior knowledge.
Every new word is explained the first time it appears, in plain language, and
again in a glossary at the end. Take it slowly — the ideas are simple once the
words stop getting in the way.*

---

## 0. What are we even trying to do?

We have some **measurements** of a gamma-ray source (how many photons arrive at
each energy). We have a **physical model** — a recipe that predicts those photon
numbers *if* we tell it a few unknown quantities, like "how steep is the particle
spectrum?" and "how much total energy is in the particles?".

Fitting means: **find the values of those unknown quantities that make the model's
prediction match the measurements** — and, just as importantly, **say how sure we
are** about each value.

Two words we'll use constantly:

- **Model** — the recipe (here: the physics of how protons or electrons make
  gamma rays). Think of it as a machine with a few **dials** on the front.
- **Parameters** — those dials. Turning a dial (e.g. the spectral steepness)
  changes the prediction. *Our whole job is to figure out where the dials should
  be set.* We'll write the full set of dial settings as **θ** — it's just shorthand for "one particular choice of all the dials."
- **Data** — the actual measurements we're trying to explain.

Bayesian statistics is simply **a principled way to use the data to figure out the
dials, and to be honest about the leftover uncertainty.**

---

## 1. The single most important idea

There are three quantities. Learn these three words and you understand 90% of it.

- **Prior** — what you believe about the dials *before* looking at the data.
  (Your starting hunch. Example: "the steepness is probably somewhere between 2
  and 3, and definitely positive.")
- **Likelihood** — for a *given* setting of the dials, **how well does the model's
  prediction match the data?** A high likelihood means "this dial setting explains
  the measurements well"; a low likelihood means "this setting predicts something
  far from what we saw."
- **Posterior** — what you believe about the dials *after* combining your prior
  hunch with the evidence from the data. **This is the answer we want.**

The rule that ties them together is **Bayes' theorem**. In words:

> **posterior  =  prior  ×  likelihood**  (and then rescale so it adds up to 1)

That's it. Your updated belief is your starting belief multiplied by how well each
possibility fits the data. Written with symbols (don't be scared, it says exactly
the sentence above):

$$
\underbrace{P(\theta \mid D)}_{\text{posterior}}
\;\;\propto\;\;
\underbrace{P(\theta)}_{\text{prior}}
\;\times\;
\underbrace{P(D \mid \theta)}_{\text{likelihood}}
$$

- `P(θ | D)` reads "the probability of the dials θ, **given** the data D" — the
  posterior.
- `P(θ)` is the prior — "the probability of θ before seeing data."
- `P(D | θ)` is the likelihood — "the probability of seeing this data **if** the
  dials were θ."
- The `∝` symbol means "is proportional to" — i.e. equal up to an overall scaling
  factor that we don't need to worry about for fitting.

**The key mindset shift:** the answer is **not a single number** for each dial. It
is a whole *range of believability* — a curve showing which values are very
likely, which are possible, and which are ruled out. The **width** of that curve
is your error bar. We'll make this concrete next.

---

## 2. A worked example you can follow with a pen

Forget gamma rays for a minute. **Is a coin fair?**

- The **dial** (our only parameter) is `p` = the coin's probability of landing
  heads. It's a number between 0 (never heads) and 1 (always heads). A fair coin
  has `p = 0.5`.
- The **data**: we flip the coin **10 times and get 7 heads, 3 tails.**

Now apply the three ingredients.

**Prior** (belief before flipping). Suppose we know nothing about this coin. Then
every value of `p` between 0 and 1 is equally believable. That's called a **flat**
(or **uniform**) prior — it has no opinion, it just says "p is somewhere in
[0, 1]."

**Likelihood** (how well does each `p` explain "7 heads in 10 flips"?). Basic
probability says the chance of that exact result, for a given `p`, is proportional
to

$$ p^{7}\,(1-p)^{3} \quad(\text{seven heads} \times \text{three tails}). $$

Try a few values by hand to feel it:
- `p = 0.1`: 0.1⁷ × 0.9³ ≈ tiny — a coin that almost never lands heads is a *terrible* explanation for 7 heads.
- `p = 0.7`: 0.7⁷ × 0.3³ — this is the **largest** value. A coin with `p = 0.7` explains "7 of 10 heads" best, which makes intuitive sense (7/10 = 0.7).
- `p = 0.95`: small again — a near-always-heads coin should have given more than 7.

**Posterior** = prior × likelihood = `1 × p⁷(1−p)³`. If we draw that curve from
`p = 0` to `p = 1`, we get a **bump** that:
- is **zero** at `p = 0` and `p = 1` (those extremes are impossible given the data),
- **peaks at `p = 0.7`** (the best single guess), and
- is **broad** — values from roughly 0.45 to 0.9 still have decent height.

That breadth is the honest message: **with only 10 flips we genuinely don't know
`p` precisely.** The best guess is 0.7, but anything from ~0.45 to ~0.9 is
plausible. That spread **is** the uncertainty — we didn't have to invent an error
bar, the posterior handed it to us.

### Two lessons from the coin

1. **More data → a narrower posterior (less uncertainty).** If instead we flipped
   **1000** times and got **700** heads, the peak would still sit at 0.7 but the
   bump would be *much* narrower — now we'd be confident `p` is near 0.70.

2. **The prior matters when data is scarce, and fades when data is plentiful.**
   Suppose we had a reason to believe the coin is *probably fair* and encoded that
   as a prior peaked at 0.5. With only 10 flips, the posterior would land
   *between* the prior (0.5) and the data (0.7) — a tug-of-war. With 10 000 flips,
   the data would completely overwhelm that prior. **The posterior is always a
   compromise between what you believed and what the data say, weighted by how
   strong each one is.**

> In our gamma-ray fits we use **flat priors inside physical limits** — e.g.
> "the spectral steepness is somewhere in [1.5, 3.5]" and "a density can't be
> negative." A flat prior adds no opinion except those hard walls, so the data do
> the talking, while impossible values stay forbidden.

---

## 3. The answer is a *distribution*, so here's how we summarise it

The posterior is a curve (a **distribution** — a function that says how believable
each value is). We usually report two things from it:

- **The best estimate** — the **median**: the value with half the believability
  below it and half above. (Often close to the peak.)
- **The uncertainty** — a **credible interval**: a range that contains, say, 68%
  of the believability. We get it from **percentiles**:
  - the **16th percentile** is the value below which 16% of the believability lies,
  - the **84th percentile** is the value below which 84% lies,
  - the gap from the 16th to the 84th percentile holds the middle **68%** — this is
    the Bayesian version of a "**1-sigma** (1σ) error bar."

So when a fit reports `Γ = 2.45 (+0.12 / −0.08)`, it means: *the best estimate of
the steepness is 2.45, and there's a 68% chance the true value is between 2.37 and
2.57.* That entire statement comes straight from reading percentiles off the
posterior curve.

---

## 4. Bayesian vs. "the other kind" (optional, one paragraph)

You may hear that there are two schools of statistics. The **frequentist** school
asks "*if* the true value were θ, how often would random data look as extreme as
mine?" — it treats the unknown as fixed and the data as random, and gives you
*p-values* and *confidence intervals*. The **Bayesian** school (what naima uses)
asks the more direct question "*given the data I actually have, what's the
probability of each θ?*" — and answers with the posterior distribution. The
practical upshot: a Bayesian "credible interval" is a genuine probability
statement about the parameter, which is usually what we actually want to say.

---

## 5. Why we can't just write the answer down — enter MCMC

For the coin (one dial) we could draw the posterior directly. But our gamma-ray
models have **3–5 dials at once**, and the likelihood involves a slow physics
calculation. The posterior is then a bumpy *landscape* in several dimensions that
**we cannot compute or draw directly.**

The trick: instead of computing the whole landscape, we **sample** it — we collect
thousands of example dial-settings θ, drawn **in proportion to how believable they
are.** Believable settings get picked often; poor ones rarely. The resulting pile
of samples *is* a stand-in for the posterior: histogram them and the shape
reappears; take percentiles of them and you get your best value and error bars.

The algorithm that produces such samples is **MCMC** — *Markov-Chain Monte Carlo*.
You don't need the name's etymology; you need the picture:

- Imagine a **landscape** where altitude = believability (high ground = good dial
  settings that fit the data; valleys = bad ones).
- Release a group of **walkers** (also called the *ensemble*) — little explorers
  that wander this landscape. Each step, a walker tends to move toward higher
  ground but sometimes wanders downhill, so the whole group ends up **spending
  most of its time on the high ground**, in proportion to the altitude.
- The recorded trail of everywhere the walkers went is called the **chain** — that
  trail *is* our collection of posterior samples.

Two practical terms you'll see:

- **Burn-in** — the walkers start at random, possibly silly, locations and need a
  while to *find* the high ground. Those first wandering steps don't represent the
  posterior, so we **throw them away**. That discarded warm-up is the burn-in.
- **Convergence** — after burn-in, a healthy run looks **settled**: the walkers
  mill around the same region instead of still drifting somewhere. We *check* this
  (see the chain plots in the notebooks) before trusting the result. If the chain
  is still drifting, we haven't run long enough.

A couple of dials you set:

- **`nwalkers`** — how many explorers (more = better coverage, slower).
- **`nburn`** — how many warm-up steps to discard.
- **`nrun`** — how many "good" steps to keep as the actual samples.
- **`prefit`** — an optional quick search for the high ground *first*, so the
  walkers start near it instead of wandering in from nowhere.

---

## 6. How all of this maps onto a naima fit

Everything above appears, one-to-one, in the fitting notebooks:

| Idea in this primer | In the gamma-ray fit |
|---------------------|----------------------|
| the dials **θ** (parameters) | the particle-spectrum numbers: normalisation `N0`, steepness `Γ`, cutoff energy `E_cut`, … |
| the **data** | the measured flux points (with their error bars and upper limits) |
| the **likelihood** (how well a setting fits) | computed from **χ²** ("chi-squared") — see below |
| the **prior** (allowed values) | `naima.uniform_prior(...)` — flat inside sensible limits, forbidden outside |
| the **posterior** (the answer) | what `naima.run_sampler` explores with the MCMC walkers |
| **best estimate** | the posterior **median** |
| **uncertainty** | the **16th–84th percentile** range |

### What is χ² (chi-squared)?

For each data point we have a measured flux and an error bar (σ, "sigma" — the
size of the uncertainty on that point). For a trial dial-setting, the model
predicts a flux. The **mismatch** of one point is

$$ \left(\frac{\text{model} - \text{measured}}{\sigma}\right)^2 $$

i.e. *how many error bars apart* the prediction and the measurement are, squared.
**χ² is just the sum of that mismatch over all the points.** A small χ² means the
model threads through the data nicely; a big χ² means it misses.

The bridge to everything above: when the measurement errors are bell-curve
("Gaussian") shaped, the **likelihood is simply `exp(−χ²/2)`**. So:

> **the best-fitting dials = the highest likelihood = the smallest χ².**

"Best fit" and "lowest χ²" and "peak of the posterior" are three names for the
same point. The *width* of the posterior around that point is the uncertainty.

We also report **χ²/ndf**, where **ndf** ("number of degrees of freedom") =
(number of data points) − (number of dials you fitted). A value near **1** means
the model fits about as well as the error bars allow. Much bigger than 1 → the
model misses the data; much smaller than 1 → the error bars were probably
overestimated.

### The corner plot (the posterior, made visible)

With several dials, the posterior lives in several dimensions and can't be drawn in
one picture. A **corner plot** shows it as all its 1-D and 2-D "shadows":

- **On the diagonal:** one bump per dial — exactly the kind of posterior curve from
  the coin example, now one for each parameter. Its centre is the best value, its
  width is the error bar.
- **Off the diagonal:** one panel per *pair* of dials, showing whether they are
  linked. A round blob = the two are independent. A **tilted, stretched "banana"**
  = a **degeneracy**: the data only pin down a *combination* of the two, not each
  separately. (In the hadronic fit you'll see this between the normalisation `N0`
  and the gas density `n_H` — the data fix only their product.)

So a corner plot lets you (1) read each value and its error from the diagonal, and
(2) spot any degeneracies from the off-diagonal shapes.

---

## 7. Run the coin example yourself (≈10 lines)

This reproduces Section 2 on a grid of values — no MCMC needed, just
prior × likelihood, exactly as described:

```python
import numpy as np, matplotlib.pyplot as plt

p = np.linspace(0, 1, 500)          # every candidate value of the bias p
prior      = np.ones_like(p)        # flat prior: no opinion
likelihood = p**7 * (1 - p)**3      # our data: 7 heads, 3 tails
posterior  = prior * likelihood     # Bayes' theorem (before rescaling)
posterior /= np.trapz(posterior, p) # rescale so the area under the curve = 1

plt.plot(p, posterior)
plt.axvline(0.7, ls=':', color='k', label='best guess = observed fraction 0.7')
plt.xlabel('p  (probability of heads)'); plt.ylabel('believability (posterior)')
plt.legend(); plt.show()

# best estimate + a 68% credible interval, read straight off the curve:
cdf = np.cumsum(posterior); cdf /= cdf[-1]
lo, med, hi = np.interp([0.16, 0.50, 0.84], cdf, p)
print(f'p = {med:.2f}  (+{hi-med:.2f} / -{med-lo:.2f})')
```

You'll see a broad bump peaking at 0.7 with a 68% interval of roughly 0.55–0.82.
**That is a Bayesian fit.** naima does the very same thing, only with several dials,
a gamma-ray physics model in place of `p⁷(1−p)³`, and MCMC instead of a grid
(because in many dimensions a grid would be astronomically large).

---

## 8. Glossary (one line each)

- **Model** — the recipe that turns dial settings into a prediction.
- **Parameter / dial (θ)** — an unknown number the fit adjusts (e.g. spectral steepness).
- **Data** — the measurements we want to explain.
- **Prior** — your belief about the dials *before* seeing the data.
- **Likelihood** — how well a given dial setting reproduces the data (high = good fit).
- **Posterior** — your belief about the dials *after* combining prior and data; **the answer**.
- **Bayes' theorem** — posterior ∝ prior × likelihood.
- **Flat / uniform prior** — a prior with no preference except hard limits.
- **Distribution** — a curve saying how believable each value is.
- **Median** — the middle value; our best single estimate.
- **Percentile** — the value below which a given fraction of believability lies (16th, 50th, 84th, …).
- **Credible interval** — a range holding a stated share (e.g. 68%) of the believability; the error bar.
- **σ (sigma)** — the size of an uncertainty; "1σ" ≈ the 68% interval.
- **χ² (chi-squared)** — summed, squared, error-bar-scaled mismatch between model and data.
- **ndf** — data points minus fitted dials; χ²/ndf ≈ 1 means a good fit.
- **MCMC** — the algorithm that draws posterior samples by random-walking the believability landscape.
- **Walker / ensemble** — the individual explorers / the group of them.
- **Chain** — the recorded trail of samples the walkers produced.
- **Burn-in** — the early, unsettled steps that we discard.
- **Convergence** — the run has settled and can be trusted.
- **Corner plot** — a picture of the multi-dimensional posterior as its 1-D and 2-D shadows.
- **Degeneracy** — when the data constrain only a *combination* of dials, not each alone (a tilted blob in the corner plot).

---

## Further reading
- D. Hogg & D. Foreman-Mackey, *Data analysis recipes: Using MCMC*, arXiv:1710.06068 — friendly and practical.
- Foreman-Mackey et al. 2013, *emcee*, PASP 125, 306 — the sampler naima uses.
- J. VanderPlas, *Frequentism and Bayesianism* blog series — clear on the distinction.
