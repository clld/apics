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


class FeatureAuthor(Base):
    feature_pk = Column(Integer, ForeignKey('feature.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))
    ord = Column(Integer, default=1)
    contributor = relationship(Contributor, lazy=False)


@implementer(interfaces.IParameter)
class Feature(Parameter, CustomModelMixin):
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

    def __unicode__(self):
        return literal(super(Feature, self).__unicode__())


@implementer(interfaces.ILanguage)
class Lect(Language, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    region = Column(Unicode)
    lexifier = Column(Unicode)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    lects = relationship(
        'Lect', foreign_keys=[language_pk], backref=backref('language', remote_side=[pk]))


GlossedText = namedtuple('GlossedText', 'pdf audio')


@implementer(interfaces.IContribution)
class ApicsContribution(Contribution, CustomModelMixin):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    language = relationship(Lect, backref=backref('contribution', uselist=False))

    @property
    def citation_name(self):
        return '%s structure dataset' % self.name

    @reify
    def glossed_text(self):
        audio, pdf = None, None
        for file_ in self.files:
            if file_.name == 'glossed-text-audio':
                audio = file_
            if file_.name == 'glossed-text-pdf':
                pdf = file_
        return GlossedText(pdf, audio)
