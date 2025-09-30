from pipelex import pretty_print
from pipelex.client.protocol import ImplicitMemory
from pipelex.language.plx_factory import PlxFactory
from pipelex.libraries.pipelines.builder.builder import PipelexBundleSpec, validate_bundle_spec
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import save_text_to_path


class BuilderLoop:
    async def build_and_fix(self, pipe_code: str, input_memory: ImplicitMemory | None = None) -> PipelexBundleSpec:
        pretty_print(f"Building and fixing with {pipe_code}")
        pipe_output = await execute_pipeline(
            pipe_code=pipe_code,
            input_memory=input_memory,
        )
        pretty_print(pipe_output, title="Pipe Output")

        pipelex_bundle_spec = pipe_output.working_memory.get_stuff_as(name="pipelex_bundle_spec", content_type=PipelexBundleSpec)
        pretty_print(pipelex_bundle_spec, title="Pipelex Bundle Spec • 1st iteration")
        plx_content = PlxFactory.make_plx_content(blueprint=pipelex_bundle_spec.to_blueprint())
        save_text_to_path(text=plx_content, path="results/generated_pipeline_1st_iteration.plx")

        await validate_bundle_spec(pipelex_bundle_spec=pipelex_bundle_spec)

        return pipelex_bundle_spec
