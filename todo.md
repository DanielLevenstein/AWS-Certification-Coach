1: Populate project README with information from design architecture and data source document
2: Audit code base and markdown files to locate unused code.
3: Refactor answer and question json files so that the question and answer are stored in the same file to make it easier to add human test cases.
4: Split code so that two language models are used. One for generating training data and one which will be deployed into production.
Increase the size of the model used for generating training data to increase model efficiency.
5: Create a new dataset of wrong answers.
