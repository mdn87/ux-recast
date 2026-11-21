# Impeccable passes in a bounded review

On Windows with Python 3.14.3, the public ux-recast CLI completed two contact
form reviews using rubric 2. Each review recorded two findings, used one
dispatch and one repair batch, and passed all seven browser checks.

Matt accepted the bounded review as completion of S4.4 on 2026-11-21.
The separate pilot installation decision remains open. Dias continues to use
built-in guidance with its current project setup.

| Project setup | Review handoff | Granted repair | Optional detector |
| --- | --- | --- | --- |
| Project-local Impeccable 4.8.0 | Issued `$impeccable critique` and recorded the Codex skill manifest and version | Issued `$impeccable adapt`, `$impeccable harden` and `$impeccable polish` | The real engine returned exit 2 and the rule `kicker-above-heading` at `div.eyebrow` |
| Built-in review guidance | Supplied the four review questions | The parent received the ordinary repair grant | The packet recorded `unavailable` and the review finished |

The local agent used the review packet and the captured form state. At 375 CSS
pixels the page fitted the viewport. Submitting an invalid email cleared the
name and request and left focus on Send request. Those observations supported
both findings. The detector's eyebrow rule stayed evidence only. The parent
replayed the fixture's tracked repair in each scratch project. Keyboard recovery
preserved the draft, focused the email field, and allowed submission after
correcting just that field. A repeated repair request was refused in both runs.
[Fixture and browser checks](../../fixtures/contact-request/test_flow.py)

This exercises the handoff to the local agent. Upstream's full web critique
asks for two isolated assessments, persistent output and an operator follow-up.
The local reviewer used the bounded guidance. The recorded commands show what
the agent received. The browser results measure the fixture's known repair.
[Upstream critique reference](https://github.com/pbakaus/impeccable/blob/e89e3ada3e87/skill/reference/critique.md)

The installed-mode fixture used the Codex skill directory from the official
`skill-v4.8.0` release in an ignored scratch project. Its archive SHA-256 was
`82e6f6ff3a2b18f46f0f2fc388c1ab7abf3ccc52bbfc522456396d13011d6706`.
Only that skill directory was extracted. The package uses the installed
references at runtime. The separate npm 4.8.0 detector used engine 0.1.18
and Chromium 149.0.7827.55. All five detector checks passed. With the real npm
launcher alone and an empty cache, the helper returned `unavailable` with
exit 127, made zero requests to the configured release server and left the
cache absent. [Skill release](https://github.com/pbakaus/impeccable/releases/tag/skill-v4.8.0)
and [detector provenance](impeccable-real-detector-2026-11-16/README.md)

An open review prepared and claimed by the released dev3 package retained its
exact task bytes and could be recorded and consumed by the new code. All eight
CLI regression scenarios retain their Phase 3 outcomes. Six have new review
text and metadata in the prepared request, claim output and saved packet.
The Phase 3 comparison file remains available for the released Lugos shim.
[Packet tests](../../tests/test_review_modes.py) and [CLI regression tests](../../tests/test_differential.py)
