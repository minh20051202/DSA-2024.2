from __future__ import annotations

# Đây là mô-đun chứa định nghĩa lớp Date.

class Date:
    """
    Custom class to represent a date (day, month, year).
    Provides methods for comparing dates and calculating the difference between them.
    """
    def __init__(self, day: int, month: int, year: int):
        # Validate day, month, year
        if not (1 <= month <= 12):
            raise ValueError("Invalid month (must be between 1 and 12).")
        if not (1 <= day <= self._days_in_month(month, year)):
            raise ValueError(f"Ngày không hợp lệ cho tháng {month} năm {year}.")
        
        self.day = day
        self.month = month
        self.year = year

    def _is_leap_year(self, year: int) -> bool:
        """Checks if a year is a leap year."""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def _days_in_month(self, month: int, year: int) -> int:
        """Returns the number of days in a specific month of a specific year."""
        if month in {1, 3, 5, 7, 8, 10, 12}:
            return 31
        elif month in {4, 6, 9, 11}:
            return 30
        elif month == 2: # February
            return 29 if self._is_leap_year(year) else 28
        else:
            # This should not happen if the month was validated in __init__
            raise ValueError("Invalid month.")

    def to_ordinal(self) -> int:
        """Converts the date to an ordinal number.
        This ordinal number represents the total number of days since a fixed epoch (e.g., 01/01/0001).
        Useful for comparing and calculating differences between dates.
        Note: This calculation is a simplified version and may not be perfectly historically accurate
        for very distant past dates, but is sufficient for the purposes of this application.
        """
        days = self.day
        # Add days from previous months in the current year
        for m_loop in range(1, self.month):
            days += self._days_in_month(m_loop, self.year)
        
        # Add days from previous years
        days_from_previous_years = 0
        for y_loop in range(1, self.year): # Assuming epoch is year 1
            days_from_previous_years += 366 if self._is_leap_year(y_loop) else 365
        days += days_from_previous_years
        return days

    def days_between(self, other_date: Date) -> int:
        """Calculates the number of days between the current date (self) and another date (other_date).
        The result is positive if other_date is after self, negative if it is before.
        """
        if not isinstance(other_date, Date):
            raise TypeError("other_date argument must be a Date object.")
        
        # Use to_ordinal for easier calculation
        return other_date.to_ordinal() - self.to_ordinal()

    def __eq__(self, other: object) -> bool:
        """Equality comparison (==) between two Date objects."""
        if not isinstance(other, Date):
            return NotImplemented # Return NotImplemented for type mismatch
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __lt__(self, other: Date) -> bool:
        """Less than comparison (<) between two Date objects."""
        if not isinstance(other, Date):
            return NotImplemented
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        return self.day < other.day

    def __le__(self, other: Date) -> bool:
        """Less than or equal to comparison (<=) between two Date objects."""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: Date) -> bool:
        """Greater than comparison (>) between two Date objects."""
        return not self.__le__(other)

    def __ge__(self, other: Date) -> bool:
        """Greater than or equal to comparison (>=) between two Date objects."""
        return not self.__lt__(other)

    def __str__(self) -> str:
        """Returns a friendly string representation of the date (dd/mm/yyyy)."""
        return f"{self.day:02d}/{self.month:02d}/{self.year:04d}"

    def __repr__(self) -> str:
        """Returns an official string representation of the Date object, usable to recreate the object."""
        return f"Date(day={self.day}, month={self.month}, year={self.year})"
