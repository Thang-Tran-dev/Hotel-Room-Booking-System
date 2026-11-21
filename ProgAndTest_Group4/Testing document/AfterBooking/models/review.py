"""Review entity + ReviewRepo."""
from models.base import Entity, Repository

class Review(Entity): FIELDS = {'review_id': 'id', 'rating': 'stars', 'content': 'text', 'review_date': 'at', 'image': 'img'}

class ReviewRepo(Repository):
    table, key = 'reviews', 'id'
    def for_room(self, rid): return self.db.q('select v.stars,v.text,v.at,u.name from reviews v join users u on u.id=v.uid where rid=? order by v.id desc', (rid,))
