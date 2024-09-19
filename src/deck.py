from pathlib import Path
from datetime import date, timedelta
import csv
import hashlib
from src.quiz import Quiz

class Card:
    def __init__(self, uid, content, bin, next: str | date):
        self.uid: str = str(uid)
        self.content: str = str(content)
        self.bin: int = int(bin)
        self.next: date = date.fromisoformat(next) if type(next) == str else next

class Deck:
    def __init__(self, path: Path):
        self.path = path
        self.cards: list[Card] = self.load_cards()

    def load_cards(self) -> list[Card]:
        with open(self.path, 'r') as f:
            return [Card(**row) for row in csv.DictReader(f)]
    
    def save_cards(self):
        with open(self.path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['uid', 'content', 'bin', 'next'])
            writer.writeheader()
            for card in self.cards:
                writer.writerow({'uid': card.uid, 'content': card.content, 'bin': card.bin, 'next': card.next.isoformat()})
        
    def use(self):

        quiz = Quiz()
        today = date.today()

        for card in self.cards:
            if card.next <= today:
                is_correct: bool = quiz.invoke(card.content)
                card.bin = card.bin + 1 if is_correct else 0
                card.next = today + timedelta(days=card.bin)

        self.save_cards()

    def add(self, content: str):
        self.cards.append(Card(
            uid=hashlib.md5(content.encode()).hexdigest(),
            content=content,
            bin=0,
            next=date.today()
        ))
        self.save_cards()

    def list(self):
        for card in self.cards:
            print(card.content)