from pathlib import Path
from datetime import date, timedelta
import csv
import hashlib
from srs.quiz import Quiz

def time_delta_for_bin(bin: int) -> timedelta:
        return timedelta(days=bin)

class Card:
    def __init__(self, uid, content, bin, next_shown: str | date):
        self.uid: str = str(uid)
        self.content: str = str(content)
        self.bin: int = int(bin)
        self.next_shown: date = date.fromisoformat(next_shown) if type(next_shown) == str else next_shown

class Deck:
    def __init__(self, path: Path):
        self.path = path
        with open(self.path, 'r') as f:
            self.cards = [Card(**row) for row in csv.DictReader(f)]
    
    def save_cards(self):
        with open(self.path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['uid', 'content', 'bin', 'next_shown'])
            writer.writeheader()
            for card in self.cards:
                writer.writerow({'uid': card.uid, 'content': card.content, 'bin': card.bin, 'next_shown': card.next_shown.isoformat()})
        
    def use(self):

        quiz = Quiz()
        today = date.today()

        for card in self.cards:
            if card.next_shown <= today:
                is_correct: bool = quiz.invoke(card.content)
                card.bin = card.bin + 1 if is_correct else 0
                card.next_shown = today + time_delta_for_bin(card.bin)

        self.save_cards()

    def add(self, content: str):
        self.cards.append(Card(
            uid=hashlib.md5(content.encode()).hexdigest(),
            content=content,
            bin=0,
            next_shown=date.today()
        ))
        self.save_cards()

    def list(self):
        for card in self.cards:
            print(card.content)