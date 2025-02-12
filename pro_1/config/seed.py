from sqlmodel import Session, select
from pro_1.config.db import connection
from pro_1.models.Schemas import Role

def seed_roles():
    with Session(connection) as session:
        existing_roles = session.exec(select(Role)).all()
        if not existing_roles:
            roles=[Role(name="super_admin"),Role(name="simple_admin"), Role(name="client"),]
            session.add_all(roles)
            session.commit()
            print("Roles seeded successfully")
        else:
            print("Roles already seeded")    


if __name__ == "__main__":
    seed_roles()