from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Parameter, Language, Contribution


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IParameter)
class Feature(Parameter, CustomModelMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    feature_type = Column(String)
    wals_id = Column(String)


@implementer(interfaces.ILanguage)
class Lect(Language, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    default_lect = Column(Boolean, default=True)
    region = Column(Unicode)
    base_language = Column(Unicode)


@implementer(interfaces.IContribution)
class ApicsContribution(Contribution, CustomModelMixin):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('lect.pk'))
    language = relationship(Lect)


#-----------------------------------------------------------------------------


class ParameterContribution(Base):
    """This is where we store the contribution-specific comments on the value
    assignment for a parameter.
    """
    comment = Column(Unicode)

    parameter_pk = Column(Integer, ForeignKey('parameter.pk'))
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))

    parameter = relationship('Parameter')
    contribution = relationship('Contribution', backref="comments")
