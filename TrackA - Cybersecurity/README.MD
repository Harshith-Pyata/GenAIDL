# Workflow for TextGrad Expansions: From Dataset to Paper

[cite_start]This document outlines the step-by-step workflow to complete your research paper by extending the "TextGrad" framework[cite: 1, 10]. It covers data generation, implementation, and analysis for the three novel directions identified: **Cybersecurity**, **Interactive (Human-in-the-Loop)**, and **Adaptive (Momentum)**.

---

## Phase 1: Dataset Generation & Preparation

### Track A: Cybersecurity (Auto-Defense)
**Objective:** Optimize YARA/Snort rules to detect attacks without blocking legitimate traffic.

* **Dataset Idea:** You need a mix of "Malicious" traffic (to detect) and "Benign" traffic (to protect).
* **Recommended Dataset:** **CIC-IDS2017** or **NSL-KDD**. These are standard benchmarks for Intrusion Detection Systems (IDS).
* **Download Links:**
    * [Canadian Institute for Cybersecurity (CIC-IDS2017)](https://www.unb.ca/cic/datasets/ids-2017.html)
    * [NSL-KDD Dataset (Kaggle)](https://www.kaggle.com/datasets/hassan06/nslkdd)
* **Data Cleaning & EDA Ideas:**
    * **Filtering:** Extract specific attack types (e.g., "DDoS" or "SQL Injection") to create a focused problem statement.
    * **EDA Plot:** "Traffic Distribution" - Visualize the ratio of benign vs. malicious packets.
    * **EDA Plot:** "Rule Complexity" - Calculate the average length of existing standard rules (Snort/YARA) to set a baseline.

### Track B: Interactive TextGrad (Human-in-the-Loop)
[cite_start]**Objective:** Integrate human feedback into the optimization loop to correct "hallucinated gradients"[cite: 206].

* **Dataset Idea:** Use a standard reasoning dataset where "correctness" is objective but "style" or "reasoning" might need human nuance.
* **Recommended Dataset:** **GSM8k** (Math) or **HumanEval** (Code).
* **Download Links:**
    * [GSM8k (Hugging Face)](https://huggingface.co/datasets/gsm8k)
    * [HumanEval (GitHub)](https://github.com/openai/human-eval)
* **Data Generation (Simulation):**
    * Since you cannot have a human sit there for 1,000 iterations, create a **"Simulated Human" dataset**.
    * Run the vanilla TextGrad. Record instances where the gradient was *wrong* (i.e., performance dropped).
    * Manually write "Corrected Gradients" for 50-100 examples to serve as your "Human Feedback" test set.
* **EDA Ideas:**
    * **EDA Plot:** "Gradient Quality" - Categorize the LLM's feedback into "Helpful", "Neutral", and "Harmful" based on the next step's performance.

### Track C: Adaptive TextGrad (Adam-Text/Momentum)
[cite_start]**Objective:** Implement "Momentum" to stabilize text updates[cite: 729].

* **Dataset Idea:** You need a task that is "hard to converge" or oscillates (keeps changing back and forth).
* **Recommended Dataset:** **LeetCode Hard** (Coding) or **Biochemistry Q&A** (GPQA).
* **Download Links:**
    * [LeetCode Hard (via TextGrad Repo)](https://github.com/zou-group/textgrad)
    * [GPQA (Google-Proof QA)](https://github.com/idavidrein/gpqa)
* **EDA Ideas:**
    * **EDA Plot:** "Oscillation Analysis" - In standard TextGrad, track how often the answer flips between two incorrect states.
    * **EDA Plot:** "Convergence Speed" - Plot `Accuracy` vs. `Iteration Count`. Show that standard TextGrad takes 10 steps, while "Adam-Text" might take 5.

---

## Phase 2: Baseline Implementation (Replication)

Before adding your novelty, ensure the base system works.
1.  [cite_start]**Clone the Repo:** `git clone https://github.com/zou-group/textgrad`[cite: 786].
2.  **Define the Computation Graph:**
    * Set up the `Variable` (Prompt/Solution).
    * Set up the `Loss` (LLM Evaluation).
    * [cite_start]Set up the `Optimizer` (TGD - Textual Gradient Descent)[cite: 235].
3.  **Run a Test:** Execute the `textgrad` pipeline on 10 samples of GSM8k. Ensure you get the "Gradient" feedback output in the logs.

---

## Phase 3: Novel Implementation (The Expansion)

### For Cybersecurity (Track A):
* **Modify `Variable`:** Change the variable from "Prompt" to "YARA Rule".
* **Modify `Loss`:** Instead of an LLM judging the answer, the Loss function should run a Python script that executes the YARA rule against your `.pcap` data.
    * `Loss = (Weight * False_Positives) + (Weight * False_Negatives)`
* **Gradient Prompt:** "The rule failed to catch Packet #402 (SQL Injection). Suggest a modification to the regex string."

### For Interactive (Track B):
* **Modify `Optimizer`:** Intercept the `backward()` step.
* **Code Logic:**
    ```python
    gradient_text = llm.generate_critique()
    # Your Novelty:
    print(f"Proposed Gradient: {gradient_text}")
    user_input = input("Approve (y) or Edit (type new): ")
    if user_input != 'y':
        gradient_text = user_input
    # Continue backprop
    variable.update(gradient_text)
    ```

### For Adaptive (Track C):
* **Modify `TGD` Class:** Add a `history` buffer.
* **Code Logic:**
    ```python
    # Standard TGD
    # current_feedback = "Make it shorter."
    
    # Adaptive TGD (Your Novelty)
    previous_feedback = self.history[-1] # e.g., "Make it professional."
    combined_feedback = llm.summarize([previous_feedback, current_feedback]) 
    # Result: "Make it shorter but keep it professional."
    variable.update(combined_feedback)
    ```

---

## Phase 4: Evaluation & Reporting (The "M1" Submission)

**Deliverable 1: The EDA Report**
* Show the distribution of your chosen dataset (e.g., "Difficulty of LeetCode problems").
* Show the "Before" examples (e.g., a bad YARA rule or a hallucinated gradient).

**Deliverable 2: The Comparison Chart**
* **X-Axis:** Iterations (1 to 10).
* **Y-Axis:** Success Rate / Accuracy.
* **Lines:**
    * Blue Line: Standard TextGrad (Baseline).
    * Red Line: Your Method (Cyber / Interactive / Adaptive).

**Deliverable 3: Qualitative Analysis**
* Show one specific example where standard TextGrad failed (e.g., "It deleted the security rule entirely") and your method succeeded ("It refined the IP range specifically").