# Contributing to Orbit

## Workflow: GitHub flow

`main` is always working and deployable. All changes reach it through pull requests.

1. **Create a branch** from the latest `main`, named after the change:
   - `feature/google-oauth`
   - `fix/briefing-timezone`
   - `chore/update-dependencies`
   - `docs/setup-guide`
2. **Make small, focused commits.** Write messages in the imperative mood, e.g. `Add Gmail sync task`.
3. **Open a pull request** early and fill in the template. Draft pull requests are welcome.
4. **Make CI pass.** Lint, formatting, type checks, tests, and the Docker build must all be green.
5. **Review, then squash and merge.** Delete the branch afterwards.

Never push directly to `main`.

## Code principles

- **Simple over clever.** Prefer clear, conventional code that anyone can follow. If a "smart" solution needs a comment to explain how it works, look for a simpler one.
- **Organised.** Put code where the project structure says it goes (see the README). One responsibility per module.
- **Readable names.** Name things after what they mean in the product, not how they are implemented.
- **Comments explain why, not what.** The code should say what it does.
- **Tested.** New behaviour comes with tests. Bug fixes come with a test that would have caught the bug.

## Security

- Never commit secrets, tokens, or real personal data, including in tests and fixtures.
- Read configuration from environment variables through `backend/app/config.py`.
- Validate all input at the API boundary with Pydantic models.
- Treat email content, calendar data, and news as untrusted, especially when passing it to an LLM.
- Request the narrowest OAuth scopes a feature needs.

## User experience

- Every view handles its loading, empty, and error states.
- Check UI changes on mobile and desktop, in light and dark mode.
- Use semantic HTML and make everything work with the keyboard.
- Write UI text that is short, plain, and tells people what to do next.
