from pathlib import Path
from datetime import date, timedelta
import csv
import hashlib
from csr.quiz import Quiz

CARD_FIELDS = ["hash", "content", "bin", "next_shown"]


def _time_delta_for_bin(bin: int) -> timedelta:
    """
    Calculate the time delta for a given bin number.

    Args:
        bin (int): The bin number.

    Returns:
        timedelta: A timedelta object representing the number of days for the given bin.
    """
    return timedelta(days=bin)


def _ensure_is_date(maybe_date: date | str) -> date:
    """
    Convert a string to a date object if necessary.

    Args:
        maybe_date (date | str): A date object or an ISO format date string.

    Returns:
        date: A date object.

    Note:
        TODO: Handle non-ISO format strings.
    """
    if isinstance(maybe_date, str):
        return date.fromisoformat(maybe_date)
    return maybe_date


def _hash_content(content: str) -> str:
    """
    Generate an MD5 hash of the given content.

    Args:
        content (str): The content to be hashed.

    Returns:
        str: The hexadecimal representation of the MD5 hash.
    """
    return hashlib.md5(content.encode()).hexdigest()


class Card:
    """
    Represents a flashcard in the spaced repetition system.

    Attributes:
        hash (str): A unique identifier for the card.
        content (str): The content of the card.
        bin (int): The current bin number for spaced repetition.
        next_shown (date): The next date the card should be shown.
    """

    def __init__(self, hash: str, content: str, bin: str | int, next_shown: str | date):
        self.hash = hash
        self.content = content
        self.bin = int(bin)
        self.next_shown = _ensure_is_date(next_shown)


def _load_cards(deck_path: Path) -> list[Card]:
    """
    Load cards from a CSV file.

    Args:
        deck_path (Path): The path to the CSV file containing the cards.

    Returns:
        list[Card]: A list of Card objects.
    """
    with open(deck_path, "r") as f:
        return [Card(**row) for row in csv.DictReader(f)]


def _save_cards(cards: list[Card], deck_path: Path) -> None:
    """
    Save cards to a CSV file.

    Args:
        cards (list[Card]): A list of Card objects to be saved.
        deck_path (Path): The path to the CSV file where cards will be saved.
    """
    with open(deck_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=CARD_FIELDS)
        writer.writeheader()

        for card in cards:
            writer.writerow(
                {
                    "hash": card.hash,
                    "content": card.content,
                    "bin": card.bin,
                    "next_shown": card.next_shown.isoformat(),
                }
            )


class Deck:
    """
    Represents a deck of flashcards for spaced repetition practice.

    Attributes:
        path (Path): The path to the CSV file containing the cards.
        cards (list[Card]): A list of Card objects in the deck.
    """

    def __init__(self, path: Path):
        """
        Initialize a Deck object.

        Args:
            path (Path): The path to the CSV file containing the cards.
        """
        self.path = path
        self.cards = _load_cards(path)

    def practice(self) -> None:
        """
        Conduct a practice session with the cards due for review.

        This method quizzes the user on cards that are due, updates their bins
        based on the user's performance, and saves the updated deck.
        """
        quiz = Quiz()
        today = date.today()

        for card in self.cards:
            if card.next_shown <= today:
                remembered: bool = quiz.does_user_remember(card.content)
                card.bin = card.bin + 1 if remembered else 0
                card.next_shown = today + _time_delta_for_bin(card.bin)

        _save_cards(self.cards, self.path)

    def add_card(self, content: str) -> None:
        """
        Add a new card to the deck.

        Args:
            content (str): The content of the new card.

        Note:
            TODO: Prevent duplicate content.
        """
        self.cards.append(
            Card(
                hash=_hash_content(content),
                content=content,
                bin=0,
                next_shown=date.today(),
            )
        )
        _save_cards(self.cards, self.path)

    def list(self) -> None:
        """
        Print the content of all cards in the deck.
        """
        for card in self.cards:
            print(card.content)
