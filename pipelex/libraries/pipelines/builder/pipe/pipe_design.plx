domain = "pipe_design"
definition = "Build and process pipes."

[concept]
PipeSignature = "A pipe contract which says what the pipe does, not how it does it: code (the pipe code in snake_case), type, description, inputs, output."
PipeSpec = "A structured spec for a pipe (union)."
# Pipe controllers
PipeBatchSpec = "A structured spec for a pipe batch."
PipeConditionSpec = "A structured spec for a pipe condition."
PipeParallelSpec = "A structured spec for a pipe parallel."
PipeSequenceSpec = "A structured spec for a pipe sequence."
# Pipe operators
PipeFuncSpec = "A structured spec for a pipe func."
PipeImgGenSpec = "A structured spec for a pipe img gen."
PipeComposeSpec = "A structured spec for a pipe jinja2."
PipeLLMSpec = "A structured spec for a pipe llm."
PipeOcrSpec = "A structured spec for a pipe ocr."
PipeFailure = "Details of a single pipe failure during dry run."

[pipe]

[pipe.detail_pipe_spec]
type = "PipeCondition"
description = "Route by signature.type to the correct spec emitter."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "ConceptSpec" }
output = "Dynamic"
expression = "pipe_signature.type"

[pipe.detail_pipe_spec.pipe_map]
PipeSequence  = "detail_pipe_sequence"
PipeParallel  = "detail_pipe_parallel"
PipeCondition = "detail_pipe_condition"
PipeLLM       = "detail_pipe_llm"
PipeOcr       = "detail_pipe_ocr"
PipeImgGen    = "detail_pipe_img_gen"
PipeCompose   = "detail_pipe_compose"

# ────────────────────────────────────────────────────────────────────────────────
# PIPE CONTROLLERS
# ────────────────────────────────────────────────────────────────────────────────

[pipe.detail_pipe_sequence]
type = "PipeLLM"
description = "Build a PipeSequenceSpec from the signature (children referenced by code)."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeSequenceSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeSequenceSpec to orchestrate a sequence of pipe steps that will run one after the other.

This PipeSequence is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeSequence related to this signature:
@pipe_signature
"""

[pipe.detail_pipe_parallel]
type = "PipeLLM"
description = "Build a PipeParallelSpec from the signature."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeParallelSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeParallelSpec to orchestrate a bunch of pipe steps that will run in parallel.

This PipeParallel is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeParallel related to this signature:
@pipe_signature
"""

[pipe.detail_pipe_condition]
type = "PipeLLM"
description = "Build a PipeConditionSpec from the signature (provide expression/pipe_map consistent with children)."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeConditionSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeConditionSpec to route to the correct pipe step based on a conditional expression.

This PipeCondition is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeCondition related to this signature:
@pipe_signature
"""

# ────────────────────────────────────────────────────────────────────────────────
# PIPE OPERATORS
# ────────────────────────────────────────────────────────────────────────────────

[pipe.detail_pipe_llm]
type = "PipeLLM"
description = "Build a PipeLLMSpec from the signature."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeLLMSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeLLMSpec to use an LLM to generate a text, or a structured object using different kinds of inputs.
Whatever it's really going to do has already been decided, as you can see:

This PipeLLM is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeLLM related to this signature:
@pipe_signature

If it's a structured generation, indicate it in the system_prompt to clarify the task.
If it's to generate free form text, the prompt_template should indicate to be concise.
If it's to generate an image generation, the prompt_template should indicate to be VERY concise and focus and apply the best practice for image generation.
"""

[pipe.detail_pipe_ocr]
type = "PipeLLM"
description = "Build a PipeOcrSpec from the signature."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeOcrSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeOcrSpec to extract text from an image or a pdf.

This PipeOcr is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeOcr related to this signature:
@pipe_signature
"""

[pipe.detail_pipe_img_gen]
type = "PipeLLM"
description = "Build a PipeImgGenSpec from the signature."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeImgGenSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeImgGenSpec to generate an image from a text prompt.

This PipeImgGen is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeImgGen related to this signature:
@pipe_signature

The inputs for the image has to be a single input which must be a Text or another concept which refines Text.
"""

[pipe.detail_pipe_compose]
type = "PipeLLM"
description = "Build a PipeComposeSpec from the signature."
inputs = { plan_draft = "PlanDraft", pipe_signature = "PipeSignature", concept_specs = "concept.ConceptSpec" }
output = "PipeComposeSpec"
llm = "llm_to_engineer"
prompt_template = """
Your job is to design a PipeComposeSpec to render a jinja2 template.

This PipeCompose is part of a larger pipeline:
@plan_draft

You will specifically generate the PipeCompose related to this signature:
@pipe_signature
"""

# ────────────────────────────────────────────────────────────────────────────────
# PIPE FIXERS — one per pipe type, all fixing specific pipe type issues
# ────────────────────────────────────────────────────────────────────────────────

# [pipe.fix_failing_pipe]
# type = "PipeCondition"
# description = "Route to specific pipe fixer based on the failing pipe type."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "Dynamic"
# expression = "pipe_failure.pipe.type"

# [pipe.fix_failing_pipe.pipe_map]
# PipeLLM = "fix_failing_llm_pipe"
# PipeImgGen = "fix_failing_imggen_pipe"
# PipeOcr = "fix_failing_ocr_pipe"
# PipeFunc = "fix_failing_func_pipe"
# PipeCompose = "fix_failing_jinja2_pipe"
# PipeSequence = "fix_failing_sequence_pipe"
# PipeParallel = "fix_failing_parallel_pipe"
# PipeCondition = "fix_failing_condition_pipe"
# PipeBatch = "fix_failing_batch_pipe"

# [pipe.fix_failing_llm_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeLLM spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeLLMSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeLLM spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeLLMSpec. Common LLM pipe issues to fix:
# - Missing input variables in the pipe inputs that are referenced in prompt_template
# - Incorrect variable names in prompt templates (use $ for inline, @ for blocks)
# - Wrong concept types for inputs/outputs
# - Missing llm configuration
# - Invalid prompt template syntax
# """

# [pipe.fix_failing_imggen_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeImgGen spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeImgGenSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeImgGen spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeImgGenSpec. Common ImgGen pipe issues to fix:
# - Missing or incorrect prompt input (should be text concept)
# - Invalid img_gen
# - Missing required inputs for dynamic prompt generation
# """

# [pipe.fix_failing_ocr_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeOcr spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeOcrSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeOcr spec.

# VERY IMPORTANT: THE INPUT OF THE PIPEOCR must be either an image or a pdf or a concept which refines one of them.
# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeOcrSpec. Common OCR pipe issues to fix:
# - Input must be of type Image or PDF
# - Output should typically be Page (native concept)
# - Missing or incorrect input concept types
# """

# [pipe.fix_failing_func_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeFunc spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeFuncSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeFunc spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeFuncSpec. Common Func pipe issues to fix:
# - Missing or incorrect function_name
# - Wrong input/output concept types for the function
# - Function not available in registry
# """

# [pipe.fix_failing_jinja2_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeCompose spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeComposeSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeCompose spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeComposeSpec. Common Jinja2 pipe issues to fix:
# - Invalid Jinja2 template syntax
# - Missing input variables referenced in template
# - Wrong concept types for inputs/outputs
# """

# [pipe.fix_failing_sequence_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeSequence spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeSequenceSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeSequence spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeSequenceSpec. Common Sequence pipe issues to fix:
# - Missing input variables needed by sub-pipes in steps
# - Referenced pipe codes in steps that don't exist
# - Circular dependencies in step order
# - Wrong result names in steps
# """

# [pipe.fix_failing_parallel_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeParallel spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeParallelSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeParallel spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeParallelSpec. Common Parallel pipe issues to fix:
# - Missing input variables needed by parallel sub-pipes
# - Referenced pipe codes that don't exist
# - Incompatible output types from parallel branches
# """

# [pipe.fix_failing_condition_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeCondition spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeConditionSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeCondition spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeConditionSpec. Common Condition pipe issues to fix:
# - Invalid expression or expression_template syntax
# - Referenced pipe codes in pipe_map that don't exist
# - Missing input variables referenced in expression
# - Incompatible output types from different condition branches
# """

# [pipe.fix_failing_batch_pipe]
# type = "PipeLLM"
# description = "Fix a failing PipeBatch spec based on its specific error."
# inputs = { pipelex_bundle_spec = "PipelexBundleSpec", pipe_failure = "PipeFailure" }
# output = "PipeBatchSpec"
# llm = "llm_to_engineer"
# prompt_template = """
# Fix this failing PipeBatch spec.

# Failing pipe:
# @pipe_failure.pipe_spec

# Error message:
# @pipe_failure.error_message

# Please provide only the corrected PipeBatchSpec. Common Batch pipe issues to fix:
# - Missing branch_pipe_code or referenced pipe that doesn't exist
# - Wrong input types for batch processing (should be ListContent)
# - Missing batch parameters configuration
# """

