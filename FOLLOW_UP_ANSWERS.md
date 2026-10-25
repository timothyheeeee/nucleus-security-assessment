# Follow-up Answers

The following answers address the Code Review and Coding Challenge follow-up questions from the Nucleus Security Software Engineering Intern assessment.

I used **Cursor** as an AI-assisted development and review tool throughout the assessment. My focus was on understanding the requirements, evaluating technical decisions, identifying risks, and verifying that the proposed solutions addressed the intended problems.

Supporting documentation:

- `AI_USAGE.md` — AI usage, development workflow, and prompts
- `AI_PROMPT_TRANSCRIPT.md` — Recoverable AI prompts and outputs
- `CODE_REVIEW.md` — Detailed webhook code review
- `README.md` — Calculator setup, features, and testing instructions

---

# Part 1 — Code Review: Follow-up Questions

## 1. Share your prompts and the AI outputs.

I used Cursor throughout the assessment to support the webhook code review and calculator implementation. Instead of relying on a single AI-generated answer, I worked through several stages, refining the requirements, examining the output, identifying limitations, and addressing issues as they emerged.

My main AI interactions followed this sequence:

1. **Initial assessment and implementation:** Analyse the official assessment Gist, review the Python webhook implementation, and develop a lightweight Flask calculator with supporting tests and documentation.
2. **Independent technical audit:** Examine the implementation for actual defects, security vulnerabilities, edge cases, and functionality that might fail despite passing standard tests.
3. **Expression display and decimal rounding:** Extend the calculator to display complete expressions and support configurable decimal precision without compromising calculation accuracy.
4. **Parentheses support:** Introduce parentheses and correct operator precedence while keeping expression evaluation restricted and secure.
5. **Debugging the equals button:** Investigate why the browser appeared to reject expression-based calculations despite successful automated tests.
6. **Final review and documentation:** Reassess the implementation, check the reported test results, document technical decisions, and explain how AI contributed to the development process.

I used the AI-generated findings and implementations as material to evaluate rather than assuming that the outputs were correct simply because they appeared technically convincing.

The recoverable prompts and outputs are documented in `AI_USAGE.md` and `AI_PROMPT_TRANSCRIPT.md`. The original Cursor conversation remains the primary source for longer interactions. The repository documentation is not presented as a complete verbatim export of every conversation or tool response.

## 2. For each prompt:

### What were you hoping for the AI to accomplish?

**For the code review:**

My objective was to identify meaningful problems that could affect security, correctness, reliability, and maintainability.

I wanted the review to resemble constructive feedback from an engineer reviewing a pull request, rather than a collection of cosmetic suggestions.

I focused particularly on:

- Authentication and webhook signature verification
- SQL injection risks and database operations
- Whether the upsert implementation behaved as intended
- Handling of secrets and configuration
- Authorisation risks involving user roles
- Error handling and operational reliability

I also wanted the recommendations to respect the existing system requirements. For example, changing the vendor's signature algorithm without confirming compatibility would not necessarily represent an improvement.

**For the coding challenge:**

My objective was to develop a functional, understandable, and testable web calculator using a lightweight architecture.

I chose a Flask backend with a simple HTML, CSS, and JavaScript frontend because the exercise did not require a large application framework.

I wanted the application to support arithmetic operations, validate user input, handle numerical edge cases, and produce predictable results.

As the implementation developed, I introduced additional requirements for expression display, operator precedence, configurable decimal rounding, and parentheses.

An important consideration was keeping the implementation manageable and avoiding unnecessary complexity, particularly unsafe expression evaluation using `eval`.

### What did it actually do?

**Code review:**

Cursor helped produce the findings documented in `CODE_REVIEW.md`, with references to the original Python webhook implementation.

The most important findings included:

1. **SQL injection:** Database queries were constructed using Python f-strings, allowing external data to influence SQL statements.
2. **Incorrect upsert behaviour:** The code did not properly implement the expected update behaviour for existing records.
3. **Authorisation risks:** The webhook allowed externally supplied information to influence user roles without sufficient validation.
4. **Weak secret handling:** A fallback value of `"dev-secret"` created a risk if the application was deployed without a properly configured secret.
5. **Signature comparison:** Direct string comparison could be replaced with a constant-time comparison method such as `hmac.compare_digest`.
6. **Error handling:** Some failures were not handled in a way that would support reliable operation or useful debugging.

One important distinction was the webhook signature algorithm.

The vendor documentation specified `SHA256(secret + body)`. Although HMAC is generally preferable when designing a new message-authentication protocol, replacing the existing algorithm without coordinating with the vendor could break interoperability.

Therefore, I distinguished between implementing the existing protocol safely and proposing an improvement that would require a protocol change.

**Coding challenge:**

Cursor assisted with developing a Flask-based calculator using:

- Python and Flask for the backend
- HTML, CSS, and JavaScript for the frontend
- `decimal.Decimal` for arithmetic
- A restricted expression evaluator supporting operator precedence and parentheses
- Server-side input validation
- pytest for automated testing

The implementation also introduced an important separation between the exact calculation result and the rounded value shown to users.

This prevents display rounding from unnecessarily reducing the precision of subsequent calculations.

The latest reported automated test run completed successfully:

**62 passed, 0 failed, 0 skipped** (`python -m pytest -q`).

### Did you have to re-prompt it based on its output?

Yes. Several follow-up prompts were necessary, although not all of them resulted from incorrect AI output.

Some prompts introduced additional functionality, while others focused on investigating unexpected behaviour or validating the implementation.

**First, the development environment required troubleshooting.**

On Windows, the `python` command initially pointed to the Microsoft Store execution alias rather than the intended Python installation.

Using `py -3` and the project's virtual environment resolved the issue.

**Second, further testing exposed numerical edge cases.**

An additional audit identified an uncaught `decimal.Overflow` exception that could result in an HTTP 500 response.

It also identified situations where very long division results could not be reused as inputs because they exceeded the application's input-length restrictions.

These findings led to targeted fixes and regression tests.

**Third, I expanded the calculator's requirements.**

The original implementation evolved to support complete expression display, operator precedence, configurable rounding, and parentheses.

These changes were feature improvements rather than evidence that the initial calculator had completely failed.

**Finally, I encountered a discrepancy between automated tests and browser behaviour.**

After expression support was added, the equals button appeared to stop working.

The automated tests were passing, but the browser continued to receive an error indicating that the API expected the old `a`, `b`, and `operator` request fields.

The investigation identified that an older Flask process was still running on port 5000.

Restarting the application with the updated implementation resolved the API mismatch.

This demonstrated an important distinction: successful unit tests do not necessarily prove that the process serving the application is running the latest code.

Cursor assisted with executing and investigating these checks. I reviewed the reported findings and the explanations behind the fixes; I do not treat AI-reported test execution as equivalent to independently completing every manual check.

### If you had to change your approach, why?

My main priority was making changes that genuinely improved correctness and security without introducing unnecessary complexity.

For the webhook, that meant respecting the documented signature contract while addressing actual vulnerabilities. Replacing a vendor-specified algorithm without confirming compatibility could create a new problem rather than solve the existing one.

For the calculator, the requirements eventually made a basic two-operand approach insufficient. Supporting expressions such as `10 + 5 × 2` required an evaluation model that understood operator precedence.

I therefore focused on a restricted parser rather than using `eval`, allowing the application to evaluate supported mathematical expressions without executing arbitrary Python code.

These decisions reinforced the importance of understanding the problem before accepting a solution. I wanted to consider not only whether a change worked, but also why it was appropriate, what risks it introduced, and whether a simpler alternative existed.

---

# Part 2 — Coding Challenge: Follow-up Questions

## 1. How far were you able to get with the exercise?

I completed a functional web calculator with a Flask backend, an interactive frontend, input validation, expression evaluation, and an automated test suite.

The application supports the following functionality:

**Core calculator features:**

- Addition, subtraction, multiplication, and division
- Decimal and negative numbers
- Expression display before evaluation
- Operator precedence
- Parentheses for grouping expressions
- Clear and backspace functionality
- Positive/negative sign switching
- Division-by-zero error handling
- Server-side input validation

**Additional functionality:**

- Configurable decimal places from 0 to 8
- Default display precision of 2 decimal places
- `ROUND_HALF_UP` rounding for displayed results
- Preservation of the underlying calculation result for subsequent operations
- Support for both expression-based and legacy two-operand API requests

**Backend endpoints:**

- `POST /api/calculate` — evaluates mathematical expressions or supported binary operations
- `POST /api/format` — formats an existing exact result to the requested display precision

For example, the calculation logic is designed and tested to produce:

- `10 + 5 * 2` → `20`
- `(10 + 5) * 2` → `30`
- `10 / 3` → `3.33` when displayed to two decimal places

The project also includes pytest coverage for arithmetic operations, expression evaluation, validation, rounding, and identified edge cases.

The latest automated test execution reported **62 passing tests with no failures or skipped tests**.

I also completed the separate Python webhook code review, documenting the main security and reliability concerns in `CODE_REVIEW.md`.

The application is intended to run locally through Flask. I have not included automated browser end-to-end testing as a completed deliverable, and I would distinguish the successful automated test results from a separately verified manual browser-testing record.

Overall, I was able to implement the core requirements and extend the application with functionality that improves usability while preserving a relatively small and understandable architecture.

## 2. What challenges did you encounter in the process?

The most challenging part was understanding why the calculator appeared to fail even though the automated tests were passing.

After expression support was introduced, the frontend began sending expression-based requests to the backend. However, the browser was still receiving responses from an older Flask process that expected the previous request format.

At first, the behaviour appeared to suggest that the equals-button functionality or expression evaluation was incorrect.

The important step was comparing the actual HTTP response against the expected API contract and investigating which application process was handling the request.

The issue was ultimately caused by a stale server process rather than the new calculation logic.

This experience highlighted that debugging involves investigating the complete system, including the environment and running processes, rather than immediately assuming that the latest code is wrong.

Another challenge was maintaining numerical correctness as the calculator became more capable.

For example, displaying `10 ÷ 3` as `3.33` should not mean that the calculator permanently replaces the underlying result with `3.33` before the next operation.

Separating calculation precision from display precision required additional consideration of how values moved between the backend and frontend.

I also needed to consider how expressions could be evaluated safely. Supporting operator precedence and parentheses was useful, but I wanted the evaluator to recognise only permitted mathematical operations instead of accepting arbitrary executable expressions.

Finally, the webhook review required distinguishing genuine security vulnerabilities from recommendations that might be inappropriate for the existing system.

For instance, improving signature comparison and secret management was important, but changing the documented vendor authentication protocol without agreement would create a compatibility risk.

Together, these challenges reinforced the importance of understanding the root cause, evaluating trade-offs, and using evidence rather than assumptions when making technical decisions.

## 3. If you were given unlimited time, what additional functionality would you include?

Rather than immediately adding more calculator features, I would prioritise improving testing, reliability, and deployment readiness.

My first improvement would be introducing automated browser-level end-to-end tests using a tool such as Playwright.

These tests would exercise complete user interactions, including entering expressions, pressing equals, changing rounding precision, using parentheses, and recovering from invalid input.

This would help identify integration issues that backend unit tests alone might not detect.

I would also improve test coverage for unusual inputs, numerical boundaries, and behaviour across supported browsers.

If the application were intended for public deployment, I would consider additional operational and security measures such as appropriate security headers, HTTPS, rate limiting, and production-ready error handling.

I would also improve the development workflow through automated checks in a CI pipeline, ensuring that tests run consistently when changes are introduced.

However, I would avoid adding unnecessary features such as accounts, databases, or a complex frontend framework simply for the sake of making the project larger.

My priority would be making the existing application more reliable, maintainable, and easier to verify before expanding its scope.

## 4. If you used AI, please include all your prompts and answer the following questions.

I used Cursor to assist with code review, implementation, testing, debugging, and documentation.

The recoverable prompts and available outputs are documented in `AI_USAGE.md` and `AI_PROMPT_TRANSCRIPT.md`.

These files summarise the recorded interactions but are not a complete verbatim export of the full Cursor history. Longer conversations and some intermediate tool outputs remain in the original Cursor session.

### What did the AI do well?

Cursor was particularly effective at accelerating implementation, organising code into manageable components, and providing useful starting points for technical investigation.

For the webhook review, it helped identify issues such as SQL injection, incorrect database update behaviour, insecure defaults, and insufficient authorisation controls.

It also helped organise those findings into structured, line-referenced feedback suitable for a pull request review.

For the calculator, Cursor supported the development of a relatively lightweight Flask application without introducing unnecessary frameworks or dependencies.

Separating calculation logic into testable Python functions also made the implementation easier to reason about and validate.

Another strength was its ability to support incremental development.

When I introduced requirements such as expression display, rounding, and parentheses, Cursor could help extend the existing implementation rather than requiring a complete rebuild.

It was also useful for generating test cases, examining edge conditions, and exploring possible explanations when unexpected behaviour occurred.

Overall, I found AI most valuable when the objective and constraints were clear, because its output could then be evaluated against specific requirements rather than accepted on appearance alone.

### What did the AI do poorly?

Although Cursor was useful, several limitations became apparent during the assessment.

**1. Passing tests did not guarantee that the running application behaved correctly.**

After expression-based evaluation was implemented, the automated tests passed, but the browser continued to communicate with an older Flask process.

The AI-assisted workflow initially focused on the updated code, while the actual running environment was not aligned with that version.

This demonstrated that successful automated tests cannot replace checking the application that users actually interact with.

**2. Some edge cases were not addressed by the initial implementation.**

The additional audit identified numerical conditions that were not handled adequately, including uncaught `decimal.Overflow` exceptions and long division results that could not be reused safely within the application's input limits.

These issues showed that an implementation can work well for standard examples while still containing meaningful reliability problems.

**3. Some AI-generated explanations were too broad or confident.**

Early documentation and follow-up answers sometimes sounded more like generic technical reports than an accurate explanation of the decisions made during this assessment.

I needed to distinguish between what the implementation demonstrated, what the automated tests reported, and what could reasonably be claimed as personally verified.

This was particularly important because technical documentation should communicate evidence rather than merely sound convincing.

**4. AI interaction records were not automatically complete.**

Although I documented the important prompts and outputs, reconstructing longer interactions afterwards was more difficult than preserving the original records as the work progressed.

This made me recognise that transparency about AI usage should be incorporated into the development workflow rather than treated as a final documentation task.

### For the places it did poorly, how did you change your approach to your prompts to improve its output?

I progressively moved toward smaller, more focused prompts with clearer expectations.

Instead of asking for broad improvements, I focused on specific questions, behaviours, and risks.

For example, I used targeted requests to investigate critical defects, add expression evaluation without unnecessarily rebuilding the application, and introduce parentheses while preserving the existing calculation functionality.

When the equals button appeared broken, I focused on investigating the difference between the running API and the updated implementation rather than immediately asking Cursor to rewrite the calculator.

This helped direct attention toward identifying the root cause of the problem.

For the code review, I also focused on the context behind each recommendation. A suggestion could appear secure in isolation but still be inappropriate if it violated the existing vendor contract.

For documentation, I placed greater emphasis on accurate attribution and verifiable evidence.

I wanted the final answers to distinguish clearly between AI assistance, implementation details, reported test results, and my own technical reasoning.

This approach made the AI interactions more useful because the outputs were directed toward specific engineering problems and could be examined against clear expectations.

### What would you do differently next time you use AI on a take-home assessment?

Next time, I would improve three areas: **planning, verification, and documentation**.

First, I would define the requirements, expected behaviour, and acceptance criteria before asking AI to assist with implementation.

This would give me a clearer basis for evaluating its recommendations and deciding which changes were actually necessary.

Second, I would use smaller, focused prompts and verify important changes incrementally. I would combine automated tests with direct checks of the running application, rather than relying on test results or AI explanations alone.

Third, I would preserve the actual AI prompts, outputs, and important development decisions as I worked, including which suggestions I accepted, modified, or rejected and why.

This would make the process more transparent and easier for another engineer to understand.

The most important lesson I took from this assessment is that **AI can accelerate software development, but it does not replace engineering judgement or responsibility**.

I still need to understand the problem, evaluate the proposed solution, identify risks, and verify that the final implementation behaves as intended.

---

# Additional Thoughts

This exercise gave me an opportunity to work through two complementary aspects of software engineering: reviewing existing code and developing a small application.

The webhook review demonstrated the importance of considering security, reliability, and compatibility when evaluating someone else's implementation.

The calculator challenge demonstrated that even a relatively simple application involves meaningful decisions about architecture, correctness, input validation, testing, and debugging.

I also found the AI component valuable because it encouraged me to think critically about how AI-assisted development should be evaluated.

Rather than treating AI-generated code as a finished result, I see it as a tool that can support implementation and investigation, provided its output is understood and verified.

If I were continuing this project, my priority would be strengthening browser-level verification and the development workflow before introducing additional features.

Overall, the experience reinforced my interest in building software that is not only functional, but also understandable, secure, and maintainable.