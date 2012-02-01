# -*- coding: utf-8 -*-
__author__ = 'kivsiak@gmail.com'

from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import PickleType, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    amf_alias = "ru.magicink.thc.domain.User"
    uuid = Column(UUID, primary_key=True)
    email = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    password = Column(String)
    lastActivity = Column(TIMESTAMP)
    currentProject_id = Column(UUID, ForeignKey("projects.uuid", use_alter=True, name='fk_current_project_id'),
        nullable=True)
    currentProject = relationship("Project")
    currentSpace_id = Column(UUID, ForeignKey("spaces.uuid", use_alter=True, name='fk_current_space_id'), nullable=True)
    currentSpace = relationship("Space")
    avatarUrl = Column(String)
    facebookID = Column(String)
    googleID = Column(String)

    def __init__(self, uuid=None, *args, **kv):
        self.uuid = str(uuid.uuid4())


class CompanyAccess(Base):
    __tablename__ = 'company_access'
    left_id = Column(UUID, ForeignKey('companies.uuid'), primary_key=True)
    right_id = Column(UUID, ForeignKey('users.uuid'), primary_key=True)
    access = Column(String(4))
    user = relationship('User')

    def __init__(self, user, level='xxxx'):
        self.user = User
        self.level = level


class Company(Base):
    __tablename__ = 'companies'
    amf_alias = "ru.magicink.thc.domain.Company"
    uuid = Column(UUID, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String, nullable=True)
    founder_id = Column(UUID, ForeignKey('users.uuid', name="fk_founder_id"))
    founder = relationship("User")
    users = relationship('CompanyAccess')


class ProjectAccess(Base):
    __tablename__ = 'project_access'
    left_id = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    right_id = Column(UUID, ForeignKey('users.uuid'), primary_key=True)
    access = Column(String(4))
    user = relationship('User')

    def __init__(self, user, level='xxxx'):
        self.user = User
        self.level = level


class Project(Base):
    __tablename__ = 'projects'
    amf_alias = "ru.magicink.thc.domain.Project"
    uuid = Column(UUID, primary_key=True)
    name = Column(String)
    slug = Column(String)
    company_id = Column(UUID, ForeignKey('companies.uuid'))
    company = relationship("Company", backref=backref('projects', order_by=uuid)) #reference
    users = relationship("ProjectAccess")


class SpaceAccess(Base):
    __tablename__ = 'space_access'

    left_id = Column(UUID, ForeignKey('spaces.uuid'), primary_key=True)
    right_id = Column(UUID, ForeignKey('users.uuid'), primary_key=True)
    access = Column(String(4))
    user = relationship('User')

    def __init__(self, user, level='xxxx'):
        self.user = User
        self.level = level


class Space(Base):
    __tablename__ = 'spaces'
    amf_alias = "ru.magicink.thc.domain.Space"
    uuid = Column(UUID, primary_key=True)
    name = Column(String)
    slug = Column(String)
    project_id = Column(UUID, ForeignKey('projects.uuid'))
    project = relationship("Project", backref=backref("spaces", order_by=uuid))
    users = relationship("SpaceAccess")


class Frame(Base):
    amf_alias = "ru.magicink.thc.domain.Frame"
    __tablename__ = 'frames'
    uuid = Column(UUID, primary_key=True)
    space_id = Column(UUID, ForeignKey('spaces.uuid'))
    project = relationship("Space", backref=backref("frames", order_by=uuid))
    type = Column(String)

    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    content = Column(PickleType) #dict type

    parentFrame_id = Column(UUID, ForeignKey('frames.uuid', use_alter=True, name='fk_parent_frame'))
    parentFrame = relationship("Frame", primaryjoin=uuid == parentFrame_id)

    rightFrame_id = Column(UUID, ForeignKey('frames.uuid', use_alter=True, name='fk_right_frame'))
    rightFrame = relationship("Frame", primaryjoin=uuid == rightFrame_id)

    leftFrame_id = Column(UUID, ForeignKey('frames.uuid', use_alter=True, name='fk_left_frame'))
    leftFrame = relationship("Frame", primaryjoin=uuid == leftFrame_id)

    topFrame_id = Column(UUID, ForeignKey('frames.uuid', use_alter=True, name='fk_top_frame'))
    topFrame = relationship("Frame", primaryjoin=uuid == parentFrame_id)

    bottomFrame_id = Column(UUID, ForeignKey('frames.uuid', use_alter=True, name='fk_bottom_frame'))
    bottomFrame = relationship("Frame", primaryjoin=uuid == topFrame_id)

    deleted = Column(Boolean, default=False)
    persisted = False
    updated = Column(TIMESTAMP)
