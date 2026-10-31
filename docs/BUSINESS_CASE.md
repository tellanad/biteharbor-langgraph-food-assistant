# Business Case and Evaluation Plan

## Problem

Food-delivery support combines high-volume menu questions with sensitive order-status requests.
Manual handling adds wait time, while a free-form chatbot can invent catalog facts or disclose an
order to the wrong customer. BiteHarbor separates conversational reasoning from deterministic
catalog and authorization controls.

## Intended business outcomes

These are evaluation targets, not measured claims:

| Outcome | Metric | Initial acceptance target |
|---|---|---:|
| Faster self-service | Median time to a grounded answer | Under 15 seconds |
| Reduced support load | Eligible conversations resolved without an agent | At least 50% |
| Accurate menu discovery | Constraint-satisfaction rate on evaluation set | At least 95% |
| Safe order access | Cross-customer disclosure rate | 0% |
| Controlled cost | Model calls and tokens per resolved conversation | Establish baseline, then reduce 20% |

## Measurement design

Create a versioned evaluation set covering greetings, dietary combinations, price boundaries,
unavailable items, malformed identifiers, mixed intents, prompt injection, and cross-customer order
attempts. Record route accuracy, tool selection, groundedness, latency, token use, interrupt
completion, and escalation. Compare the assistant with the existing support flow through a staged
pilot. Publish observed results only after sample size, time window, and measurement method are
documented.

## Business risks

Dietary tags are informational and cannot guarantee allergy safety. Order data requires real caller
authentication in production. Automated replies need escalation paths for refunds, changes,
complaints, emergencies, and low-confidence answers. Retention, deletion, and regional privacy
requirements must be defined before customer data replaces the synthetic fixtures.
