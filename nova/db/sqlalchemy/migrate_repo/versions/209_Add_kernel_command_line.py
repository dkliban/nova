from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Adding column to store the kernel command line
    meta = MetaData(bind=migrate_engine)
    instances = Table('instances', meta, autoload=True)
    cmdline = Column('cmdline', String(length=255))
    cmdline.create(instances)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade.
    meta = MetaData(bind=migrate_engine)
    instances = Table('instances', meta, autoload=True)
    instances.c.cmdline.drop()
