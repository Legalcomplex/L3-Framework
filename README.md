# Legal Large Language Models (LLMs) Evaluation Framework

# 1\. Introduction: Test Deficiency, Not Proficiency

The Legal LLM Evaluation Framework Initiative introduces a novel approach to evaluating Large Language Models (LLMs) in the legal domain. Unlike conventional benchmarks that attempt to measure proficiency on complex, subjective legal tasks, the S3 framework focuses on benchmarking deficiency. It targets three fundamental weaknesses inherent in current LLMs:

1. **Accuracy:** Especially regarding the correct citation of legal codes and case law.  
2. **Recency:** Assessing the model’s knowledge of up-to-date legal information, given inherent training data cutoffs.  
3. **Consistency:** Evaluating the reliability and predictability of model outputs on repeated objective tasks.

This initiative stems from the observation that, while LLMs demonstrate impressive capabilities, their application in the sensitive and precise field of law requires rigorous verification of foundational reliability before assessing higher-level proficiency.

# 2\. The Controversy and Challenges of Legal AI Benchmarking

Benchmarking AI for legal work presents unique and significant challenges, leading to considerable controversy:

1. **The Impossibility of Universal Legal Benchmarking:** Law is not monolithic. It varies across jurisdictions, languages, and cultures, involving nuanced interpretations and subjective outcomes. Attempting to create a single, universal benchmark for legal proficiency risks oversimplifying complex local specificities and may be influenced by commercial interests rather than genuine legal diversity. Courts and judges exist precisely because legal outcomes are often debatable and context-dependent.  
2. **Lack of Generalizable Infrastructure:** The global legal AI community currently lacks a unified entity to build truly general legal AI systems that function effectively across all languages and cultures. Development is often concentrated in specific hubs (e.g., London, New York, San Francisco), whose perspectives and priorities may not align with grassroots legal needs globally.  
3. **Lack of Unity on Challenges:** There is insufficient consensus within the legal AI community regarding the fundamental difficulties outlined above. This hinders collaborative progress toward genuinely applicable and safe legal AI.  
4. **Objective vs. Subjective Tasks:** Unlike math or coding, where benchmarks can rely on objectively verifiable results, legal work often involves interpreting illogical or conflicting laws and constructing arguments based on subjective factors. Current LLM benchmarks focusing on logic or games demonstrate AI intelligence but lack practical relevance for many core legal tasks. Furthermore, AI struggles with the subjectivity inherent in law, similar to its challenges with nuanced human expression, such as high-level comedy.  
5. **The Proficiency “Arms Race”:** Testing LLMs for proficiency on complex tasks creates a scenario where AI developers inevitably “teach to the test.” This leads to an asymmetry where AI systems, through targeted training on specific tests, can develop apparent proficiency that masks underlying deficiencies, as any test can eventually be mastered.

# 3\. The L3 Methodology

Acknowledging these challenges, the S3 framework offers a pragmatic and transparent approach focused on essential, measurable outputs:

**Core Focus:** The benchmark verifies whether a raw instruct model’s outputs are sufficiently reliable for basic legal support tasks, primarily targeting the capabilities needed by application layers like Retrieval-Augmented Generation (RAG).

**The “S3” Pillars:**

* **Accurate Code & Case Law References:** Does the model correctly identify and cite relevant legal articles and case law? (Measurable: Yes/No)  
* **Recency:** Does the model possess knowledge of recent legal developments? (Measurable against known timelines)  
* **Consistency:** Can the model consistently follow specific instructions for objective tasks, such as verifying references multiple times? (Measurable via repeated prompts)

**Why These Pillars?** These elements are crucial for legal accuracy, have objectively measurable outcomes that anyone can test, and target known LLM weaknesses (hallucination, knowledge cutoffs). Their random nature makes them harder to “game” through training compared to subjective tasks.

**Scope:**

* **Instruct Models:** Tests focus on instruct-tuned models (using zero-shot prompts), as these are most commonly deployed in production, rather than base models.  
* **Exclusion of Subjective Tasks:** Summarization, drafting, and complex legal reasoning are not tested. These outputs are highly subjective, difficult to measure objectively, depend heavily on variable inputs, and are easily gamed via specific RLHF (Reinforcement Learning from Human Feedback). The goal is objective measurement, not evaluation of stylistic or argumentative quality.  
* **Civil Law Focus (Initial):** The initial framework emphasizes civil law systems, where finding measurable outcomes linked to codified statutes is often more straightforward than in common law systems, where precedent and interpretation introduce more ambiguity for benchmarking.

**Framework Goal:** To provide a simple, transparent framework allowing any jurisdiction or legal professional to create custom benchmarks while maintaining consistent evaluation principles focused on foundational LLM deficiencies.

# 4\. Rationale and Background

The S3 evaluation originated from practical needs during the development of Sabaio OI. Calibrating and comparing the performance of different open-source models required a consistent method to determine if newer models offered tangible improvements over older ones in core reliability.

It serves as a counterpoint to prevailing benchmark trends that focus on mimicking human cognitive tests or complex, subjective tasks. The legal industry often thrives on complexity, but foundational AI reliability requires a focus on simple, verifiable truths. The benchmark also critiques the tendency for legal tech development to be overly influenced by major Anglophone hubs, potentially neglecting the localized nature of law.

Furthermore, the benchmark acknowledges that many real-world legal tasks require access to proprietary or personal data (e.g., S1 filings, tax data) provided only at inference time. This data cannot be part of training, highlighting the importance of reliable raw model outputs before such data is processed.

# 5\. Frequently Asked Questions (FAQ)

* **Why only test instruct models?**These are the models most frequently deployed in production applications. Base models typically lack the necessary RLHF for consistent instruction following.  
* **Why focus benchmarking on civil law systems initially?**Codified systems make it easier to establish objectively measurable outcomes (e.g., tracing a decision to a specific legislative rule). While common law has traceable attributes, outcomes can be more open to debate, complicating objective benchmarking.  
* **Why not test summarizing, drafting, etc.?**The core premise is objective measurable outcomes. Summaries and drafts are subjective and open to multiple valid interpretations. Standardizing inputs (e.g., the exact document for summarization) across all tests is also challenging.  
* **Why not offer legal reasoning tests?**Similar to summarizing/drafting, reasoning involves subjective interpretation rather than easily measurable outcomes. Furthermore, reasoning tests can be “gamed” with specific RL training (“studying to the test”), undermining the goal of assessing inherent model capabilities.  
* **Do these tests work on cloud or closed-source models?**Yes, the methodology can be applied via API access (assuming no additional system prompts interfere). However, comparing results directly with open-source models may be difficult (“apples to oranges”) due to potential provider censorship or hidden system prompts influencing outputs.  
* **Can I use these tests on my vendor’s AI product?**No, the tests are designed to measure the performance of raw instruct models, not layered AI applications or vendor platforms. For vendor comparisons, a Chatbot Arena-style evaluation might be more appropriate, although vendor participation is unlikely. Factors like proprietary system prompts and fine-tuning in vendor products make direct comparison using this benchmark unsuitable.  
* **Do the tests measure AI response time?**No. Inference speed depends on model size, parameters, and hardware (GPU speed)—these are infrastructure variables, not consistent indicators of a model’s inherent legal knowledge accuracy or recency.  
* **Will this framework be updated?**Updates are planned but do not have a set timeline. This framework was developed as part of a larger initiative to donate assets to the legal community associated with the closing of sabaio.com operations.

# 6\. Prompt Template

To ensure the benchmark can be recreated and applied consistently across different programming languages, we define a standardized prompt template for querying legal concepts. This template provides a clear structure for formulating questions about specific legal topics within a given jurisdiction. The structure is as follows:

“In \[Jurisdiction\], is ‘\[Code name\] \[Reference type\] \[Number\]’ the correct reference for ‘\[Subject \- Topic\]’?”

Each component of this template serves a specific purpose:

* **\[Jurisdiction\]:** Specifies the legal system or geographical area relevant to the query (e.g., “Dutch Law,” “the State of California,” “European Union Regulations”).  
* **”\[Code name\] \[Reference type\] \[Pre-Number\] \[Offset N1\]\[N2\] \[Sub\]”:** The structured legal reference being evaluated, comprising:  
  * **\[Code name\]:** The official or common name of the legal document (e.g., “Algemene Wet inzake Rijksbelastingen,” “Civil Code,” “GDPR”).  
  * **\[Reference type\]:** The specific type of legal reference within the code (e.g., “artikel” (article), “section,” “paragraph,” “directive”).  
  * **\[Number\]:** An optional prefix or initial number indicating a broader division within the code (e.g., “Boek” (Book) followed by a number).  
  * **\[Offset N1\]:** The primary identifying number of the specific reference (e.g., “31”).  
  * **\[N2\]:** A secondary identifier (number or letter) for further specificity within \[Offset N1\] (e.g., “g”).  
  * **\[Sub\]:** An optional sub-level identifier like a paragraph or subsection (e.g., “lid 1” (paragraph 1), “sub a”).  
* **”\[Subject \- Topic\]”:** Clearly states the legal concept being inquired about (e.g., “Belastingrente” (Tax Interest), “Data Protection,” “Contract Formation”).

**Example:**

A query about the legal reference for “Belastingrente” in Dutch Law would be:

“In Dutch Law, is ‘Burgerlijk Wetboek Boek 7 artikel 675’ the correct reference for ‘Wanprestatie’? Answer True/False with a 20-word explanation as to why.”

This prompt ensures clarity and allows for systematic evaluation of whether a given legal citation accurately corresponds to a specific legal concept. By adhering to this template, researchers and practitioners can consistently generate benchmark queries across languages and legal domains, facilitating comparable and reproducible results.

# 7\. Validation and Evaluation

For this framework, we use a straightforward quantitative approach: counting the number of correct answers provided by the model. Each benchmark consists of a fixed set of queries, and the model’s performance is reported as a simple ratio (e.g., 12/12). This method offers clear, objective measurement and facilitates easy comparison across models and test runs. It also ensures transparency and reproducibility, as results can be independently verified by re-running the same set of queries.

A video demonstration is available here: [How good is DeepSeek R1-0528 for legal work? ↗](https://www.linkedin.com/posts/raymondblijd_how-good-is-deepseek-r1-0528-for-legal-work-activity-7334949353356251136-CWkB) 

# 8\. Conclusion

The Legal LLM Evaluation Framework offers a focused, pragmatic, and transparent alternative to conventional legal AI evaluation. By concentrating on fundamental deficiencies—accuracy in citations, recency of knowledge, and consistency in following instructions—it provides a necessary foundation for assessing the reliability of LLMs for basic legal tasks. This framework encourages verifying objective, measurable outputs before tackling more complex, subjective legal capabilities, promoting a more grounded and cautious approach to integrating AI in the legal domain.
