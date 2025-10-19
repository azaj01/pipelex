from abc import abstractmethod
from typing import Any, Protocol, Sequence

from pydantic import BaseModel
from typing_extensions import runtime_checkable

from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.stuffs.stuff_content import StuffContent
from pipelex.pipe_run.pipe_run_params import PipeOutputMultiplicity
from pipelex.types import StrEnum
from pipelex.core.pipes.pipe_output import PipeOutput

# StuffContentOrData represents all possible formats for implicit memory input:
# Case 1: Direct content (no 'concept' key)
#   - 1.1: str (simple string)
#   - 1.2: Sequence[str] (list of strings)
#   - 1.3: StuffContent (a StuffContent object)
#   - 1.4: Sequence[StuffContent] (list of StuffContent objects, covariant)
# Case 2: Dict with 'concept' AND 'content' keys
#   - 2.1: {"concept": str, "content": str}
#   - 2.2: {"concept": str, "content": Sequence[str]}
#   - 2.3: {"concept": str, "content": StuffContent}
#   - 2.4: {"concept": str, "content": Sequence[StuffContent]}
#   - 2.5: {"concept": str, "content": dict[str, Any]}
#   - 2.6: {"concept": str, "content": Sequence[dict[str, Any]]}
DictStuffContent = dict[str, Any]
StuffContentOrData = (
    str  # Case 1.1
    | Sequence[str]  # Case 1.2
    | StuffContent  # Case 1.3
    | Sequence[StuffContent]  # Case 1.4 (covariant - accepts list[TextContent], etc.)
    | DictStuffContent  # Case 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
)
DictMemory = dict[str, DictStuffContent]  # Special case of ImplicitMemory (Case 2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
ImplicitMemory = dict[str, StuffContentOrData]


class PipelineState(StrEnum):
    """Enum representing the possible states of a pipe execution."""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    STARTED = "STARTED"


class ApiResponse(BaseModel):
    """Base response class for Pipelex API calls.

    Attributes:
        status (str | None): Status of the API call ("success", "error", etc.)
        message (str | None): Optional message providing additional information
        error (str | None): Optional error message when status is not "success"

    """

    status: str | None = None
    message: str | None = None
    error: str | None = None


class PipelineRequest(BaseModel):
    """Request for executing a pipeline.

    Attributes:
        inputs (ImplicitMemory | None): Inputs in the format of WorkingMemory.to_implicit_memory()
        output_name (str | None): Name of the output slot to write to
        output_multiplicity (PipeOutputMultiplicity | None): Output multiplicity setting
        dynamic_output_concept_code (str | None): Override for the dynamic output concept code

    """

    inputs: ImplicitMemory | None = None
    output_name: str | None = None
    output_multiplicity: PipeOutputMultiplicity | None = None
    dynamic_output_concept_code: str | None = None


class PipelineResponse(ApiResponse):
    """Response for pipeline execution requests.

    Attributes:
        created_at (str): Timestamp when the pipeline was created
        pipeline_state (PipelineState): Current state of the pipeline
        finished_at (str | None): Timestamp when the pipeline finished, if completed
        pipeline_run_id (str): Unique identifier for the pipeline run
        pipe_output (DictMemory | None): Output data from the pipeline execution as raw dict, if available
        main_stuff_name (str): Name of the main stuff in the pipeline output
    """

    created_at: str
    finished_at: str | None = None
    pipeline_state: PipelineState
    pipe_output: PipeOutput | None = None


@runtime_checkable
class PipelexProtocol(Protocol):
    """Protocol defining the contract for the Pipelex API.

    This protocol specifies the interface that any Pipelex API implementation must adhere to.
    All methods are asynchronous and handle pipeline execution, monitoring, and control.

    Attributes:
        api_token (str): Authentication token for API access
        api_base_url (str): Base URL for the API

    """

    api_token: str
    api_base_url: str

    @abstractmethod
    async def execute_pipeline(
        self,
        pipe_code: str,
        working_memory: WorkingMemory | None = None,
        inputs: ImplicitMemory | None = None,
        output_name: str | None = None,
        output_multiplicity: PipeOutputMultiplicity | None = None,
        dynamic_output_concept_code: str | None = None,
    ) -> PipelineResponse:
        """Execute a pipeline synchronously and wait for its completion.

        Args:
            pipe_code (str): The code identifying the pipeline to execute
            working_memory (WorkingMemory | None): Memory context passed to the pipeline
            inputs (ImplicitMemory | None): Inputs passed to the pipeline
            output_name (str | None): Target output slot name
            output_multiplicity (PipeOutputMultiplicity | None): Output multiplicity setting
            dynamic_output_concept_code (str | None): Override for dynamic output concept
        Returns:
            PipelineResponse: Complete execution results including pipeline state and output

        Raises:
            HTTPException: On execution failure or error
            ClientAuthenticationError: If API token is missing for API execution

        """
        ...

    @abstractmethod
    async def start_pipeline(
        self,
        pipe_code: str,
        working_memory: WorkingMemory | None = None,
        inputs: ImplicitMemory | None = None,
        output_name: str | None = None,
        output_multiplicity: PipeOutputMultiplicity | None = None,
        dynamic_output_concept_code: str | None = None,
    ) -> PipelineResponse:
        """Start a pipeline execution asynchronously without waiting for completion.

        Args:
            pipe_code (str): The code identifying the pipeline to execute
            working_memory (WorkingMemory | None): Memory context passed to the pipeline
            inputs (ImplicitMemory | None): Inputs passed to the pipeline
            output_name (str | None): Target output slot name
            output_multiplicity (PipeOutputMultiplicity | None): Output multiplicity setting
            dynamic_output_concept_code (str | None): Override for dynamic output concept

        Returns:
            PipelineResponse: Initial response with pipeline_run_id and created_at timestamp

        Raises:
            HTTPException: On pipeline start failure
            ClientAuthenticationError: If API token is missing for API execution

        """
        ...
