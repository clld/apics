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
from clld.db.models.common import Parameter, Language, Contribution, Source, Contributor
from clld.web.util.htmllib import literal

from apics.interfaces import IWals


class FeatureAuthor(Base):
    feature_pk = Column(Integer, ForeignKey('feature.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))
    ord = Column(Integer, default=1)
    contributor = relationship(Contributor, lazy=False)


@implementer(IWals)
class Wals(object):
    replacement_id = None

    def __init__(self, parameter=None):
        self.parameter = parameter

    @classmethod
    def mapper_name(cls):
        return 'Wals'


class Phoible(object):
    def __init__(self, d):
        self.id = d['id']
        self.segment = d['segment']

    @property
    def url(self):
        return 'http://phoible.org/parameters/' + self.id


@implementer(interfaces.IParameter)
class Feature(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    feature_type = Column(String)
    multivalued = Column(Boolean, default=False)
    wals_id = Column(Integer)
    wals_representation = Column(Integer)
    representation = Column(Integer)
    area = Column(Unicode)

    _authors = relationship(FeatureAuthor, order_by=[FeatureAuthor.ord])

    @property
    def authors(self):
        return [a.contributor for a in self._authors]

    def format_authors(self):
        apics = 'APiCS Consortium'
        if self.authors:
            return ', '.join(a.name for a in self.authors) + ' and the ' + apics
        return 'The ' + apics

    @property
    def phoible(self):
        phoible = self.jsondatadict.get('phoible')
        if phoible:
            return Phoible(phoible)

    def __unicode__(self):
        return literal(super(Feature, self).__unicode__())

    def __rdf__(self, request):
        if self.phoible:
            yield 'owl:sameAs', self.phoible.url


@implementer(interfaces.ILanguage)
class Lect(CustomModelMixin, Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    region = Column(Unicode)
    lexifier = Column(Unicode)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    lects = relationship(
        'Lect', foreign_keys=[language_pk], backref=backref('language', remote_side=[pk]))


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
            self.files.get('%s-gt.pdf' % self.id),
            self.files.get('%s-gt.mp3' % self.id))
