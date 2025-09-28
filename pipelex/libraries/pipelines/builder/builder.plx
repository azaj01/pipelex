domain = "builder"
definition = "Auto-generate a Pipelex bundle (concepts + pipes) from a short user brief."

[concept]
UserBrief = "A short, natural-language description of what the user wants."
PlanDraft = "Natural-language pipeline plan text describing sequences, inputs, outputs."
ConceptDrafts = "Textual representation of the concepts to create."
PipelexBundleSpec = "A Pipelex bundle spec."
PipeFailure = "Details of a single pipe failure during dry run."
DryRunResult = "A result of a dry run of a pipelex bundle spec."
DomainInformation = "A domain information object."

# ────────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────────
[pipe]
[pipe.pipe_builder]
type = "PipeSequence"
description = "This pipe is going to be the entry point for the builder. It will take a UserBrief and return a PipelexBundleSpec."
inputs = { brief = "UserBrief" }
output = "Dynamic"
steps = [
    { pipe = "draft_planning_text", result = "plan_draft" },
    { pipe = "draft_to_conceptspecs_text", result = "concept_spec_drafts_text" },
    # { pipe = "draft_to_pipesignatures_text", result = "pipe_signatures_text" },
    # { pipe = "materialize_concept_spec_drafts", result = "concept_spec_drafts" },
    # { pipe = "materialize_pipe_signatures", result = "pipe_signatures" },
    # { pipe = "pipe_builder_domain_information", result = "domain_information" },
    # { pipe = "build_concept_spec", batch_over = "concept_spec_drafts", batch_as = "concept_spec_draft", result = "concept_specs" },
    # { pipe = "create_pipes_from_signatures", batch_over = "pipe_signatures", batch_as = "pipe_signature", result = "pipe_specs" },
    # { pipe = "compile_in_pipelex_bundle_spec", result = "pipelex_bundle_spec" }
    # { pipe = "validate_pipelex_bundle_spec", result = "pipelex_bundle_spec" }
]

[pipe.pipe_builder_domain_information]
type = "PipeLLM"
description = "Turn the brief into a DomainInformation object."
inputs = { brief = "UserBrief" }
output = "DomainInformation"
prompt_template = """
Based on the brief output the "domain" of this pipe, and a definition of what it would represent.

Brief:
@brief

For example, if the pipe is about generating a compliance matrix out of a RFP, the domain would be "rfp_compliance_matrix"...
It should be not more than 4 words, in snake_case.
For the definition, i would like to see a short description of what the bundle would represent.
"""

# ────────────────────────────────────────────────────────────────────────────────
# STAGE 1 — plan (natural language pseudo-code, but explicit about IO + sequencing)
# ────────────────────────────────────────────────────────────────────────────────

[pipe.draft_planning_text]
type = "PipeLLM"
description = "Turn the brief into a pseudo-code plan describing controllers, pipes, their inputs/outputs."
inputs = { brief = "UserBrief" }
output = "PlanDraft"
llm = "llm_to_engineer"
prompt_template = """
Return a draft of a plan that narrates the pipeline as pseudo-steps (no code):
- Explicitly indicate when you are running things in sequence,
  or in parallel (several independant steps in parallel),
  or in batch (same operation applied to N elements of a list)
  or based on a condition
- For each pipe: state the pipe's description, inputs (by name), and the output (by name), DO NOT indicate the inputs or output type. Just name them.
- Be aware of the steps where you want structures: either structured objects as outputs or inputs. Make sense of it but be concise.

Available pipe controllers:
- PipeSequence: A pipe that executes a sequence of pipes: it needs to reference the pipes it will execute.
- PipeParallel: A pipe that executes a few pipes in parallel. It needs to reference the pipes it will execute.
  The results of each pipe will be in the working memory. The output MUST BE "Dynamic".
- PipeCondition: A pipe that based on a conditional expression, branches to a specific pipe.
  You have to explain what the expression of the condition is,
  and what the different pipes are that can be executed based on the condition.
  It needs to reference the pipes it will execute.

When describing the task of a pipe controller, be concise, don't detail all the sub-pipes.

Available pipe operators:
- PipeLLM: A pipe that uses an LLM to generate a text, or a structured object. It is a vision LLM so it can also use images.
  CRITICAL: When extracting MULTIPLE items (articles, employees, products), use multiple_output = true with SINGULAR concepts!
  - Create concept "Article" (not "Articles") with fields "item_name", "quantity" (not "item_names", "quantities")
  - Then set multiple_output = true to get a list of Article objects
- PipeImgGen: A pipe that uses an AI model to generate an image.
  VERY IMPORTANT: IF YOU DECIDE TO CREATE A PipeImgGen, YOU ALSO HAVE TO CREATE A PIPELLM THAT WILL WRITE THE PROMPT, AND THAT NEEDS TO PRECEED THE PIPEIMGEN, based on the necessary elements.
  That means that in the MAIN pipeline, the prompt MUST NOT be considered as an input. It should be the output of a step that generates the prompt.
- PipeOcr: A pipe that uses an OCR technology to extract text from an image or a pdf.
  VERY IMPORTANT: THE INPUT OF THE PIPEOCR MUST BE either an image or a pdf or a concept which refines one of them.
- PipeCompose: A pipe that uses Jinja2 to render a template.

Keep your style concise, no need to write tags such as "Description:", just write what you need to write.

@brief
"""

# ────────────────────────────────────────────────────────────────────────────────
# STAGE 2 — textual specs (still TEXT, not structured objects yet)
# ────────────────────────────────────────────────────────────────────────────────
[pipe.draft_to_conceptspecs_text]
type = "PipeLLM"
description = "Interpret the draft of a plan to create an AI pipeline, and define the needed concepts."
inputs = { plan_draft = "PlanDraft", brief = "UserBrief" }
output = "ConceptDrafts"
llm = "llm_to_engineer"
prompt_template = """
We are working on writing an AI pipeleine to answer this brief:
@brief

We have already written a plan for the pipeline. It's built using pipes, each with its own inputs (one or more) and output (single).
Variables are snake_case and concepts are PascalCase.

Your job is to clarify the different concepts used in the plan.
We want clear concepts but we don't want  too many concepts. If a concept can be reused in the pipeline, it's the same concept.
For instance:
- If you have a "FlowerDescription" concept, then it can be used for rose_description, tulip_description, beautiful_flower_description, dead_flower_description, etc.
- DO NOT define concepts that include adjectives: "LongArticle" is wrong, "Article" is right.
- DO NOT include circumstances in the concept definition:
  "ArticleAboutApple" is wrong, "Article" is right.
  "CounterArgument" is wrong, "Argument" is right.
- Concepts are always expressed as singular nouns, even if we're to use them as a list:
  for instance, define the concept as "Article" not "Articles", "Employee" not "Employees".
  If we need multiple items, we'll indicate it elsewhere so you don't bother with it here.
- Provide a short description concise description for each concept

If the concept can be expressed as a text, image, pdf, number, or page:
- Name the concept, define it and just write "refines: Text", "refines: PDF", or "refines: Image" etc.
- No need to define its structure
Else, if you need structure for your concept, draft its structure:
- field name in snake_case
- definition:
  - definition: the definition of the field, in natural language
  - type: the type of the field (text, integer,boolean, number, date)
  - required: add required = true if the field is required (otherwise, leave it empty)
  - default_value: the default value of the field

DO NOT redefine native concepts such as: Text, Image, PDF, Number, Page. if you need one of these, they already exist so you should NOT REDEFINE THEM.

@plan_draft
"""

[pipe.draft_to_pipesignatures_text]
type = "PipeLLM"
description = "Write the pipe signatures for the plan."
inputs = { plan_draft = "PlanDraft", brief = "UserBrief" }
output = "Text"
llm = "llm_to_engineer"
prompt_template = """
Return PipeSignaturesText listing every pipe to build:
- For each pipe: give a unique snake_case pipe_code, type, definition, inputs (by concept code/name), output, and important_features
- Controller pipes must reference children by their codes consistently
- The Pipe Controllers, if they mention pipes, they should always mention existing pipes.
- Add as much details as possible for the description.

Here are the ESSENTIAL features for each pipe type that should be included in important_features (only include these key ones):

**PipeLLM**: A pipe that uses an LLM to generate a text, or a structured object. It is a vision LLM that can read images.
The inputs of the PipeLLM should be:
The variables tagged in the prompt template (with $ or @). If there are no variables, the inputs should be empty.
The ouput should be the concept code of the output
- prompt_template: The prompt template with variable substitution ($ for inline, @ for blocks)
- multiple_output: true if generating multiple number of outputs: That means it will output a LIST of the CONCEPT!

CRITICAL RULE FOR PIPELLM:
- If extracting MULTIPLE items (like multiple articles, employees, products), use multiple_output = true
- The concept should represent ONE SINGLE item (Article, Employee, Product)
- DO NOT create concepts with plural field names like "item_names", "quantities"
- Instead: use multiple_output = true with singular concept fields like "item_name", "quantity"
- Example: To extract multiple articles, create concept "Article" with fields "item_name", "quantity", then use multiple_output = true

**PipeSequence**: A pipe that executes a sequence of pipes: It needs to reference the pipes it will execute.
The inputs of the PipeSequence should be all the necessary inputs in the below steps, and the inputs that are NOT generated by intermediate steps.
The output should be the concept code of the output of the last step.
- steps: List of pipe codes to execute in order, with result names
- Each step format: {"pipe": "pipe_code", "result": "result_name"}
- Can include batch operations: {"pipe": "pipe_code", "batch_over": "list_input", "batch_as": "item_name", "result": "result_name"}

**PipeParallel**: A pipe that executes a few pipes in parallel. It needs to reference the pipes it will execute.
The inputs of the PipeParallel should be all the necessary inputs in the below steps
The output should be the concept code of the output of the last step.
The results of each pipe will be in the working memory.
- parallels: List of pipes to execute in parallel
- Each parallel format: {"pipe": "pipe_code", "result": "result_name"}

**PipeCondition**: A pipe that based on a specific condition, branches to a specific pipe. You have to explain what the expression of the condition is,
    and what the different pipes are that can be executed based on the condition. It needs to reference the pipes it will execute.
The inputs of the PipeCondition should be all the necessary inputs in the below steps
The output should be the concept code of the output of all the steps, except if the outputs are different, then its "Dynamic"
- expression: Direct expression to evaluate (e.g., "task_result.status")
- pipe_map: Dictionary mapping condition results to pipe codes (e.g., {"completed": "success_pipe", "failed": "failure_pipe"})
- default_pipe_code: Fallback pipe when no conditions match

**PipeBatch**: A pipe that executes a batch of pipes in parallel. It needs to reference the pipe it will execute.
- branch_pipe_code: The pipe code to execute for each item
- input_list_name: Name of the list to iterate over
- input_item_name: Name for individual items within each execution

**PipeImgGen**: A pipe that uses an LLM to generate an image.
The inputs of the PipeImgGen should be: {prompt: ImgGenPrompt}
The output should be the concept code that refines Image.
- img_gen_prompt: Static prompt for image generation (if using static prompt)
- nb_output: Number of images to generate (default 1)
VERY IMPORTANT: IF YOU DECIDE TO CREATE A PIPEIMGEN, YOU ALSO HAVE TO CREATE A PIPELLM THAT WILL WRITE THE PROMPT, AND THAT NEEDS TO PRECEED THE PIPEIMGEN, based on the necessary elements.
THERFORE, the OUTPUT OF THIS PIPELLM should be a VARIABLE NAMED "prompt" that will be used as input for the PipeImgGen.
That means that in the MAIN pipeline, the prompt should NOT be an input. It should be a step that generates the prompt.

**PipeOcr**: A pipe that uses an LLM to extract text from an image.
- The INPUTS of PipeOcr must be either an image or a pdf or a concept which refines one of them.

**PipeFunc**: A pipe that executes a custom Python function.
- function_name: Name of the Python function to call

**PipeCompose**: A pipe that uses Jinja2 to render a template.
- jinja2: Raw Jinja2 template string OR
- jinja2_name: Name reference to a template (use one or the other)

Plan:
@plan_draft

Brief:
@brief

No more than 10 PipeSignatures
"""

# ────────────────────────────────────────────────────────────────────────────────
# STAGE 3 — materialize: TEXT → real objects (ConceptSpec[], PipeSignature[])
# ────────────────────────────────────────────────────────────────────────────────

[pipe.materialize_concept_spec_drafts]
type = "PipeLLM"
description = "Turn ConceptSpecsText into ConceptSpec objects."
inputs = { concept_spec_drafts_text = "Text", brief = "UserBrief" }
output = "concept.ConceptSpecDraft"
multiple_output = true
llm = "llm_to_engineer"
prompt_template = """
Materialize ConceptSpec objects from the ConceptSpecsText.
Do not change the information in the input. Just organize the information

ConceptSpecs:
@concept_spec_drafts_text

Brief:
@brief

LIMIT TO A MAXIMUM OF 5 fields for now
"""

[pipe.materialize_pipe_signatures]
type = "PipeLLM"
description = "Turn PipeSignaturesText into PipeSignature objects that reference the ConceptSpec objects."
inputs = { pipe_signatures_text = "Text", concept_spec_drafts = "concept.ConceptSpecDraft", brief = "UserBrief" }
output = "pipe.PipeSignature"
multiple_output = true
llm = "llm_to_engineer"
prompt_template = """
Materialize PipeSignature objects from the PipeSignaturesText.
- pipe_code MUST be snake_case
- inputs must be a Dict[str, ConceptSpecDraft] referencing the provided ConceptSpecDraft objects. If Its the concept itself, use the concept code in PascalCase.
- output must be a ConceptSpec from the provided set. If Its the concept itself, use the concept code in PascalCase.
- important_features must be a Dict containing the pipe-specific features mentioned in the text

VERY IMPORTANT: A pipe has inputs, and an output. The inputs are a dict of keys in snake_case, corresponding to the variables names in the working memory, and the values are the concept codes in PascalCase.
The output is a concept code in PascalCase.
The field "result" is corresponding to the name of the result of the pipe. It will be used in the inputs of the next pipes.
It is important that they link each other in the right way.

The output concept should be a concepts should be in PascalCase

IMPORTANT:
- THE MAIN PIPE SHOULD CONTAIN IN ITS NAME "main_pipeline"
- IF THERE IS A PipeIMG, VERIFIES THAT THE INPUT PROMPT IS ACTUALLY GENERATED BY A PIPELLM BEFORE THE PIPEIMG.
THIS PIPELLM SHOULD NAME THE RESULT OF ITS PIPE "prompt".

PipeSignatures:
@pipe_signatures_text

ConceptSpecDrafts:
@concept_spec_drafts

Brief:
@brief

No more than 10 PipeSignatures
"""

[pipe.compile_in_pipelex_bundle_spec]
type = "PipeFunc"
description = "Compile the pipelex bundle spec."
inputs = { pipe_specs = "PipeSpec", concept_specs = "ConceptSpec" }
output = "PipelexBundleSpec"
function_name = "compile_in_pipelex_bundle_spec"

[pipe.validate_pipelex_bundle_spec]
type = "PipeSequence"
description = "Validate the pipelex bundle spec with iterative fixing."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec" }
output = "PipelexBundleSpec"
steps = [
    { pipe = "validate_dry_run", result = "failed_pipes" },
    { pipe = "check_validation_status", result = "validation_status" },
    { pipe = "handle_validation_result", result = "pipelex_bundle_spec" }
]

[pipe.check_validation_status]
type = "PipeCompose"
description = "Check if validation failed by examining if failed_pipes list is empty."
inputs = { failed_pipes = "PipeFailure" }
output = "Text"
jinja2 = "{% if failed_pipes.content.items|length > 0 %}FAILURE{% else %}SUCCESS{% endif %}"

[pipe.handle_validation_result]
type = "PipeCondition"
description = "Handle validation result - continue if success or fix failures once."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec", failed_pipes = "PipeFailure", validation_status = "Text" }
output = "PipelexBundleSpec"
expression = "validation_status.text"

[pipe.handle_validation_result.pipe_map]
SUCCESS = "continue"
FAILURE = "fix_failing_pipes_once"

[pipe.fix_failing_pipes_once]
type = "PipeSequence"
description = "Fix failing pipes once and return the result."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec", failed_pipes = "PipeFailure" }
output = "PipelexBundleSpec"
steps = [
    { pipe = "fix_failing_pipe", batch_over = "failed_pipes", batch_as = "failed_pipe", result = "fixed_pipes" },
    { pipe = "reconstruct_bundle_with_all_fixes", result = "pipelex_bundle_spec" },
    { pipe = "validate_pipelex_bundle_spec", result = "pipelex_bundle_spec" }
]

[pipe.validate_dry_run]
type = "PipeFunc"
description = "Validate the pipelex bundle spec and return only failed pipes."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec" }
output = "PipeFailure"
function_name = "validate_dry_run"

[pipe.continue]
type = "PipeCompose"
description = "Continue with successful validation - return the bundle unchanged."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec" }
output = "PipelexBundleSpec"
jinja2 = "{{ pipelex_bundle_spec }}"

[pipe.reconstruct_bundle_with_all_fixes]
type = "PipeFunc"
description = "Reconstruct the bundle spec with all the fixed pipes."
inputs = { pipelex_bundle_spec = "PipelexBundleSpec", fixed_pipes = "Dynamic" }
output = "PipelexBundleSpec"
function_name = "reconstruct_bundle_with_all_fixes"

