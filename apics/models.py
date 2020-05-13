from collections import namedtuple

from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
from pyramid.decorator import reify

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, Language, Contribution, Source, Contributor, IdNameDescriptionMixin,
)
from clld.web.util.htmllib import literal

from apics.interfaces import IWals, ISurvey


@implementer(IWals)
class Wals(Base):
    id = Column(String, unique=True)
    parameter_pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    parameter = relationship(Parameter, backref=backref('wals', uselist=False))
    replacement_id = Column(Unicode)

    @property
    def name(self):
        return self.parameter.name

    def __json__(self, *args):
        return {'name': self.name}


class Phoible(object):
    def __init__(self, d):
        self.id = d['id']
        self.segment = d['segment']

    @property
    def url(self):
        return 'http://phoible.org/parameters/' + self.id


class WithContributorsMixin(object):
    @property
    def primary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id))]

    @property
    def secondary_contributors(self):
        return []

    def formatted_contributors(self):
        return ' and '.join(c.name for c in self.primary_contributors)


@implementer(interfaces.IParameter)
class Feature(CustomModelMixin, Parameter, WithContributorsMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    feature_type = Column(String)
    multivalued = Column(Boolean, default=False)
    wals_id = Column(Integer)
    wals_representation = Column(Integer)
    representation = Column(Integer)
    area = Column(Unicode)

    @property
    def authors(self):
        return [a for a in self.primary_contributors]

    def format_authors(self):
        apics = 'APiCS Consortium'
        if self.authors:
            return ', '.join(a.name for a in self.authors) + ' and the ' + apics
        return 'The ' + apics

    @property
    def phoible(self):
        phoible = self.jsondata.get('phoible')
        if phoible:
            return Phoible(phoible)

    def __str__(self):
        return literal(super(Feature, self).__str__())

    def __rdf__(self, request):
        if self.phoible:
            yield 'owl:sameAs', self.phoible.url


class FeatureAuthor(Base):
    feature_pk = Column(Integer, ForeignKey('feature.pk'))
    feature = relationship(Feature, backref='contributor_assocs')
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))
    ord = Column(Integer, default=1)
    contributor = relationship(Contributor, lazy=False, backref='feature_assocs')


@implementer(ISurvey)
class Survey(Base, IdNameDescriptionMixin, WithContributorsMixin):
    @property
    def citation_name(self):
        return '%s survey' % self.name


@implementer(interfaces.ILanguage)
class Lect(CustomModelMixin, Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    region = Column(Unicode)
    lexifier = Column(Unicode)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    lects = relationship(
        'Lect', foreign_keys=[language_pk], backref=backref('language', remote_side=[pk]))
    survey_pk = Column(Integer, ForeignKey('survey.pk'))
    survey = relationship(Survey, backref=backref('languages'))


GlossedText = namedtuple('GlossedText', 'pdf audio')


@implementer(interfaces.IContribution)
class ApicsContribution(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    language = relationship(Lect, backref=backref('contribution', uselist=False))

    survey_reference_pk = Column(Integer, ForeignKey('source.pk'))
    survey_reference = relationship(Source)

    @property
    def citation_name(self):
        return '%s structure dataset' % self.name

    @reify
    def glossed_text(self):
        return GlossedText(
            self.files.get('%s_gt.pdf' % self.id),
            self.files.get('%s_gt.mp3' % self.id))


class SurveyContributor(Base):
    survey_pk = Column(Integer, ForeignKey('survey.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))
    ord = Column(Integer, default=1)
    primary = Column(Boolean, default=True)
    survey = relationship(Survey, backref='contributor_assocs')
    contributor = relationship(Contributor, lazy=False, backref='survey_assocs')
