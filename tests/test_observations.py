"""Reading observations (DESIGN §2): four fields per row, and the one query,
everything public as of a date."""
from datetime import date

from abductive.observations import Row, as_of, read_csv


def test_reads_the_four_fields(tmp_path):
    f = tmp_path / "obs.csv"
    f.write_text("series,measured,value,public\nUNRATE,2024-01-01,3.7,2024-02-08\n")
    assert read_csv(f) == [Row("UNRATE", date(2024, 1, 1), 3.7, date(2024, 2, 8))]


def test_as_of_a_date_only_what_was_public_by_then():
    rows = [Row("UNRATE", date(2024, 1, 1), 3.7, date(2024, 2, 8)),
            Row("UNRATE", date(2024, 2, 1), 3.9, date(2024, 3, 8))]
    assert as_of(rows, date(2024, 3, 7)) == {"UNRATE": [(date(2024, 1, 1), 3.7)]}


def test_as_of_a_date_the_newest_version_public_by_then_counts():
    rows = [Row("CPIAUCSL", date(2024, 1, 1), 101.0, date(2024, 2, 16)),
            Row("CPIAUCSL", date(2024, 1, 1), 101.5, date(2024, 3, 16))]
    assert as_of(rows, date(2024, 3, 1))["CPIAUCSL"] == [(date(2024, 1, 1), 101.0)]
    assert as_of(rows, date(2024, 3, 16))["CPIAUCSL"] == [(date(2024, 1, 1), 101.5)]
