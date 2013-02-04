from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
#from clld.db.models.common import Language


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
#@implementer(interfaces.ILanguage)
#class {{package}}Language(Language, CustomModelMixin):
#    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)

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
