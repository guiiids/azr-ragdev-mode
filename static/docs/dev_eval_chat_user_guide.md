# Developer Evaluation Chat UI User Guide

## Introduction

The Developer Evaluation Chat UI provides a conversational interface for evaluating LLM responses with different parameters. This guide will help you understand how to use this feature effectively.

## Getting Started

### Enabling Developer Mode

1. Open the RAG Knowledge Assistant web interface
2. Click the "Developer Mode" button in the top-right corner
3. The button will turn green and display "Developer Mode: ON"
4. The system will prompt you to enter your query

### Conversational Flow

The Developer Evaluation Chat UI will guide you through a series of steps to collect the necessary parameters:

1. **Query Input**: Enter the query you want to evaluate
2. **Custom Instructions**: Enter any custom prompt/instructions (or leave blank for default)
3. **Temperature Setting**: Enter a value between 0.0 and 2.0 (default is 0.3)
4. **Top P Setting**: Enter a value between 0.0 and 1.0 (default is 1.0)
5. **Max Tokens Setting**: Enter a value between 1 and 4000 (default is 1000)

After providing all parameters, the system will automatically process your request and display the results.

## Using the Settings Drawer

You can also set parameters using the Settings drawer:

1. Click the "Settings" button in the top navigation
2. Enter custom instructions in the "Custom Instructions" field
3. Adjust the Temperature, Top P, and Max Tokens sliders/inputs
4. Click "Apply" to save your settings

When you use Developer Mode, these settings will be used as defaults in the conversation flow. You can still override them during the conversation if needed.

## Understanding Parameters

- **Temperature**: Controls randomness in the response. Higher values (e.g., 1.0) make output more random, while lower values (e.g., 0.2) make it more focused and deterministic.
- **Top P**: Controls diversity via nucleus sampling. A value of 0.5 means the model considers tokens comprising the top 50% probability mass.
- **Max Tokens**: The maximum number of tokens to generate in the response.

## Viewing Results

After processing your request, the Developer Evaluation Chat UI will display:

1. **Parameters Used**: A summary of the parameters used for the evaluation
2. **LLM Output**: The raw response from the language model
3. **Developer Evaluation**: An analysis of the response quality and suggestions for improvement
4. **Report Options**: Links to download the evaluation report in JSON or Markdown format

## Saving and Downloading Reports

You can save and download evaluation reports in two formats:

1. **JSON Format**: Contains the raw data including query, parameters, result, and evaluation
2. **Markdown Format**: A formatted report suitable for sharing or documentation

Click the corresponding download button to save the report to your device.

## Viewing Reports in Console

You can also view the formatted Markdown report directly in the console:

1. Click the "View in Console" button after an evaluation
2. The console drawer will open with the formatted report
3. You can scroll through the report and copy content as needed

## Tips for Effective Evaluation

1. **Start with Default Parameters**: Begin with the default parameters and adjust as needed
2. **Systematic Testing**: Change one parameter at a time to understand its impact
3. **Save Important Results**: Download reports for significant findings
4. **Compare Different Settings**: Use the results to compare how different parameters affect the output

## Troubleshooting

- **Invalid Parameter Values**: If you enter an invalid value, the system will use the default value instead
- **Processing Errors**: If an error occurs during processing, check your query and parameters
- **UI Issues**: If the UI becomes unresponsive, try refreshing the page

## Keyboard Shortcuts

- Press **Enter** to submit your input at each step
- Use the **Tab** key to navigate between input fields

## Parameter Persistence

Your parameter preferences (temperature, top_p, max_tokens) are saved in your browser's localStorage. These values will be remembered across sessions, making it easier to continue your evaluation work.
