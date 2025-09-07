---
description: Create a semantic git commit with proper formatting
---

Analyze the current git status and staged changes, then create a semantic git commit following these rules:

1. Use conventional commit format: `type(scope): description`
2. Common types: feat, fix, docs, refactor, test, chore, style
3. Keep description under 50 characters
4. Add detailed body if needed
5. Include the footer: 🤖 Generated with [Claude Code](https://claude.ai/code)

Before committing:
- Show git status
- Show git diff --staged 
- Explain what changes will be committed
- Create appropriate commit message
- Execute the commit

Arguments: $ARGUMENTS (optional commit message override)