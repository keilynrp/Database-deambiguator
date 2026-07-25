from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ROIRequest")


@_attrs_define
class ROIRequest:
    """
    Attributes:
        investment (float):
        market_size (int):
        revenue_per_unit (float):
        adoption_volatility (float | Unset):  Default: 0.05.
        annual_cost (float | Unset):  Default: 0.0.
        base_adoption_rate (float | Unset):  Default: 0.15.
        horizon_years (int | Unset):  Default: 5.
        n_simulations (int | Unset):  Default: 2000.
    """

    investment: float
    market_size: int
    revenue_per_unit: float
    adoption_volatility: float | Unset = 0.05
    annual_cost: float | Unset = 0.0
    base_adoption_rate: float | Unset = 0.15
    horizon_years: int | Unset = 5
    n_simulations: int | Unset = 2000
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        investment = self.investment

        market_size = self.market_size

        revenue_per_unit = self.revenue_per_unit

        adoption_volatility = self.adoption_volatility

        annual_cost = self.annual_cost

        base_adoption_rate = self.base_adoption_rate

        horizon_years = self.horizon_years

        n_simulations = self.n_simulations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "investment": investment,
                "market_size": market_size,
                "revenue_per_unit": revenue_per_unit,
            }
        )
        if adoption_volatility is not UNSET:
            field_dict["adoption_volatility"] = adoption_volatility
        if annual_cost is not UNSET:
            field_dict["annual_cost"] = annual_cost
        if base_adoption_rate is not UNSET:
            field_dict["base_adoption_rate"] = base_adoption_rate
        if horizon_years is not UNSET:
            field_dict["horizon_years"] = horizon_years
        if n_simulations is not UNSET:
            field_dict["n_simulations"] = n_simulations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        investment = d.pop("investment")

        market_size = d.pop("market_size")

        revenue_per_unit = d.pop("revenue_per_unit")

        adoption_volatility = d.pop("adoption_volatility", UNSET)

        annual_cost = d.pop("annual_cost", UNSET)

        base_adoption_rate = d.pop("base_adoption_rate", UNSET)

        horizon_years = d.pop("horizon_years", UNSET)

        n_simulations = d.pop("n_simulations", UNSET)

        roi_request = cls(
            investment=investment,
            market_size=market_size,
            revenue_per_unit=revenue_per_unit,
            adoption_volatility=adoption_volatility,
            annual_cost=annual_cost,
            base_adoption_rate=base_adoption_rate,
            horizon_years=horizon_years,
            n_simulations=n_simulations,
        )

        roi_request.additional_properties = d
        return roi_request

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
