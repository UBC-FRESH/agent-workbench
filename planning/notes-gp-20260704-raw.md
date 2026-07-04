# Raw Delegation Economics Note

This note preserves the developer's original framing for the post-P30
Agent Workbench planning pivot. It is intentionally raw and lightly formatted
only as Markdown so the original signal is not lost.

---

I think you are thinking too narrowly. Think more broadly in terms of me
deploying this to do actual work on actual projects. We have proven that the
basic task-delegation system works and can be used to get one of several
available self-hosted open LLM models to "do a think". The real goal though is
for me to stop hemorrhaging cash in pay-as-you-go OpenAI GPT Codex API tokens.
If the supervisor agent costs me more in "task delegation overhead and
supervision" tokens than it would have if I had asked the supervisor to do the
task directly with no locally hosted open-model delegation, then we are not
winning. I want to win this game.

Typically, this type of Goldilocks game has a non-linear objective function
solution-space shape, and depending on how we frame it will have more than two
dimensions. If you delegate tasks whose size tends to zero, you are paying too
much in overhead. If you delegate everything, you are no longer supervising.
Closer to the sweet spot, but still in the losing part of the solution space,
you are either paying more in overhead cost than any benefit you get, or if you
delegate chunks that are too big or too hard for the subordinate agent you end
up paying more to mop up the mess it makes. That can happen if you let it make
changes and for some reason do not just reject them and do a git rollback to the
last-known-good checkpoint, or if you detect that the delegate agent broke
something several delegated tasks later and it is easier to patch things up than
to do a full rollback and redo yourself. Or maybe you bail out on delegation
after too many subordinate-agent failures and just do the task yourself, but now
it costs much more than if you had just done it yourself at the start.

The decisions the supervisor needs to make, on average, are:

- Correctly identify which types of tasks are good candidates for subordinate
  agent delegation, for each available subordinate model. Each model is good at
  different types, ranges, and scopes of things.
- Identify task-bundle plus delegate-model pairs that are good candidates for
  delegation in a given project. The currently open part of the planned
  development roadmap defines the task-bundle dimension of the solution space.
  In UBC-FRESH dev projects that means phase, task, and subtask.
- Estimate the likely net benefit of a hypothetical task-bundle plus
  delegate-model decision if activated. That means saving the cost of the
  tokens required to do the delegated job, minus supervision token cost, minus a
  mess-mop-up cost term. That cleanup term can be treated as a Bayesian product
  of the magnitude of the mess you might need to mop up if the delegate model
  fails and the probability of delegate-agent failure.
- Recognize that the same task bundle can be planned and communicated better or
  worse as a ticket or bundle of tickets. The supervisor has agency over the
  local shape of the delegation solution space, even though the larger project
  roadmap is developer-defined.

We need to plan at a level that converges on evidence for whether it is possible
to win this game. We do not need to demonstrate global delegation-policy
optimality immediately. We need a solid argument that Agent Workbench can
consistently achieve a non-trivial positive net benefit.

If we can do this, I can immediately deploy it in practice across UBC-FRESH dev
projects and collect more empirical performance data. That data can feed back
into the system to tune parameters. We could eventually implement one or more
hyperparameter tuning engines inside the package if that consistently boosts
average benefit. Later, if enough data exists, we could consider replacing
hand-tuned policies with an ML inference engine trained on real development
workflow delegation data so we get quasi-realtime parameter optimization.

Structurally, this resembles the problem of converting single-threaded code
into a parallel equivalent without paying more for parallelization overhead than
the parallel speedup gained. The delegation problem is more complicated because
it has more dimensions.
