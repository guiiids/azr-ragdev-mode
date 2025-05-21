import logging
import traceback
import json
from rag_assistant import FlaskRAGAssistant

# Try to import the summary modules if present
try:
    from llm_summary import summarize_results, developer_evaluate_job
    from llm_summary_compact import summarize_batch_comparison
    HAS_SUMMARY = True
except ImportError:
    HAS_SUMMARY = False

def setup_logging():
    logger = logging.getLogger("batch_rag")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("app.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # Also log to console
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def get_float(prompt, default, minval, maxval):
    try:
        val = float(input(f"{prompt} (default {default}): ").strip() or default)
        if val < minval or val > maxval:
            raise ValueError
        return val
    except ValueError:
        print(f"Invalid value, using default {default}")
        return default

def get_int(prompt, default, minval, maxval):
    try:
        val = int(input(f"{prompt} (default {default}): ").strip() or default)
        if val < minval or val > maxval:
            raise ValueError
        return val
    except ValueError:
        print(f"Invalid value, using default {default}")
        return default

def run_batch(query, system_prompt, params, logger, batch_label="batch"):
    settings = {
        "temperature": params["temperature"],
        "top_p": params["top_p"],
        "max_tokens": params["max_tokens"]
    }
    if system_prompt:
        settings["system_prompt"] = system_prompt
        settings["system_prompt_mode"] = "Override"
    assistant = FlaskRAGAssistant(settings=settings)
    actual_prompt = getattr(assistant, "DEFAULT_SYSTEM_PROMPT", "")
    logger.info(f"{batch_label}: System prompt sent to AzureOpenAI: {actual_prompt!r}")
    results = []
    for i in range(params["n_runs"]):
        try:
            logger.info(f"{batch_label} Run {i+1}: Query: {query!r}")
            answer, sources, _, evaluation, context = assistant.generate_rag_response(query)
            logger.info(f"{batch_label} Run {i+1}: Answer: {answer!r}")
            logger.info(f"{batch_label} Run {i+1}: Sources: {sources!r}")
            # Display response in a more readable format
            print(f"\n{'='*80}")
            print(f"  {batch_label.upper()} RUN {i+1}")
            print(f"{'='*80}")
            print(f"\n📝 ANSWER:\n")
            print(f"{answer}")
            
            if sources:
                print(f"\n📚 SOURCES:\n")
                for idx, source in enumerate(sources, 1):
                    print(f"  [{idx}] {source.get('title', 'Untitled')}")
            print(f"\n{'-'*80}")
            results.append({
                "run": i+1,
                "answer": answer,
                "sources": sources,
                "evaluation": evaluation,
                "context": context
            })
        except Exception as e:
            logger.error(f"{batch_label} Error on run {i+1}: {e}")
            logger.error(traceback.format_exc())
            results.append({
                "run": i+1,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    return results

def offer_summary(results, json_file=None, is_comparison=False):
    if not HAS_SUMMARY:
        print("\n[LLM Summary module not available. Skipping summary generation.]")
        return
    resp = input("\nGenerate LLM summary report for these results? (y/n, default n): ").strip().lower() or "n"
    if resp != "y":
        return
    print("\nGenerating LLM summary report (this may take a moment)...")
    try:
        # Use compact summary for comparison mode
        if is_comparison:
            summary = summarize_batch_comparison(results)
        else:
            summary = summarize_results(results)
            
        print("\n=== LLM Summary Report ===\n")
        print(summary)
        
        # Save summary to separate report file
        save_report = input("\nSave LLM summary report to a separate file? (y/n, default y): ").strip().lower() or "y"
        if save_report == "y":
            report_format = input("Choose format (md/txt, default md): ").strip().lower() or "md"
            if report_format not in ["md", "txt"]:
                report_format = "md"
                
            # Create reports directory if it doesn't exist
            import os
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                print(f"\nCreated directory: {reports_dir}")
            
            # Generate report filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if is_comparison:
                report_filename = os.path.join(reports_dir, f"comparison_report_{timestamp}.{report_format}")
            else:
                report_filename = os.path.join(reports_dir, f"batch_report_{timestamp}.{report_format}")
                
            # Create report content
            if report_format == "md":
                report_content = f"# LLM Summary Report\n\n"
                report_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                
                # Add query information
                report_content += f"## Query\n\n"
                report_content += f"`{results.get('query', 'No query provided')}`\n\n"
                
                # Add batch information for comparison mode
                if is_comparison:
                    batch1 = results.get("batch_1", {})
                    batch2 = results.get("batch_2", {})
                    
                    report_content += f"## Batch 1 Parameters\n\n"
                    batch1_params = batch1.get("parameters", {})
                    report_content += f"- Temperature: {batch1_params.get('temperature', 'N/A')}\n"
                    report_content += f"- Top P: {batch1_params.get('top_p', 'N/A')}\n"
                    report_content += f"- Max Tokens: {batch1_params.get('max_tokens', 'N/A')}\n"
                    report_content += f"- System Prompt: `{batch1.get('system_prompt', batch1_params.get('system_prompt', 'Default'))}`\n\n"
                    
                    report_content += f"## Batch 2 Parameters\n\n"
                    batch2_params = batch2.get("parameters", {})
                    report_content += f"- Temperature: {batch2_params.get('temperature', 'N/A')}\n"
                    report_content += f"- Top P: {batch2_params.get('top_p', 'N/A')}\n"
                    report_content += f"- Max Tokens: {batch2_params.get('max_tokens', 'N/A')}\n"
                    report_content += f"- System Prompt: `{batch2.get('system_prompt', batch2_params.get('system_prompt', 'Default'))}`\n\n"
                
                # Add summary
                report_content += f"## Analysis\n\n{summary}\n"
            else:
                # Plain text format
                report_content = f"LLM SUMMARY REPORT\n\n"
                report_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                report_content += f"QUERY: {results.get('query', 'No query provided')}\n\n"
                
                if is_comparison:
                    batch1 = results.get("batch_1", {})
                    batch2 = results.get("batch_2", {})
                    
                    report_content += f"BATCH 1 PARAMETERS:\n"
                    batch1_params = batch1.get("parameters", {})
                    report_content += f"- Temperature: {batch1_params.get('temperature', 'N/A')}\n"
                    report_content += f"- Top P: {batch1_params.get('top_p', 'N/A')}\n"
                    report_content += f"- Max Tokens: {batch1_params.get('max_tokens', 'N/A')}\n"
                    report_content += f"- System Prompt: {batch1.get('system_prompt', batch1_params.get('system_prompt', 'Default'))}\n\n"
                    
                    report_content += f"BATCH 2 PARAMETERS:\n"
                    batch2_params = batch2.get("parameters", {})
                    report_content += f"- Temperature: {batch2_params.get('temperature', 'N/A')}\n"
                    report_content += f"- Top P: {batch2_params.get('top_p', 'N/A')}\n"
                    report_content += f"- Max Tokens: {batch2_params.get('max_tokens', 'N/A')}\n"
                    report_content += f"- System Prompt: {batch2.get('system_prompt', batch2_params.get('system_prompt', 'Default'))}\n\n"
                
                report_content += f"ANALYSIS:\n\n{summary}\n"
            
            # Save the report
            try:
                with open(report_filename, "w", encoding="utf-8") as f:
                    f.write(report_content)
                print(f"\nLLM summary report saved to: {report_filename}")
            except Exception as e:
                print(f"Failed to save report to {report_filename}: {e}")
        
        # Also save summary alongside results in JSON if provided
        if json_file:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # If the file is a list, wrap in a dict
                if isinstance(data, list):
                    data = {"results": data, "llm_summary": summary}
                else:
                    data["llm_summary"] = summary
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\nSummary also appended to {json_file}")
            except Exception as e:
                print(f"Could not append summary to {json_file}: {e}")
    except Exception as e:
        print(f"Failed to generate summary: {e}")

def main():
    logger = setup_logging()
    print("Select mode:\n0. Developer evaluation (vanilla)\n1. Standard batch\n2. Compare settings (Mode 2)")
    mode = input("Enter mode (0, 1 or 2, default 1): ").strip() or "1"

    if mode == "0":
        # Mode 0: Developer evaluation
        query = input("Enter your query: ").strip()
        system_prompt = input("Enter prompt/instructions (or leave blank for default): ").strip()
        temperature = get_float("Set temperature (0.0-2.0)", 0.3, 0.0, 2.0)
        top_p = get_float("Set top_p (0.0-1.0)", 1.0, 0.0, 1.0)
        max_tokens = get_int("Set max_tokens (1-4000)", 1000, 1, 4000)

        params = {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }

        settings = {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        if system_prompt:
            settings["system_prompt"] = system_prompt
            settings["system_prompt_mode"] = "Override"

        assistant = FlaskRAGAssistant(settings=settings)
        actual_prompt = getattr(assistant, "DEFAULT_SYSTEM_PROMPT", "")
        logger.info(f"Mode 0: System prompt sent to AzureOpenAI: {actual_prompt!r}")

        try:
            logger.info(f"Mode 0: Query: {query!r}")
            answer, sources, _, evaluation, context = assistant.generate_rag_response(query)
            # Display response in a more readable format
            print(f"\n{'='*80}")
            print(f"  DEVELOPER EVALUATION OUTPUT")
            print(f"{'='*80}")
            print(f"\n📝 ANSWER:\n")
            print(f"{answer}")
            
            if sources:
                print(f"\n📚 SOURCES:\n")
                for idx, source in enumerate(sources, 1):
                    print(f"  [{idx}] {source.get('title', 'Untitled')}")
            print(f"\n{'-'*80}")
            # Developer evaluation
            if HAS_SUMMARY:
                print("\n=== Developer Evaluation (LLM Suggestions) ===\n")
                suggestions = developer_evaluate_job(
                    query=query,
                    prompt=system_prompt,
                    parameters=params,
                    result=answer
                )
                print(suggestions)
            else:
                print("\n[LLM Summary module not available. Skipping developer evaluation.]")
            # Save output
            json_file = input("\nEnter JSON output filename to save results (or leave blank to skip): ").strip()
            if json_file:
                output = {
                    "query": query,
                    "prompt": system_prompt,
                    "parameters": params,
                    "result": answer,
                    "sources": sources
                }
                if HAS_SUMMARY:
                    output["developer_evaluation"] = suggestions
                try:
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)
                    print(f"\nResults saved to {json_file}")
                except Exception as e:
                    print(f"Failed to save results to {json_file}: {e}")
        except Exception as e:
            logger.error(f"Mode 0: Error: {e}")
            logger.error(traceback.format_exc())
            print(f"Error: {e}")

    elif mode == "2":
        # Shared input
        query = input("Enter your query: ").strip()
        
        # Batch 1 params
        print("\n--- Batch 1 parameters ---")
        system_prompt1 = input("Enter system prompt/instructions for Batch 1 (or leave blank for default): ").strip()
        temp1 = get_float("Set temperature (0.0-2.0)", 0.3, 0.0, 2.0)
        top_p1 = get_float("Set top_p (0.0-1.0)", 1.0, 0.0, 1.0)
        max_tokens1 = get_int("Set max_tokens (1-4000)", 1000, 1, 4000)
        n_runs1 = get_int("How many times to run batch 1? (max 20)", 1, 1, 20)
        logger.info(f"Mode 2: Batch 1 params: prompt={system_prompt1!r}, temp={temp1}, top_p={top_p1}, max_tokens={max_tokens1}, n_runs={n_runs1}")

        # Batch 2 params
        print("\n--- Batch 2 parameters ---")
        system_prompt2 = input("Enter system prompt/instructions for Batch 2 (or leave blank for default): ").strip()
        temp2 = get_float("Set temperature (0.0-2.0)", 0.3, 0.0, 2.0)
        top_p2 = get_float("Set top_p (0.0-1.0)", 1.0, 0.0, 1.0)
        max_tokens2 = get_int("Set max_tokens (1-4000)", 1000, 1, 4000)
        n_runs2 = get_int("How many times to run batch 2? (max 20)", 1, 1, 20)
        logger.info(f"Mode 2: Batch 2 params: prompt={system_prompt2!r}, temp={temp2}, top_p={top_p2}, max_tokens={max_tokens2}, n_runs={n_runs2}")

        # Run batch 1
        print("\nRunning batch 1...")
        batch1_params = {
            "temperature": temp1,
            "top_p": top_p1,
            "max_tokens": max_tokens1,
            "n_runs": n_runs1,
            "system_prompt": system_prompt1
        }
        batch1_results = run_batch(query, system_prompt1, batch1_params, logger, batch_label="batch_1")

        # Confirm to run batch 2
        confirm = input("\nBatch 1 complete. Run batch 2? (y/n, default y): ").strip().lower() or "y"
        if confirm != "y":
            print("Batch 2 cancelled.")
            offer_summary({"batch_1": {"parameters": batch1_params, "results": batch1_results}})
            return

        # Run batch 2
        print("\nRunning batch 2...")
        batch2_params = {
            "temperature": temp2,
            "top_p": top_p2,
            "max_tokens": max_tokens2,
            "n_runs": n_runs2,
            "system_prompt": system_prompt2
        }
        batch2_results = run_batch(query, system_prompt2, batch2_params, logger, batch_label="batch_2")

        # Save JSON
        json_file = input("\nEnter JSON output filename to save results (or leave blank to skip): ").strip()
        output = {
            "query": query,
            "batch_1": {
                "parameters": batch1_params,
                "system_prompt": system_prompt1,
                "results": batch1_results
            },
            "batch_2": {
                "parameters": batch2_params,
                "system_prompt": system_prompt2,
                "results": batch2_results
            }
        }
        if json_file:
            try:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                print(f"\nResults saved to {json_file}")
                logger.info(f"Mode 2: Results saved to {json_file}")
            except Exception as e:
                print(f"Failed to save results to {json_file}: {e}")
                logger.error(f"Failed to save results to {json_file}: {e}")
                logger.error(traceback.format_exc())
        # Use the compact summary for comparison mode
        offer_summary(output, json_file=json_file if json_file else None, is_comparison=True)

    else:
        # Standard batch mode (Mode 1)
        query = input("Enter your query: ").strip()
        system_prompt = input("Enter system prompt/instructions (or leave blank for default): ").strip()
        try:
            n_runs = int(input("How many times to run? (max 20): ").strip())
        except ValueError:
            n_runs = 1
        n_runs = min(max(n_runs, 1), 20)

        temperature = get_float("Set temperature (0.0-2.0)", 0.3, 0.0, 2.0)
        top_p = get_float("Set top_p (0.0-1.0)", 1.0, 0.0, 1.0)
        max_tokens = get_int("Set max_tokens (1-4000)", 1000, 1, 4000)

        json_file = input("Enter JSON output filename to save results (or leave blank to skip): ").strip()
        save_json = bool(json_file)

        logger.info(f"User submitted system prompt: {system_prompt!r}")
        logger.info(f"User set temperature: {temperature}, top_p: {top_p}, max_tokens: {max_tokens}")
        settings = {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        if system_prompt:
            settings["system_prompt"] = system_prompt
            settings["system_prompt_mode"] = "Override"

        assistant = FlaskRAGAssistant(settings=settings)
        actual_prompt = getattr(assistant, "DEFAULT_SYSTEM_PROMPT", "")
        logger.info(f"System prompt sent to AzureOpenAI: {actual_prompt!r}")

        results = []
        for i in range(n_runs):
            try:
                logger.info(f"Run {i+1}: Query: {query!r}")
                answer, sources, _, evaluation, context = assistant.generate_rag_response(query)
                logger.info(f"Run {i+1}: Answer: {answer!r}")
                logger.info(f"Run {i+1}: Sources: {sources!r}")
                # Display response in a more readable format
                print(f"\n{'='*80}")
                print(f"  RUN {i+1}")
                print(f"{'='*80}")
                print(f"\n📝 ANSWER:\n")
                print(f"{answer}")
                
                if sources:
                    print(f"\n📚 SOURCES:\n")
                    for idx, source in enumerate(sources, 1):
                        print(f"  [{idx}] {source.get('title', 'Untitled')}")
                print(f"\n{'-'*80}")
                results.append({
                    "run": i+1,
                    "query": query,
                    "system_prompt": system_prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "answer": answer,
                    "sources": sources,
                    "evaluation": evaluation,
                    "context": context
                })
            except Exception as e:
                logger.error(f"Error on run {i+1}: {e}")
                logger.error(traceback.format_exc())
                results.append({
                    "run": i+1,
                    "query": query,
                    "system_prompt": system_prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })

        if save_json:
            try:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"\nResults saved to {json_file}")
                logger.info(f"Results saved to {json_file}")
            except Exception as e:
                print(f"Failed to save results to {json_file}: {e}")
                logger.error(f"Failed to save results to {json_file}: {e}")
                logger.error(traceback.format_exc())
        offer_summary(results, json_file=json_file if save_json else None)

if __name__ == "__main__":
    main()
