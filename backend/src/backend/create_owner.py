from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend import models
from backend.database import SessionLocal
from backend.enums import Role
from backend.schemas import UserCreate


def main():
    with SessionLocal() as db:
        owner_exists = db.scalar(
            select(models.User.id).where(models.User.role == Role.OWNER).limit(1)
        )

        if owner_exists:
            print(
                "\nERROR: Owner already exists, please use the API to create other users.\n"
            )
            return

        username = input("Username: ").strip()
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        password = getpass("Password (min 8 char): ")

        if password != getpass("Confirm password: "):
            print("Password do not match")
            return

        try:
            data = UserCreate(
                username=username,
                email=email,
                name=name,
                phone=phone,
                role=Role.OWNER,
                status=True,
                password=password,
            )

        except ValidationError as e:
            print(e)
            return

        owner = models.User(
            username=data.username,
            email=data.email,
            name=data.name,
            phone=data.phone,
            role=data.role,
            status=data.status,
        )
        owner.set_password(data.password)

        try:
            db.add(owner)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("A user with this username, email or phone already exists")
            return

        print(f"Owner '{owner.username}' created successfully")


if __name__ == "__main__":
    main()
