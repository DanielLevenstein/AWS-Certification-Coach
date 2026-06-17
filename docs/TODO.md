# feature/question_expansion
This feature will be used to expand the question selection to better match AWS Developer Certificate exam.
Once this feature is stable, it will be merged into release/v2.2

## Version 2.1.0 Feature Design. 
- Before making a code change, create a QUESTION_EXPANSION_FEATURE.md document with a proposed design for the new feature which follows the requirements listed in TODO.md file 
- Create a new skill for training new local semantic models which will be used in the next section to implement the Question Heuristic Grading. 
- Create an additional heuristic_scoring to assist in evaluating question fidelity to an original AWS question set. 
- Add all new documentation files to the docs folder except AGENTS.md and SKILL.md
### Version 2.1.1 Question Heuristic Grading

- Download a set of example questions and save them to the data/original_questions directory
- Create a set of new freeform questions and implement a semantic grading model which identifies concept fidelity of the generated questions compared to the original
- Report question fidelity metric in the release notes under the column question fidelity as a percentage
- Use a different model for question fidelity rating from the model used for semantic evaluation of answers. 
- Ensure that the release note is updated with each change and include a one-line description of the release along with detailed release metrics in RELEASE_NOTES.md 
- Each time the release metric code is run commit local changes with a commit message with form v2.1.x Change made.
- Don't make any pushes to docker or create any GitHub tags until a human reviews the changes. 

## Version 2.2.0 heuristic_scoring Feature Design. 

- Before making a code change, create the HEURISTIC_SCORING_FEATURE.md document with a proposed design for the new feature which follows the requirements listed in TODO.md file 
- Update existing heuristic_scoring skill based on information in a design document.

### Version 2.2.1 heuristic_scoring Implementation
Heuristic-based scoring was originally implemented on feature/heuristic_scoring
This branch was originally intended to be release/v2 but cannot be merged in directly because too much code drift has happened since it was created. 

- Implement heuristic-based answer scoring as a third model which returns an answer score between values of 0 and 100
- Ensure that model weights between semantic scoring and heuristic scoring are not linked in the code base.
- Ensure that both heuristic-based scoring and semantic-based scoring use proper train, test, validation split for data.
- For each round of training update the release notes with a one-line change description output release metrics in table. 
