from pydantic import BaseModel
from typing import List

class GenreTitle(BaseModel):
    genreTitle: str

class AkaTitle(BaseModel):
    akaTitle: str
    regionAbbrev: str

class PrincipalsObject(BaseModel):
    nameID: str
    name: str
    category: str

class RatingObject(BaseModel):
    avRating: str
    nVotes: str

class TitleObject(BaseModel):
    titleID: str
    type: str
    originalTitle: str
    titlePoster: str
    startYear: str
    endYear: str
    genres: List[GenreTitle]
    titleAkas: List[AkaTitle]
    principals: List[PrincipalsObject]
    rating: List[RatingObject]

class NameObject(BaseModel):
    nameID: str
    name: str
    namePoster: str
    birthYr: str
    deathYr: str
    profession: str
    nameTitles: List[PrincipalsObject]