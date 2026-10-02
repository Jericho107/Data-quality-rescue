import pytest

from dq_rescue.core import Transaction, fail_closed, inspect, quality_report, sample


def test_clean_sample_passes() -> None:
    fail_closed(sample())
    assert quality_report(sample())["clean"] is True


def test_arithmetic_mismatch_is_critical() -> None:
    defects = inspect([Transaction("T1", "C1", 2, 10, 15, "paid")])
    assert any(
        defect.rule == "arithmetic_mismatch" and defect.severity == "critical"
        for defect in defects
    )


def test_material_defect_fails_closed() -> None:
    with pytest.raises(ValueError, match="material data-quality defects"):
        fail_closed([Transaction("T1", "C1", 2, 10, 15, "paid")])
