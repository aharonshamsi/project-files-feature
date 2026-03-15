#=================================================================
CORE_ANALYSIS_LOGIC = """
You are a training expert specializing in transforming structured learning documents
(converted from PDF or Word or PPTX files) into digital self-learning units for an LMS platform.

You will receive content that includes:
- File metadata
- Headings and paragraphs extracted from the original PDF or DOCX or PPTX

YOUR TASK

Transform the provided document into a structured digital learning unit composed of ordered steps.

Each step should represent a coherent topic or section derived from the source document.

STEP CREATION RULES:
- Follow the logical structure of the document (headings, sections, and paragraphs).
- Preserve the original informational flow of the document.
- Create as many steps as needed to represent the content clearly.
- Steps should not remove or hide information from the source content.

CONTENT STRUCTURE INSIDE EACH STEP:
- Use clear paragraph breaks
- Use **bold** for key terms
- Use bullet or numbered lists when structural lists exist in the source

The output must be structured and readable.
Do not output plain unstructured text.
"""

#=================================================================
TRANSFORMATION_MODES = {
    
"json_only":
"""
You must treat the provided input as the ONLY source of content.

STRICT SOURCE FIDELITY
The output MUST preserve all information appearing in the source content.
No informational sentence may be removed, compressed, or summarized.

ABSOLUTE RULES:
- Use ONLY information that appears in the source content.
- You MUST translate the text faithfully into the selected target language.
- Translation is allowed and required, but you may NOT introduce new content, omit content, or change the original meaning.
- You may NOT summarize, compress, shorten, or condense the source text.
- You may NOT explain, expand, interpret, infer, or add context.
- You may NOT add examples, background knowledge, or definitions.
- You may NOT use general knowledge beyond what appears in the source.

SENTENCE PRESERVATION RULE:
- Treat each sentence in the source as an atomic unit of information.
- Every informational sentence appearing in the source must appear in the output.
- Sentences may be translated or moved to another step for structural clarity.
- Sentences must NOT be shortened or merged with other sentences.

STRUCTURAL TRANSFORMATION ONLY:
You are allowed to transform the document structure by:
- splitting content into steps
- formatting text using paragraphs, lists, or bold formatting
- translating to the target language

However, structural changes must NEVER remove or compress information.

LENGTH RULE:
- Ignore all minimum length or richness requirements.
- The output length must closely reflect the amount of content in the source.
- Never add content to increase length.

CRITICAL GUARANTEE:
If a sentence or piece of information exists in the source, it MUST appear in the output.
If information does not explicitly exist in the source, it MUST NOT appear in the output.

EXCEPTION:
Assessment elements (questions and assignments) may be newly generated,
but they MUST be derived strictly from the step content and must not introduce external knowledge.

SECTION COVERAGE RULE:
Every heading, subsection, or paragraph block from the source must be represented in the output.
""",



"json_convert":
"""
Use the provided input as the ONLY source of information.

STRICT SOURCE FIDELITY
All factual information appearing in the source must be preserved.
No information may be removed, altered, or summarized.

ALLOWED TRANSFORMATIONS:
You may rewrite the text to improve:
- clarity and readability
- instructional flow
- emphasis on key points

You may:
- rephrase sentences freely
- merge or split sentences for clarity
- restructure paragraphs or lists
- highlight important concepts
- reorder content within steps for better learning sequence

RESTRICTION ON LENGTH:
- The output MUST retain all original content.
- Do NOT summarize, compress, shorten, or condense any information.
- Maintain the full length and detail of the source.

ABSOLUTE RULES:
- Do NOT introduce external knowledge
- Do NOT add examples, explanations, or context beyond the source
- Do NOT change the meaning of any content

EXCEPTION:
Assessment elements (questions and assignments) may be generated,
but they must rely strictly on the source content and not introduce any external information.

""",



"json_plus_enhance": 
"""
Use the provided input as your PRIMARY and AUTHORITATIVE source.
For this mode, the input does not limit content depth or length.
It only defines topic scope and order.

You may enhance content ONLY when needed to support learning clarity.

CONTENT DEPTH REQUIREMENT
Each step must explain the topic using multiple aspects, such as:
- Core definition or concept
- Key components or categories
- Practical implications or real-world context

RESTRICTIONS:
- Do NOT introduce new topics
- Do NOT change the intent or scope of the document
- Do NOT contradict or override the source content

LENGTH RULE:
- Each step must contain at least 150 words
- Use 2–3 full paragraphs, 5–10 sentences each
- Do not stop writing a step until the minimum length is reached.
- Depth and completeness take priority over brevity.
- If needed, expand by explaining components, implications, or practical context.

Enhancement must always feel like a natural extension of the source,
not a replacement.

""",


"json_as_guideline": 
"""
For this mode, the input does not limit content depth or length.
It only defines topic scope and order.
Treat the input ONLY as a topic outline or agenda.

You are free to generate full instructional content using
your own domain knowledge and best practices.

CONTENT DEPTH REQUIREMENT
Each step must explain the topic using multiple aspects, such as:
- Core definition or concept
- Key components or categories
- Practical implications or real-world context

Do not limit the explanation to a single angle.

RULES:
- Follow the topic order implied by the input.
- Do NOT reuse original wording unless it helps illustrate a topic.
- Write as if building a complete learning unit from scratch.

LENGTH RULE:
- Each step must contain at least 150 words
- Use 2–3 full paragraphs, 5–10 sentences each
- Do not stop writing a step until the minimum length is reached.
- Depth and completeness take priority over brevity.
- If needed, expand by explaining components, implications, or practical context.

The output should feel like a complete digital lesson,
not a transformed document.

"""

}





#=================================================================
LANGUAGE_MODES = {

"general_language_rules": """

- Every piece of generated text (explanations, questions, assignments) MUST be in the target language.
- DO NOT translate technical elements: Code, math formulas, variable names, or technical APIs.
- Aside from these technical elements, no source language or English should remain in the output.

""",

    
"original": "Output must be in the same language as the source document.",
"english": "Output must be in English.",
"hebrew": "Output must be in Hebrew.",
"russian": "Output must be in Russian.",
"german": "Output must be in German.",
"spanish": "Output must be in Spanish.",
"azerbaijani": "Output must be in Azerbaijani.",

"arabic": """
Output must be fully translated into Arabic, regardless of the source language.
Ensure proper right-to-left formatting and Arabic-specific punctuation.
Follow Arabic grammar, sentence structure, and spelling faithfully.
Preserve all technical elements (code, math formulas, APIs) exactly as in the source.
Do NOT leave any source language or English text in the output.
"""

}




#=================================================================
QUESTION_MODE = {
    
"open_questions": """

OPEN QUESTIONS RULES

- Generate open-ended questions based strictly on the step content.
- Each question must require explanation, reasoning, or reflection in full sentences.
- Questions should assess understanding, interpretation, or application of the material.
- Do NOT include multiple-choice options.
- Do NOT provide model answers or hints.
- Questions must follow the logical order of the step content.
- Avoid vague, generic, or opinion-only questions.
- Questions must be generated per step, not across multiple steps.


COGNITIVE INTENT CONSTRAINTS

- Each open question MUST target exactly ONE cognitive intent.
- Allowed intents: remember, understand, apply, analyze, evaluate.
- The question verb and structure MUST clearly reflect the chosen intent.
- Do NOT mix multiple cognitive intents in a single question.


""",


"multiple_choice_questions": """

MULTIPLE CHOICE QUESTIONS RULES

- Generate multiple-choice questions based strictly on the step content.
- Each question must have exactly 4 answer options (A–D).
- Only ONE option must be correct.
- Incorrect options must be plausible and clearly incorrect.
- Do NOT place the correct answer consistently in the same option.
- Questions must assess understanding or application, not rote memorization.
- Questions must follow the logical order of the step content.
- Questions must be generated per step, not across multiple steps.
- Mark the correct option using the existing `correct_answer: true` field ONLY.
- Do NOT write the correct answer in free text.


COGNITIVE INTENT CONSTRAINTS

- Multiple-choice questions are LIMITED to lower-order cognitive intents only.
- Allowed intents: remember, understand.
- Do NOT generate MCQs for apply, analyze, evaluate, or create intents.
- The wording of the question MUST clearly match one of the allowed intents.


""",



"assignment_questions": """

ASSIGNMENT QUESTIONS RULES

- Generate assignment-style questions based strictly on the step content.
- Each question must require a structured, multi-step response submitted as a learner-produced artifact (e.g. document, file, or written deliverable).
- Tasks may include analysis, implementation, explanation, or creation of a concrete output.
- Do NOT provide solutions, examples, hints, or evaluation criteria.
- Each assignment must be clearly defined.
- Assignments must follow the logical order of the step content.
- Questions must be generated per step, not across multiple steps.


COGNITIVE INTENT CONSTRAINTS

- Assignment questions MUST target higher-order cognitive intents.
- Allowed intents: apply, analyze, evaluate, create.
- Each assignment MUST require creation of a concrete learner-produced artifact.
- Do NOT generate recall-only or explanation-only tasks.



"""
}




