from sqlmodel import Session, select
from pro_1.config.db import connection
from pro_1.models.users import Role

def seed_roles():
    with Session(connection) as session:
        existing_roles = session.exec(select(Role)).all()
        if not existing_roles:
            session.add_all([Role(name="admin"), Role(name="client")])
            session.commit()
