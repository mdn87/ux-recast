# Brief: <task name>

Stage 1 of the redesign method (`docs/plans/redesign-first.md`). Written from the code, the current screens, process documentation and known complaints. Every assumption is marked `[assumed]`; anything that would materially change the design and cannot be settled from available material is listed under Open questions, and only those are asked.

## The person and the situation

- **Who does this**: role, how often, how familiar with the task and with this application.
- **What brings them here**: the situation or trigger, and what they have in hand when they arrive.
- **The result they need**: in their words, and how they will know it is done.

## What they know and what the application knows

| Needed for the task | The person already has it | The application can infer, remember or calculate it | Must be asked |
| --- | --- | --- | --- |
| | | | |

Anything in the last column is a step the person must perform; everything else is a step the interface should absorb.

## Mandatory rules and dependencies

Rules the result must obey (business, data, order of operations) with the source for each (file and line, document, or person). Separate from these, habits of the current implementation that look like rules but are not.

## Anti-goals

What must remain untouched, and what would make the result feel wrong even if it looked polished.

## Capabilities recovered from the code

What the application can already do that the task needs, with file references. Note where a capability exists but is reached only through machinery the person should not have to understand.

## Open questions

Only the facts that would substantially change the design. Everything else is decided here and marked `[assumed]`.
