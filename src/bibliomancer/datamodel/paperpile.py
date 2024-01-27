from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict,  Field, field_validator
import re
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra = 'forbid',
        arbitrary_types_allowed=True,
        use_enum_values = True)


class ItemTypeEnum(str, Enum):
    
    # Preprint Manuscript
    Preprint_Manuscript = "Preprint Manuscript"
    # Thesis
    Thesis = "Thesis"
    # Book Chapter
    Book_Chapter = "Book Chapter"
    # Dataset
    Dataset = "Dataset"
    # Journal Article
    Journal_Article = "Journal Article"
    # Video or Film
    Video_or_Film = "Video or Film"
    # Review
    Review = "Review"
    # Conference Paper
    Conference_Paper = "Conference Paper"
    # Report
    Report = "Report"
    # Computer Program
    Computer_Program = "Computer Program"
    # News
    News = "News"
    
    

class LanguageEnum(str, Enum):
    
    # eng
    eng = "eng"
    # en
    en = "en"
    
    

class Sub-typeEnum(str, Enum):
    
    # Review
    Review = "Review"
    # Research Article
    Research_Article = "Research Article"
    # Online Video
    Online_Video = "Online Video"
    # News
    News = "News"
    
    

class ArchivePrefixEnum(str, Enum):
    
    # arXiv
    arXiv = "arXiv"
    
    

class Entry(ConfiguredBaseModel):
    
    Item_type: Optional[ItemTypeEnum] = Field(None)
    Authors: Optional[str] = Field(None)
    Editors: Optional[str] = Field(None)
    Title: Optional[List[str]] = Field(default_factory=list)
    Journal: Optional[str] = Field(None)
    Full_journal: Optional[str] = Field(None)
    Publication_year: Optional[int] = Field(None)
    Volume: Optional[str] = Field(None)
    Issue: Optional[str] = Field(None)
    Pages: Optional[str] = Field(None)
    Folders_filed_in: Optional[str] = Field(None)
    Labels_filed_in: Optional[str] = Field(None)
    Institution: Optional[str] = Field(None)
    Publisher: Optional[str] = Field(None)
    Address: Optional[str] = Field(None)
    Book_title: Optional[str] = Field(None)
    Proceedings_title: Optional[str] = Field(None)
    Conference: Optional[str] = Field(None)
    Conference_location: Optional[str] = Field(None)
    Conference_date: Optional[datetime ] = Field(None)
    Date_published: Optional[datetime ] = Field(None)
    Date_accessed: Optional[datetime ] = Field(None)
    ISBN: Optional[int] = Field(None)
    ISBN_(alt.): Optional[int] = Field(None)
    ISSN: Optional[str] = Field(None)
    ISSN_(alt.): Optional[str] = Field(None)
    URLs: Optional[str] = Field(None)
    DOI: Optional[str] = Field(None)
    PMID: Optional[int] = Field(None)
    Arxiv_ID: Optional[float] = Field(None)
    Associated_DOI: Optional[str] = Field(None)
    PMC_ID: Optional[str] = Field(None)
    Abstract: Optional[str] = Field(None)
    Keywords: Optional[str] = Field(None)
    Notes: Optional[str] = Field(None)
    Short_title: Optional[str] = Field(None)
    Copyright: Optional[str] = Field(None)
    Affiliation: Optional[str] = Field(None)
    Language: Optional[LanguageEnum] = Field(None)
    Sub_type: Optional[Sub-typeEnum] = Field(None)
    Series: Optional[str] = Field(None)
    Archive_prefix: Optional[ArchivePrefixEnum] = Field(None)
    Eprint_ID: Optional[float] = Field(None)
    Primary_class: Optional[str] = Field(None)
    Pages_cited: Optional[datetime ] = Field(None)
    Advisor: Optional[str] = Field(None)
    School: Optional[str] = Field(None)
    Department: Optional[str] = Field(None)
    Degree: Optional[str] = Field(None)
    Source: Optional[str] = Field(None)
    Dataset_name: Optional[str] = Field(None)
    Dataset_author(s): Optional[str] = Field(None)
    Dataset_URL: Optional[str] = Field(None)
    Dataset_DOI: Optional[str] = Field(None)
    Running_time: Optional[str] = Field(None)
    Directors: Optional[str] = Field(None)
    Date_released: Optional[datetime ] = Field(None)
    Studio_or_distributor: Optional[str] = Field(None)
    Library_catalog/database: Optional[str] = Field(None)
    Social_Media_handle: Optional[str] = Field(None)
    
        


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Entry.model_rebuild()

