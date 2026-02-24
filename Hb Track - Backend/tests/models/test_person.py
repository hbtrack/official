"""
Test Person Model - AR_999 Example

Validates that Person model has birth_date field working correctly.
"""
import pytest
from datetime import date
from app.models.person import Person


def test_birthdate_field():
    """
    AR_999: Validate that Person.birth_date field exists and is correctly typed.
    
    This is an example test demonstrating write_scope validation.
    The field already exists in the schema (not a new migration).
    """
    # Arrange: Create a Person instance (not persisted, just ORM object)
    person = Person(
        first_name="João",
        last_name="Silva",
        full_name="João Silva",
        birth_date=date(1990, 5, 15),
    )
    
    # Assert: Verify birth_date attribute exists and has correct type
    assert hasattr(person, 'birth_date'), "Person must have birth_date attribute"
    assert isinstance(person.birth_date, date), "birth_date must be a date object"
    assert person.birth_date == date(1990, 5, 15), "birth_date value must match"
    
    # Assert: Verify the mapped column exists in model
    assert 'birth_date' in Person.__mapper__.columns, "Person must have birth_date column"
    
    print("✅ test_birthdate_field PASSED: Person.birth_date exists and works correctly")
