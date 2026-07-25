from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TransformPreviewResponse")


@_attrs_define
class TransformPreviewResponse:
    """
    Attributes:
        errors (list[None | str]):
        expression (str):
        field (str):
        original (list[None | str]):
        sample_size (int):
        transformed (list[None | str]):
    """

    errors: list[None | str]
    expression: str
    field: str
    original: list[None | str]
    sample_size: int
    transformed: list[None | str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        errors = []
        for errors_item_data in self.errors:
            errors_item: None | str
            errors_item = errors_item_data
            errors.append(errors_item)

        expression = self.expression

        field = self.field

        original = []
        for original_item_data in self.original:
            original_item: None | str
            original_item = original_item_data
            original.append(original_item)

        sample_size = self.sample_size

        transformed = []
        for transformed_item_data in self.transformed:
            transformed_item: None | str
            transformed_item = transformed_item_data
            transformed.append(transformed_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errors": errors,
                "expression": expression,
                "field": field,
                "original": original,
                "sample_size": sample_size,
                "transformed": transformed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:

            def _parse_errors_item(data: object) -> None | str:
                if data is None:
                    return data
                return cast(None | str, data)

            errors_item = _parse_errors_item(errors_item_data)

            errors.append(errors_item)

        expression = d.pop("expression")

        field = d.pop("field")

        original = []
        _original = d.pop("original")
        for original_item_data in _original:

            def _parse_original_item(data: object) -> None | str:
                if data is None:
                    return data
                return cast(None | str, data)

            original_item = _parse_original_item(original_item_data)

            original.append(original_item)

        sample_size = d.pop("sample_size")

        transformed = []
        _transformed = d.pop("transformed")
        for transformed_item_data in _transformed:

            def _parse_transformed_item(data: object) -> None | str:
                if data is None:
                    return data
                return cast(None | str, data)

            transformed_item = _parse_transformed_item(transformed_item_data)

            transformed.append(transformed_item)

        transform_preview_response = cls(
            errors=errors,
            expression=expression,
            field=field,
            original=original,
            sample_size=sample_size,
            transformed=transformed,
        )

        transform_preview_response.additional_properties = d
        return transform_preview_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
