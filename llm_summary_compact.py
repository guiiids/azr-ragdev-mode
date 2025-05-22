import json
from rag_assistant import FlaskRAGAssistant

# A more compact prompt that focuses only on the essential information
COMPACT_SUMMARY_PROMPT = """
You are an expert LLM analyst. Compare these two batches of LLM runs with different parameters and prompts:

QUERY: {query}

BATCH 1:
- System Prompt: {prompt1}
- Temperature: {temp1}
- Top P: {top_p1}
- Max Tokens: {max_tokens1}
- Number of runs: {n_runs1}

BATCH 1 SAMPLE RESPONSE:
{response1}

BATCH 2:
- System Prompt: {prompt2}
- Temperature: {temp2}
- Top P: {top_p2}
- Max Tokens: {max_tokens2}
- Number of runs: {n_runs2}

BATCH 2 SAMPLE RESPONSE:
{response2}

Provide:
1. Analysis of how the parameter differences affected the outputs
2. Which parameter settings worked better for this query and why
3. Recommendations for optimal parameters for similar queries
"""

def summarize_batch_comparison(results):
    """
    Create a compact summary comparing two batches with different parameters.
    Only passes essential information to stay within token limits.
    
    Args:
        results: dict containing batch comparison results
        
    Returns:
        str: LLM-generated analysis
    """
    # Extract the query
    query = results.get("query", "No query provided")
    
    # Extract batch 1 parameters, prompt, and sample response
    batch1 = results.get("batch_1", {})
    batch1_params = batch1.get("parameters", {})
    batch1_results = batch1.get("results", [])
    
    # Get system prompt from either location (for backward compatibility)
    system_prompt1 = batch1.get("system_prompt", batch1_params.get("system_prompt", "Default prompt"))
    if not system_prompt1:
        system_prompt1 = "Default prompt"
    
    temp1 = batch1_params.get("temperature", "N/A")
    top_p1 = batch1_params.get("top_p", "N/A")
    max_tokens1 = batch1_params.get("max_tokens", "N/A")
    n_runs1 = batch1_params.get("n_runs", 0)
    
    # Get first successful response from batch 1
    response1 = "No response available"
    for result in batch1_results:
        if "answer" in result and result["answer"]:
            response1 = result["answer"]
            break
    
    # Extract batch 2 parameters, prompt, and sample response
    batch2 = results.get("batch_2", {})
    batch2_params = batch2.get("parameters", {})
    batch2_results = batch2.get("results", [])
    
    # Get system prompt from either location (for backward compatibility)
    system_prompt2 = batch2.get("system_prompt", batch2_params.get("system_prompt", "Default prompt"))
    if not system_prompt2:
        system_prompt2 = "Default prompt"
    
    temp2 = batch2_params.get("temperature", "N/A")
    top_p2 = batch2_params.get("top_p", "N/A")
    max_tokens2 = batch2_params.get("max_tokens", "N/A")
    n_runs2 = batch2_params.get("n_runs", 0)
    
    # Get first successful response from batch 2
    response2 = "No response available"
    for result in batch2_results:
        if "answer" in result and result["answer"]:
            response2 = result["answer"]
            break
    
    # Format the prompt with extracted data
    prompt = COMPACT_SUMMARY_PROMPT.format(
        query=query,
        prompt1=system_prompt1[:300] + "..." if len(system_prompt1) > 300 else system_prompt1,
        temp1=temp1,
        top_p1=top_p1,
        max_tokens1=max_tokens1,
        n_runs1=n_runs1,
        response1=response1[:500] + "..." if len(response1) > 500 else response1,
        prompt2=system_prompt2[:300] + "..." if len(system_prompt2) > 300 else system_prompt2,
        temp2=temp2,
        top_p2=top_p2,
        max_tokens2=max_tokens2,
        n_runs2=n_runs2,
        response2=response2[:500] + "..." if len(response2) > 500 else response2
    )
    
    # Generate the analysis
    assistant = FlaskRAGAssistant(settings={
        "temperature": 0.3,
        "max_tokens": 1000
    })
    
    try:
        answer, *_ = assistant.generate_rag_response(prompt)
        return answer
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Function to evaluate prompt effectiveness for a single batch
EVALUATE_PROMPT_EFFECTIVENESS_PROMPT = """
You are an expert LLM analyst. Given the following:
- Query: {query}
- System Prompt: {prompt}
- Parameters: temperature={temp}, top_p={top_p}, max_tokens={max_tokens}
- Sample Response: {response}

Evaluate how effectively the system prompt addressed the user’s query. Do not critique the query nor suggest alternate queries. Provide a concise assessment.
"""

def evaluate_prompt_effectiveness(batch_data):
    """
    Evaluate how effectively the system prompt addressed the query.
    Args:
        batch_data: dict with keys 'query', 'system_prompt', 'parameters', 'results'
    Returns:
        str: LLM-generated evaluation of the system prompt.
    """
    query = batch_data.get("query", "")
    prompt = batch_data.get("system_prompt", "")
    params = batch_data.get("parameters", {})
    temp = params.get("temperature", "")
    top_p = params.get("top_p", "")
    max_tokens = params.get("max_tokens", "")
    # Get first response
    results = batch_data.get("results", [])
    response = ""
    if isinstance(results, list) and results:
        first = results[0]
        response = first.get("answer") or first.get("result") or ""
    assistant = FlaskRAGAssistant(settings={
        "temperature": temp or 0.3,
        "top_p": top_p or 1.0,
        "max_tokens": max_tokens or 1000
    })
    prompt_text = EVALUATE_PROMPT_EFFECTIVENESS_PROMPT.format(
        query=query,
        prompt=prompt,
        temp=temp,
        top_p=top_p,
        max_tokens=max_tokens,
        response=response[:500] + "..." if len(response) > 500 else response
    )
    try:
        evaluation, *_ = assistant.generate_rag_response(prompt_text)
        return evaluation
    except Exception as e:
        return f"Error evaluating prompt effectiveness: {str(e)}"
