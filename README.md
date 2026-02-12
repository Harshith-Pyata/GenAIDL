# P1-Workflow for TextGrad Expansions: From Dataset to Paper

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

# P2-Workflow for TextGrad Expansions: Textual Learning Rate Scheduling.
This document outlines the step-by-step workflow to complete your research paper by extending the "TextGrad" framework. It covers data generation, implementation, and analysis for the novel direction identified: Textual Learning Rate Scheduling.

## Phase 1: Dataset Generation & Preparation
### Track D: Textual Scheduling (Learning Rate Control)

#### Objective: Stabilize optimization by dynamically adjusting the "step size" (edit magnitude) of the LLM updates to prevent overshooting.

#### Dataset Idea: You need a dataset where multi-step reasoning is required, making it sensitive to "overshooting" (breaking one step while fixing another).


Recommended Dataset: GSM8k (Grade School Math).

Download Links:

GSM8k (GitHub) - https://github.com/openai/grade-school-math

Data Cleaning & EDA Ideas:

Filtering: Select a subset of problems with 4+ reasoning steps to ensure complexity.

EDA Plot: "Problem Complexity" - Histogram of the number of reasoning steps in the ground truth solutions.

EDA Plot: "Baseline Instability" - Run standard TextGrad and plot Edit Distance vs. Iteration. Show the "zig-zag" pattern where the model rewrites too much text in later stages.

## Phase 2: Baseline Implementation (Replication)
Before adding your novelty, ensure the base system works.


Clone the Repo: git clone https://github.com/zou-group/textgrad.

Define the Computation Graph:

Set up the Variable (Math Solution).

Set up the Loss (LLM Evaluation against Ground Truth).

Set up the Optimizer (TGD - Textual Gradient Descent).

Run a Test: Execute the textgrad pipeline on 10 samples of GSM8k. Ensure you get the "Gradient" feedback output in the logs (e.g., "The calculation in step 2 is incorrect").

## Phase 3: Novel Implementation (The Expansion)
For Textual Scheduling (Track D):
Create Scheduler Class: Implement a class that tracks the iteration count and returns a specific prompt.

Code Logic:

Python
class TextualScheduler:
    def get_instruction(self, step):
        if step < 3:
            # Phase 1: High Learning Rate (Exploration)
            return "Rewrite the logic completely if necessary. Make major changes."
        else:
            # Phase 2: Low Learning Rate (Refinement)
            return "Make ONLY small, surgical changes. Do NOT rewrite the whole solution."

# In your optimization loop:
instruction = scheduler.get_instruction(current_step)
variable.update(feedback, instruction)
Integration: Inject this instruction string into the TGD step function, appending it to the standard system prompt.

## Phase 4: Evaluation & Reporting (The "M1" Submission)
Deliverable 1: The EDA Report

Show the distribution of problem lengths in GSM8k to justify why a static prompt is inefficient (short problems need small tweaks, long problems need big fixes).

Show the "Before" trajectory: A line graph of Edit Distance for the baseline, demonstrating high volatility/instability.

Deliverable 2: The Comparison Chart

X-Axis: Iterations (1 to 6).

Y-Axis: Levenshtein Edit Distance (Step Size).

Lines:

Blue Line: Standard TextGrad (Baseline) - Should stay high or oscillate.

Red Line: Scheduled TextGrad (Your Method) - Should show a smooth decay curve (high initially, then dropping near zero).

Deliverable 3: Qualitative Analysis

Show one specific example where standard TextGrad failed (e.g., "It rewrote the correct first half while fixing the second half") and your method succeeded (e.g., "It kept the correct logic and only fixed the final calculation").

Connect this back to the paper's future work on "connections... between numerical optimization... and TextGrad".

# Future Improvements: Adaptive Textual Optimization


Current textual optimization relies on simple, instance-specific feedback analogous to basic Stochastic Gradient Descent, which can lead to instability or slow convergence. A key area for future work is the development of an "Adam for Text" algorithm that formalizes momentum in natural language. By maintaining a history of past textual gradients—extending the specific "momentum analogy" currently used only in radiotherapy —future systems could smooth out conflicting feedback, prevent oscillation between incorrect states, and accelerate convergence across diverse tasks like coding and reasoning.
