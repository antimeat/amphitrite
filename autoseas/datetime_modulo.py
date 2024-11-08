"""
Module for an extension of the datetime.datetime class that provides additional
functionality for handling timedelta objects.

Author: Daz Vink
"""

import datetime as dt

class datetime(dt.datetime):
    """
    Subclass of datetime.datetime that overrides the division, integer division,
    and modulo operators to handle datetime.timedelta objects.
    """
    
    def __divmod__(self, delta):
        """
        Compute the quotient and remainder of the datetime object divided by a timedelta object.

        Args:
            delta (datetime.timedelta): The timedelta object to divide by.

        Returns:
            tuple: A tuple containing the quotient and remainder as datetime objects.
        """
        seconds = int((self - dt.datetime.min).total_seconds())
        remainder = dt.timedelta(
            seconds=seconds % delta.total_seconds(),
            microseconds=self.microsecond,
        )
        quotient = self - remainder
        return quotient, remainder

    def __floordiv__(self, delta):
        """
        Compute the floor division of the datetime object by a timedelta object.

        Args:
            delta (datetime.timedelta): The timedelta object to divide by.

        Returns:
            datetime.datetime: The result of the floor division as a datetime object.
        """
        return divmod(self, delta)[0]

    def __mod__(self, delta):
        """
        Compute the modulo of the datetime object by a timedelta object.

        Args:
            delta (datetime.timedelta): The timedelta object to divide by.

        Returns:
            datetime.datetime: The result of the modulo operation as a datetime object.
        """
        return divmod(self, delta)[1]

