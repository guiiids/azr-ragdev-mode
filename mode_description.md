The system includes three distinct developer evaluation modes: eVal, reAsk, and sMash. These modes allow for detailed analysis and optimization of the RAG (Retrieval-Augmented Generation) assistant's performance.

### Evaluator Mode (eVal)

The **Evaluator Mode (eVal)** is designed for a single, detailed evaluation of the RAG assistant's response to a specific query with user-defined parameters.

* **Parameter Collection**: The user interface, managed by `dev_eval_chat.js`, interactively collects parameters step-by-step. These parameters include the `query`, a custom `prompt` (optional), `temperature`, `top_p`, and `max_tokens`.
* **API Endpoint**: Once parameters are collected, a `POST` request is sent to the `/api/dev_eval` endpoint.
* **Processing**:
    * The backend uses the `FlaskRAGAssistant` to generate a response based on the provided query and settings (temperature, top_p, max_tokens, and an overridden system prompt if a custom prompt is given).
    * The `developer_evaluate_job` function from `llm_summary.py` is then called to provide an analysis and actionable suggestions regarding the prompt, parameters, and the generated result.
* **Output**: The API returns the LLM's `result` (answer), any `sources` used, the `developer_evaluation` text, URLs to download JSON and Markdown reports of the evaluation, and the raw `markdown_report` content. The Markdown report includes the query, parameters, custom prompt (if any), LLM output, sources, and the developer evaluation.

---
### Batch Mode (reAsk)

The **Batch Mode (reAsk)** allows for running the same query multiple times with the same set of parameters to assess consistency or observe variations in responses.

* **API Endpoint**: This mode is triggered via a `POST` request to the `/api/dev_eval_batch` endpoint.
* **Parameters**: It accepts a `query`, `prompt`, `parameters` (temperature, top_p, max_tokens), and the number of `runs`.
* **Processing**:
    * The RAG assistant processes the query for the specified number of `runs` using the given configuration.
    * Optionally, if the `llm_summary` module is available, the `summarize_results` function can be called to generate a summary of all the runs.
* **Output**: The endpoint returns a list of `results` (one for each run, including answer, sources, etc.), the `summary` (if generated), and download links for JSON and Markdown reports detailing the batch execution.

---
### Compare Mode (sMash)

The **Compare Mode (sMash)** facilitates a side-by-side comparison of the RAG assistant's performance on the same query but with two different sets of configurations (e.g., different prompts or model parameters).

* **API Endpoint**: This mode is accessed through a `POST` request to the `/api/dev_eval_compare` endpoint.
* **Parameters**:
    * It requires a `query`.
    * It takes configurations for two batches:
        * **Batch 1**: `prompt`, `parameters` (temperature, top_p, max_tokens), and `runs`.
        * **Batch 2**: `prompt` (can default to Batch 1's prompt if not specified), `temperature`, `top_p`, `max_tokens`, and `runs`.
    * An optional boolean flag `generate_llm_analysis` (defaults to true) determines if an LLM should be used to analyze and compare the results of the two batches.
* **Processing**:
    * The RAG assistant runs the query for the specified number of `runs` for each batch, using their respective configurations.
    * A general `developer_evaluate_job` is performed on the comparison setup itself.
    * If `generate_llm_analysis` is true, the `summarize_batch_comparison` function (from `llm_summary_compact.py`) is invoked to produce an LLM-generated analysis of the differences and similarities between the two batches' outputs.
* **Output**: The API returns `batch1_results`, `batch2_results`, the general `developer_evaluation`, download URLs for comprehensive JSON and Markdown reports, the raw `markdown_report`, and the `llm_analysis` (if requested). The Markdown report is structured to present the comparison clearly.