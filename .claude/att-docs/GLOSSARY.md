# Overmind

A shared base of skills, hooks, and scripts that agents use to work a repository's issues unattended and to keep its documents and tests current.

## Language

### Work selection

**Cleared**:
An issue that carries the `ready-for-agent` label, so an unattended session may take it up. An issue that is not cleared is never served.
_Avoid_: Ready, approved

**Blocked**:
The `Blocked` label on an issue that waits on something it cannot get for itself, such as another issue or pull request, a person, or a service. It is set and removed by hand or by the implement skill, and a labeled issue is never served.
_Avoid_: Blocker

**Blocker**:
An open issue that GitHub's issue dependencies list as blocking another issue. The blocked issue is not served until every one of its blockers is closed.
_Avoid_: Dependency, blocked issue

### Review

**Ready for review**:
A pull request whose self review is clean and whose checks have all passed, marked by the `Manual Review Needed` label, so it waits on the user.
_Avoid_: Ready, done

### Test packs

**Output budget**:
The most tokens one model call in a test pack build may produce, its thinking and its answer together. A call that reaches it is cut off and its answer is lost.
_Avoid_: Thinking limit, reasoning output, cap

**Thinking budget**:
The most tokens a model call may spend thinking before it is made to write its answer. Smaller than the output budget, so the answer always has room.
_Avoid_: Reasoning limit, thinking cap

**Draft workbook**:
The test pack workbook as it stands before the quality review, with the review's sheets marked Pending review and its confidence shown as Low until the review rates it. Phase 8 ends by writing it, and Phase 9 writes it again from the current pack before each review call.
_Avoid_: Review workbook, draft pack

**Confidence ceiling**:
The highest overall confidence the workbook builder accepts for a pack, set by what the pack leaves open.
_Avoid_: Confidence limit, confidence cap

**Build supervisor**:
A session that watches a running test pack build and answers the questions the build would otherwise stop on, from the documents, the build's inputs, the approved rules and the issue's own record only. It writes the answers file and nothing else.
_Avoid_: Reviewer, operator

**Model gate**:
The rule that the local model runs only on the user's yes, asked for each run.
_Avoid_: Approval, permission check
