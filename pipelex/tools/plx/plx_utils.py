from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, cast

import tomlkit
from tomlkit import array, document, inline_table, table
from tomlkit import string as tomlkit_string

from pipelex.tools.misc.json_utils import remove_none_values_from_dict

if TYPE_CHECKING:
    from pipelex.core.bundles.pipelex_bundle_blueprint import PipelexBundleBlueprint


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
    data = remove_none_values_from_dict(data=data)
    document_root = document()
    for section_key, section_value in data.items():
        if isinstance(section_value, Mapping):
            section_value = cast("Mapping[str, Any]", section_value)
            # Skip empty mappings (empty concept and pipe sections)
            if not section_value:
                continue
            table_obj = table()
            for field_key, field_value in section_value.items():
                if isinstance(field_value, Mapping):
                    # Second level mapping -> standard table [section.field]
                    sub_table = _convert_mapping_to_table(cast("Mapping[str, Any]", field_value))
                    table_obj.add(field_key, sub_table)
                else:
                    table_obj.add(field_key, _convert_dicts_to_inline_tables(field_value))
            document_root.add(section_key, table_obj)  # `[section_key]` section
        else:
            document_root.add(section_key, _convert_dicts_to_inline_tables(section_value))
    return tomlkit.dumps(document_root)  # pyright: ignore[reportUnknownMemberType]


def make_plx_content(blueprint: PipelexBundleBlueprint) -> str:
    blueprint_dict = blueprint.model_dump(serialize_as_any=True)
    return dict_to_plx_styled_toml(data=blueprint_dict)
