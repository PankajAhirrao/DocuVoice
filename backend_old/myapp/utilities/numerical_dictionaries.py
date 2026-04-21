"""
This module provides dictionaries for handling numerical values in legal text simplification.
"""


class NumericalDictionaries:
    """
    Class that provides dictionaries for numerical values and formatting patterns.
    """

    @staticmethod
    def get_dictionaries():
        """
        Get all numerical dictionaries needed for legal text simplification.

        Returns:
            dict: Dictionary of all numerical dictionaries and formatting patterns
        """
        # Basic number words
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
            'seventy': 70, 'eighty': 80, 'ninety': 90
        }

        # Add capitalized versions
        capitalized = {word.capitalize(): value for word, value in number_words.items()}
        number_words.update(capitalized)

        # Add magnitude words
        magnitude_words = {
            'hundred': 100,
            'thousand': 1000,
            'million': 1000000,
            'billion': 1000000000,
            'trillion': 1000000000000
        }

        # Add capitalized versions of magnitude words
        magnitude_capitalized = {word.capitalize(): value for word, value in magnitude_words.items()}
        magnitude_words.update(magnitude_capitalized)

        # Add common date words
        date_words = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        # Add capitalized versions of month names
        date_capitalized = {word.capitalize(): value for word, value in date_words.items()}
        date_words.update(date_capitalized)

        # Add ordinal numbers
        ordinal_words = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
            'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
            'eleventh': 11, 'twelfth': 12, 'thirteenth': 13, 'fourteenth': 14, 'fifteenth': 15,
            'sixteenth': 16, 'seventeenth': 17, 'eighteenth': 18, 'nineteenth': 19, 'twentieth': 20,
            'thirtieth': 30, 'fortieth': 40, 'fiftieth': 50, 'sixtieth': 60,
            'seventieth': 70, 'eightieth': 80, 'ninetieth': 90
        }

        # Add capitalized versions of ordinals
        ordinal_capitalized = {word.capitalize(): value for word, value in ordinal_words.items()}
        ordinal_words.update(ordinal_capitalized)

        # Add common currency terms
        currency_terms = {
            'dollar': 'USD',
            'dollars': 'USD',
            'cent': 'cent',
            'cents': 'cents',
            'euro': 'EUR',
            'euros': 'EUR',
            'pound': 'GBP',
            'pounds': 'GBP'
        }

        # Add capitalized versions of currency terms
        currency_capitalized = {word.capitalize(): value for word, value in currency_terms.items()}
        currency_terms.update(currency_capitalized)

        # Add time period terms
        time_terms = {
            'day': 'day',
            'days': 'days',
            'week': 'week',
            'weeks': 'weeks',
            'month': 'month',
            'months': 'months',
            'year': 'year',
            'years': 'years',
            'annual': 'yearly',
            'annually': 'yearly',
            'quarterly': 'every 3 months',
            'bi-weekly': 'every 2 weeks',
            'bi-monthly': 'every 2 months',
            'semi-annually': 'every 6 months'
        }

        # Add capitalized versions of time terms
        time_capitalized = {word.capitalize(): value for word, value in time_terms.items()}
        time_terms.update(time_capitalized)

        # Add legal-specific numerical terms
        legal_numerical_terms = {
            'per annum': 'per year',
            'per diem': 'per day',
            'per month': 'monthly',
            'per quarter': 'quarterly',
            'per week': 'weekly',
            'pro rata': 'proportionally',
            'net 30': 'payable within 30 days',
            'net 60': 'payable within 60 days',
            'net 90': 'payable within 90 days'
        }

        # Numerical extracted from documents (example)
        extracted_numerical = {
            # Monetary values
            'Two Thousand Dollars': '$2,000',
            'Three Thousand Dollars': '$3,000',
            'One Thousand Five Hundred Dollars': '$1,500',
            'Five Hundred Dollars': '$500',

            # Dates
            'January 1, 2025': '1/1/2025',
            'December 31, 2025': '12/31/2025',
            'March 15, 2025': '3/15/2025',

            # Time periods
            'twelve (12) months': '12 months',
            'thirty (30) days': '30 days',
            'ninety (90) days': '90 days',
            'forty-five (45) days': '45 days',

            # Percentages
            'fifty percent (50%)': '50%',
            'twenty-five percent (25%)': '25%',
            'seventy-five percent (75%)': '75%',

            # Fractions
            'one-half (1/2)': '1/2',
            'one-third (1/3)': '1/3',
            'three-quarters (3/4)': '3/4'
        }

        # Format patterns for numbers, dates, and currency across simplification levels
        format_patterns = {
            # Level 1 patterns (maintain formality)
            1: {
                'date': '{month} {day}, {year}',
                'money': '{words} Dollars (${amount})',
                'money_simple': '${amount}',
                'number_with_unit': '{number} ({digit}) {unit}',
                'number': '{number} ({digit})'
            },

            # Level 2 patterns (moderate simplification)
            2: {
                'date': '{month} {day}, {year}',
                'money': '${amount} ({words} Dollars)',
                'money_simple': '${amount}',
                'number_with_unit': '{digit} {unit}',
                'number': '{digit}'
            },

            # Level 3 patterns (maximum simplification)
            3: {
                'date': '{digit_month}/{day}/{year}',
                'money': '${amount}',
                'money_simple': '${amount}',
                'number_with_unit': '{digit} {unit}',
                'number': '{digit}'
            }
        }

        return {
            'numbers': number_words,
            'magnitudes': magnitude_words,
            'dates': date_words,
            'ordinals': ordinal_words,
            'currencies': currency_terms,
            'time_terms': time_terms,
            'legal_numerical': legal_numerical_terms,
            'extracted': extracted_numerical,
            'patterns': format_patterns
        }