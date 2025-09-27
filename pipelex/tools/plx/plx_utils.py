from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, cast

import tomlkit
from tomlkit import array, document, inline_table, table
from tomlkit import string as tomlkit_string

from pipelex import log
from pipelex.core.bundles.pipelex_bundle_blueprint import PipelexBundleBlueprint
from pipelex.tools.misc.json_utils import remove_none_values_from_dict
from pipelex.types import StrEnum

if TYPE_CHECKING:
    from pipelex.core.bundles.pipelex_bundle_blueprint import PipelexBundleBlueprint


class SectionKey(StrEnum):
    PIPE = "pipe"
    CONCEPT = "concept"


CONCEPT_STRUCTURE_FIELD_KEY = "structure"


def _format_tomlkit_string(
    text: str,
    prefer_literal: bool = False,
    force_multiline: bool = False,
    ensure_trailing_newline: bool = True,
    ensure_leading_blank_line: bool = True,
) -> Any:  # Can't type this because of tomlkit
    r"""Build a tomlkit string node.
    - If `force_multiline` or the text contains '\\n', we emit a triple-quoted multiline string.
    - When multiline, `ensure_trailing_newline` puts the closing quotes on their own line.
    - When multiline, `ensure_leading_blank_line` inserts a real blank line at the start of the string.
    """
    needs_multiline = force_multiline or ("\n" in text)
    normalized = text

    if needs_multiline:
        if ensure_leading_blank_line and not normalized.startswith("\n"):
            normalized = "\n" + normalized
        if ensure_trailing_newline and not normalized.endswith("\n"):
            normalized = normalized + "\n"

    use_literal = prefer_literal and ("'''" not in normalized)
    return tomlkit_string(normalized, multiline=needs_multiline, literal=use_literal)


def _convert_dicts_to_inline_tables(value: Any) -> Any:  # Can't type this because of tomlkit
    """Recursively convert Python values; dicts -> inline tables; lists kept as arrays."""
    if isinstance(value, Mapping):
        value = cast("Mapping[str, Any]", value)
        inline_table_obj = inline_table()
        for key, value_item in value.items():
            inline_table_obj[key] = _convert_dicts_to_inline_tables(value_item)
        return inline_table_obj

    if isinstance(value, list):
        value = cast("list[Any]", value)
        array_obj = array()
        array_obj.multiline(True)  # set to False for single-line arrays
        for element in value:
            if isinstance(element, Mapping):
                element = cast("Mapping[str, Any]", element)
                inline_element = inline_table()
                for inner_key, inner_value in element.items():
                    inline_element[inner_key] = _convert_dicts_to_inline_tables(inner_value)
                array_obj.append(inline_element)  # pyright: ignore[reportUnknownMemberType]
            else:
                array_obj.append(_convert_dicts_to_inline_tables(element))  # pyright: ignore[reportUnknownMemberType]
        return array_obj

    if isinstance(value, str):
        return _format_tomlkit_string(value)
    return value


def _convert_mapping_to_table(mapping: Mapping[str, Any]) -> Any:  # Can't type this because of tomlkit
    """Convert a mapping into a TOML Table where any nested mappings (third level+)
    are converted to inline tables.

    This creates a second-level standard table, and only uses inline tables for
    third level and deeper structures.
    """
    tbl = table()
    for field_key, field_value in mapping.items():
        if isinstance(field_value, Mapping):
            # Third-level mapping -> inline table
            tbl.add(field_key, _convert_dicts_to_inline_tables(field_value))
        else:
            tbl.add(field_key, _convert_dicts_to_inline_tables(field_value))
    return tbl


def dict_to_plx_styled_toml(data: Mapping[str, Any]) -> str:
    """Top-level keys become tables; second-level mappings become tables; inline tables start at third level."""
    log.debug("=" * 100)
    data = remove_none_values_from_dict(data=data)
    document_root = document()
    for root_key, root_value in data.items():
        if not isinstance(root_value, Mapping):
            log.debug(f"Root root_key is not a mapping: key = {root_key}, value = {root_value}")
            document_root.add(root_key, _convert_dicts_to_inline_tables(root_value))
            continue

        # It's a mapping, therefore it's a section
        log.debug(f"Root {root_key} is a section -------------------")

        section_key = SectionKey(root_key)
        section_value = cast("Mapping[str, Any]", root_value)
        # Skip empty mappings (empty concept and pipe sections)
        if not section_value:
            log.debug(f"Section {section_key} is empty, skipping")
            continue
        match section_key:
            case SectionKey.PIPE:
                table_obj_for_pipe = _make_table_obj_for_pipe(section_value)
                document_root.add(section_key, table_obj_for_pipe)
            case SectionKey.CONCEPT:
                table_obj_for_concept = _make_table_obj_for_concept(section_value)
                document_root.add(section_key, table_obj_for_concept)

    return tomlkit.dumps(document_root)  # pyright: ignore[reportUnknownMemberType]


def _make_table_obj_for_pipe(section_value: Mapping[str, Any]) -> Any:
    """Make a table object for a pipe section."""
    log.debug("******** Making table object for pipe section ********")
    table_obj = table()
    for field_key, field_value in section_value.items():
        log.debug(f"------ Field {field_key} is a {type(field_value)}")
        if not isinstance(field_value, Mapping):
            log.debug(f"Field is not a mapping: key = {field_key}, value = {field_value}")
            table_obj.add(field_key, _convert_dicts_to_inline_tables(field_value))
            continue
        log.debug(f"Field is a mapping: key = {field_key}, value = {field_value}")
        field_value = cast("Mapping[str, Any]", field_value)
        table_obj.add(field_key, _convert_mapping_to_table(field_value))
    return table_obj


def _make_table_obj_for_concept(section_value: Mapping[str, Any]) -> Any:
    """Make a table object for a concept section."""
    log.debug("******** Making table object for concept section ********")
    table_obj = table()
    for concept_key, concept_value in section_value.items():
        if isinstance(concept_value, str):
            log.debug(f"Concept '{concept_key}' is a string: {concept_value}")
            table_obj.add(concept_key, concept_value)
            continue
        if not isinstance(concept_value, Mapping):
            msg = f"Concept field value is not a mapping: key = {concept_key}, value = {concept_value}"
            raise TypeError(msg)
        log.debug(f"Concept '{concept_key}' is a mapping: {concept_value}")
        concept_value = cast("Mapping[str, Any]", concept_value)
        concept_table_obj = table()
        for concept_field_key, concept_field_value in concept_value.items():
            if concept_field_key == CONCEPT_STRUCTURE_FIELD_KEY:
                if isinstance(concept_field_value, str):
                    log.debug(f"Structure for concept '{concept_key}' is a string: {concept_field_value}")
                    concept_table_obj.add("structure", concept_field_value)
                    continue
                if not isinstance(concept_field_value, Mapping):
                    msg = f"Structure field value is not a mapping: key = {concept_field_key}, value = {concept_field_value}"
                    raise TypeError(msg)
                log.debug(f"Structure for concept '{concept_key}' is a mapping: {concept_field_value}")
                structure_value = cast("Mapping[str, Any]", concept_field_value)
                structure_table_obj = table()
                for structure_field_key, structure_field_value in structure_value.items():
                    if isinstance(structure_field_value, str):
                        log.debug(f"Structure '{structure_field_key}' is a string: {structure_field_value}")
                        structure_table_obj.add(structure_field_key, structure_field_value)
                        continue
                    if not isinstance(structure_field_value, Mapping):
                        msg = f"Structure field value is neither a string nor a mapping: key = {structure_field_key}, value = {structure_field_value}"
                        raise TypeError(msg)
                    log.debug(f"Structure for '{concept_key}' is a mapping: {structure_field_value}")
                    # structure_field_value = cast("Mapping[str, Any]", structure_field_value)
                    # structure_field_table = _convert_mapping_to_table(structure_value)
                    structure_table_obj.add(structure_field_key, _convert_dicts_to_inline_tables(structure_field_value))
                concept_table_obj.add("structure", structure_table_obj)
            else:
                # sub_table = _convert_mapping_to_table(concept_field_value)
                log.debug(f"{concept_key}/'{concept_field_key}' is inline: {concept_field_value}")
                concept_table_obj.add(concept_field_key, _convert_dicts_to_inline_tables(concept_field_value))
        table_obj.add(concept_key, concept_table_obj)
    return table_obj


def make_plx_content(blueprint: PipelexBundleBlueprint) -> str:
    blueprint_dict = blueprint.model_dump(serialize_as_any=True)
    return dict_to_plx_styled_toml(data=blueprint_dict)
