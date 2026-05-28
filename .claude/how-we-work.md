# Skill for how we work together

## Feature or Bug work

When working on a new feature or bug, we will do these actions:
1. Create a new branch with descriptive name of the work being done, e.g. `feature/add-todo-reminders` or `bugfix/fix-datetime-parsing`
2. Make commits to the branch with descriptive messages about the changes made — one commit per logical unit of work, not WIP dumps
3. Run `venv/bin/pytest tests/ -v` before each commit; do not commit if tests are failing
4. Do not push up until human has reviewed the code and said something like "Looks good, you can push up now"
5. Before pushing, start both servers and smoke-test the critical paths end-to-end
6. Always make new commits, never amend or rebase commits that have been pushed up to the remote repository

## PR hygiene

- Close open PRs before opening new ones
- If there's a good reason to have multiple PRs open at once (e.g. the work is genuinely independent and separating it makes review cleaner), raise that option before creating a new branch — don't just open a new PR and let the queue grow