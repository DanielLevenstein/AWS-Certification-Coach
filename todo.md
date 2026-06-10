0: Regenerate training data and re-run unit tests
1: Populate project README with information from design architecture and data source document
2: Remove tiny llama I don't think we should be using it. 
3: Refactor answer and question json files so that the question and answer are stored in the same file to make it easier to add human test cases.
4: Split code so that two language models are used. One for generating training data and one which will be deployed into production.
5: Increase the size of the model used for generating training data to increase model efficiency.
6: Create a new dataset of wrong answers.
7: For partial answers grad model based on mean sqrd error from target percentage rather than giving it a binary rating. 
8: Update unit tests to output accuracy, precision and recal metrics for the model rather than binary pass fail. 
9: If accuracy comes out to 100% that is a sign the model is over tuned I need real metrics before I can deploy this. 