from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict, Field, field_validator
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
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


class TypeEnum(str, Enum):

    Audiovisual = "Audiovisual"

    Book = "Book"

    BookChapter = "BookChapter"

    ComputationalNotebook = "ComputationalNotebook"

    Collection = "Collection"

    ConferencePaper = "ConferencePaper"

    ConferenceProceeding = "ConferenceProceeding"

    Dataset = "Dataset"

    Dissertation = "Dissertation"

    Journal = "Journal"

    JournalArticle = "JournalArticle"

    Model = "Model"

    PeerReview = "PeerReview"

    News = "News"

    Preprint = "Preprint"

    Report = "Report"

    Software = "Software"

    Standard = "Standard"

    Other = "Other"


class ContributorType(str, Enum):
    """
    The type of contributor being represented
    """

    # a person
    Person = "Person"
    # an organization
    Organization = "Organization"


class ContributorRole(str, Enum):
    """
    The type of contribution made by a contributor
    """

    # Person with knowledge of how to access, troubleshoot, or otherwise field issues related to the resource. May also be "Point of Contact" in organisation that controls access to the resource, if that organisation is different from Publisher, Distributor, Data Manager.
    DataCiteCOLONContactPerson = "DataCite:ContactPerson"
    # Person/institution responsible for finding, gathering/collecting data under the guidelines of the author(s) or Principal Investigator (PI). May also use when crediting survey conductors, interviewers, event or condition observers, person responsible for monitoring key instrument data.
    DataCiteCOLONDataCollector = "DataCite:DataCollector"
    # Person tasked with reviewing, enhancing, cleaning, or standardizing metadata and the associated data submitted for storage, use, and maintenance within a data centre or repository. While the "DataManager" is concerned with digital maintenance, the DataCurator's role encompasses quality assurance focused on content and metadata. This includes checking whether the submitted dataset is complete, with all files and components as described by submitter, whether the metadata is standardized to appropriate systems and schema, whether specialized metadata is needed to add value and ensure access across disciplines, and determining how the metadata might map to search engines, database products, and automated feeds.
    DataCiteCOLONDataCurator = "DataCite:DataCurator"
    # Person (or organisation with a staff of data managers, such as a data centre) responsible for maintaining the finished resource. The work done by this person or organisation ensures that the resource is periodically "refreshed" in terms of software/hardware support, is kept available or is protected from unauthorized access, is stored in accordance with industry standards, and is handled in accordance with the records management requirements applicable to it.
    DataCiteCOLONDataManager = "DataCite:DataManager"
    # Institution tasked with responsibility to generate/disseminate copies of the resource in either electronic or print form. Works stored in more than one archive/repository may credit each as a distributor.
    DataCiteCOLONDistributor = "DataCite:Distributor"
    # A person who oversees the details related to the publication format of the resource. N.b. if the Editor is to be credited in place of multiple creators, the Editor's name may be supplied as Creator, with "(Ed.)" appended to the name.
    DataCiteCOLONEditor = "DataCite:Editor"
    # Typically, the organisation allowing the resource to be available on the internet through the provision of its hardware/software/operating support. May also be used for an organisation that stores the data offline. Often a data centre (if that data centre is not the "publisher" of the resource.)
    DataCiteCOLONHostingInstitution = "DataCite:HostingInstitution"
    # Typically a person or organisation responsible for the artistry and form of a media product. In the data industry, this may be a company "producing" DVDs that package data for future dissemination by a distributor.
    DataCiteCOLONProducer = "DataCite:Producer"
    # Person officially designated as head of project team or sub- project team instrumental in the work necessary to development of the resource. The Project Leader is not "removed" from the work that resulted in the resource; he or she remains intimately involved throughout the life of the particular project team.
    DataCiteCOLONProjectLeader = "DataCite:ProjectLeader"
    # Person officially designated as manager of a project. Project may consist of one or many project teams and sub-teams. The manager of a project normally has more administrative responsibility than actual work involvement.
    DataCiteCOLONProjectManager = "DataCite:ProjectManager"
    # Person on the membership list of a designated project/project team. This vocabulary may or may not indicate the quality, quantity, or substance of the person's involvement.
    DataCiteCOLONProjectMember = "DataCite:ProjectMember"
    # Institution/organisation officially appointed by a Registration Authority to handle specific tasks within a defined area of responsibility. DataCite is a Registration Agency for the International DOI Foundation (IDF). One of DataCite's tasks is to assign DOI prefixes to the allocating agents who then assign the full, specific character string to data clients, provide metadata back to the DataCite registry, etc.
    DataCiteCOLONRegistrationAgency = "DataCite:RegistrationAgency"
    # A standards-setting body from which Registration Agencies obtain official recognition and guidance. The IDF serves as the Registration Authority for the International Standards Organisation (ISO) in the area/domain of Digital Object Identifiers.
    DataCiteCOLONRegistrationAuthority = "DataCite:RegistrationAuthority"
    # A person without a specifically defined role in the development of the resource, but who is someone the author wishes to recognize. This person could be an author's intellectual mentor, a person providing intellectual leadership in the discipline or subject domain, etc.
    DataCiteCOLONRelatedPerson = "DataCite:RelatedPerson"
    # A person involved in analyzing data or the results of an experiment or formal study. May indicate an intern or assistant to one of the authors who helped with research but who was not so "key" as to be listed as an author. Should be a person, not an institution. Note that a person involved in the gathering of data would fall under the contributorType "DataCollector." The researcher may find additional data online and correlate it to the data collected for the experiment or study, for example.
    DataCiteCOLONResearcher = "DataCite:Researcher"
    # Typically refers to a group of individuals with a lab, department, or division; the group has a particular, defined focus of activity. May operate at a narrower level of scope; may or may not hold less administrative responsibility than a project team.
    DataCiteCOLONResearchGroup = "DataCite:ResearchGroup"
    # Person or institution owning or managing property rights, including intellectual property rights over the resource.
    DataCiteCOLONRightsHolder = "DataCite:RightsHolder"
    # Person or organisation that issued a contract or under the auspices of which a work has been written, printed, published, developed, etc. Includes organisations that provide in-kind support, through donation, provision of people or a facility or instrumentation necessary for the development of the resource, etc.
    DataCiteCOLONSponsor = "DataCite:Sponsor"
    # Designated administrator over one or more groups/teams working to produce a resource or over one or more steps of a development process.
    DataCiteCOLONSupervisor = "DataCite:Supervisor"
    # A Work Package is a recognized data product, not all of which is included in publication. The package, instead, may include notes, discarded documents, etc. The Work Package Leader is responsible for ensuring the comprehensive contents, versioning, and availability of the Work Package during the development of the resource.
    DataCiteCOLONWorkPackageLeader = "DataCite:WorkPackageLeader"
    # Any person or institution making a significant contribution to the development and/or maintenance of the resource, but whose contribution does not "fit" other controlled vocabulary for contributorType. Could be a photographer, artist, or writer whose contribution helped to publicize the resource (as opposed to creating it), a reviewer of the resource, someone providing administrative services to the author (such as depositing updates into an online repository, analysing usage, etc.), or one of many other roles.
    DataCiteCOLONOther = "DataCite:Other"
    # Ideas; formulation or evolution of overarching research goals and aims.
    CRediTCOLONconceptualization = "CRediT:conceptualization"
    # Management activities to annotate (produce metadata), scrub data and maintain research data (including software code, where it is necessary for interpreting the data itself) for initial use and later reuse.
    CRediTCOLONdata_curation = "CRediT:data-curation"
    # Application of statistical, mathematical, computational, or other formal techniques to analyze or synthesize study data.
    CRediTCOLONformal_analysis = "CRediT:formal-analysis"
    # Acquisition of the financial support for the project leading to this publication.
    CRediTCOLONfunding_acquisition = "CRediT:funding-acquisition"
    # Conducting a research and investigation process, specifically performing the experiments, or data/evidence collection.
    CRediTCOLONinvestigation = "CRediT:investigation"
    # Development or design of methodology; creation of models.
    CRediTCOLONmethodology = "CRediT:methodology"
    # Management and coordination responsibility for the research activity planning and execution.
    CRediTCOLONproject_administration = "CRediT:project-administration"
    # Provision of study materials, reagents, materials, patients, laboratory samples, animals, instrumentation, computing resources, or other analysis tools.
    CRediTCOLONresources = "CRediT:resources"
    # Programming, software development; designing computer programs; implementation of the computer code and supporting algorithms; testing of existing code components.
    CRediTCOLONsoftware = "CRediT:software"
    # Oversight and leadership responsibility for the research activity planning and execution, including mentorship external to the core team.
    CRediTCOLONsupervision = "CRediT:supervision"
    # Verification, whether as a part of the activity or separate, of the overall replication/reproducibility of results/experiments and other research outputs.
    CRediTCOLONvalidation = "CRediT:validation"
    # Preparation, creation and/or presentation of the published work, specifically visualization/data presentation.
    CRediTCOLONvisualization = "CRediT:visualization"
    # Preparation, creation and/or presentation of the published work, specifically writing the initial draft (including substantive translation).
    CRediTCOLONwriting_original_draft = "CRediT:writing-original-draft"
    # Preparation, creation and/or presentation of the published work by those from the original research group, specifically critical review, commentary or revision -- including pre- or post-publication stages.
    CRediTCOLONwriting_review_editing = "CRediT:writing-review-editing"


class RoleEnum(str, Enum):

    # The investigator who had a primary role in conceiving and directing the study, and is ultimately solely responsible for the final content of the publication. Typically listed last.
    senior = "senior"
    # One of two or more senior investigators who played a major driving role is conceiving and directing the study, and has a major say in the final content of the publication.
    co_senior = "co_senior"
    # The researcher who conducted a major portion of the work, sometimes also playing a major role in conceiving and directing the study. Typically listed first.
    lead = "lead"
    # One of two or more researchers who jointly conducted the majority of the work
    co_lead = "co_lead"
    # A researcher who made major contributions to the work
    other_major = "other_major"
    # A researcher who was among many who made valuable contributions to the work, but it not among the major contributors
    contributor = "contributor"
    # A researcher who conducted the work independently, without the assistance of others
    sole = "sole"


class Bibliography(ConfiguredBaseModel):

    entries: Optional[List[Entry]] = Field(
        default_factory=list, description="""A collection of bibliographic entries"""
    )


class Entry(ConfiguredBaseModel):

    type: Optional[TypeEnum] = Field(None)
    title: str = Field(...)
    authors: Optional[List[str]] = Field(default_factory=list)
    authors_verbatim: Optional[str] = Field(
        None,
        description="""A verbatim representation of the authors, as it appears in the original source. This is useful for cases where the original source uses a non-standard format for representing authors, such as a list of names separated by commas.""",
    )
    journal: Optional[str] = Field(None)
    repository: Optional[str] = Field(None)
    conference_proceedings: Optional[str] = Field(None)
    urls: Optional[List[str]] = Field(default_factory=list)
    urls_verbatim: Optional[str] = Field(None)
    ceur_ws_url: Optional[str] = Field(None)
    doi: Optional[str] = Field(None)
    pmid: Optional[str] = Field(
        None, description="""A unique identifier for a published article in the PubMed database"""
    )
    pmcid: Optional[str] = Field(None)
    arxiv_id: Optional[str] = Field(None)
    chemrxiv_id: Optional[str] = Field(None)
    year: Optional[str] = Field(None)
    volume: Optional[str] = Field(None)
    issue: Optional[str] = Field(None)
    pages: Optional[str] = Field(None, description="""Number of pages within the container.""")
    num_authors: Optional[int] = Field(None)
    position: Optional[int] = Field(
        None,
        description="""Description for 'position' SlotDefinition: \"Specifies the location or order within the container.\"""",
    )
    rank: Optional[int] = Field(None)
    significance: Optional[float] = Field(None)
    role: Optional[RoleEnum] = Field(None)
    local_id: Optional[str] = Field(
        None,
        description="""Description: \"Unique identifier assigned to an item within the context of the container.\"""",
    )

    @field_validator("ceur_ws_url")
    def pattern_ceur_ws_url(cls, v):
        pattern = re.compile(r"^https?://ceur-ws.org/")
        if isinstance(v, list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid ceur_ws_url format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid ceur_ws_url format: {v}")
        return v


class Author(ConfiguredBaseModel):

    None


class Person(Author):

    None


class Organization(Author):

    None


class EntryToAuthorRelationship(ConfiguredBaseModel):
    """
    A relationship between an entry and an author, including the author's position in the author list. Note that the author is stored in a denormalized form, so
    """

    name: Optional[str] = Field(None, description="""The name of the agent""")
    contributor_type: Optional[ContributorType] = Field(
        None, description="""The type of contributor being represented"""
    )
    given_name: Optional[str] = Field(None, description="""The given name of the agent""")
    family_name: Optional[str] = Field(None, description="""The family name of the agent""")
    middle_names: Optional[str] = Field(None, description="""The middle names of the agent""")
    orcid: Optional[str] = Field(None, description="""The ORCID identifier of the agent""")
    affiliation: Optional[str] = Field(None, description="""The affiliation of the agent""")
    position: Optional[int] = Field(None, description="""The position of the author in the author list""")
    contributor_roles: Optional[ContributorRole] = Field(None)
    author_object: Optional[Author] = Field(None, description="""The author of the entry""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Bibliography.model_rebuild()
Entry.model_rebuild()
Author.model_rebuild()
Person.model_rebuild()
Organization.model_rebuild()
EntryToAuthorRelationship.model_rebuild()
