import email
import click
import csv
import logging
import secrets
import os
from typing import Optional

from inquizitor import crud, models
from inquizitor.commands.initial_data import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.argument('email')
@click.argument('last_name')
@click.argument('first_name')
def create_account(
    email: str, last_name: str, first_name: str, 
    is_student: bool = True, is_teacher: bool = False, is_admin: bool = False,
    password: str = None
) -> None:
    """
        Create a student account with the provided details, 
        and then send an email containing login credentials
        to get app access.
    """
    last_name = last_name.capitalize()
    first_name = first_name.capitalize()
    username = f'{last_name}{"".join([w[0] for w in first_name])}'.lower()
    user_in = models.UserCreate(
        username=username,
        email=email,
        full_name=f'{last_name}, {first_name}',
        last_name=last_name,
        first_name=first_name,
        is_student=is_student,
        is_teacher=is_teacher,
        is_admin=is_admin,
        password=password or secrets.token_hex(4),
    )
    try:
        user = crud.user.create(db, obj_in=user_in)
        return 1
    except:
        logger.info(f"Account with email {email} or username {username} already exists!")
        return 0

    # send email

@click.command()
@click.argument('filepath')
@click.argument('heroku_app', required=False)
def create_accounts(filepath: str, heroku_app: Optional[str] = None):
    """
        This creates accounts by reading from a csv file.
    
        # TESTING AN OPTION
        # This command should only be called from local. 
        # And only for the purposes of generating accounts in a 
        # production setting.
    """
    if not filepath.endswith('.csv'):
        logger.info('File should be in CSV')
        return

    base_command = f'heroku run python main.py create-student %s --app {heroku_app}'
    if not heroku_app:
        base_command = 'python main.py create-account %s'
        
    total_accounts = 0
    with open(filepath, newline='') as csvf:
        account_reader = csv.reader(csvf)
        email_index, fullname_index = None, None
        logger.info('Creating accounts...')
        for i, row in enumerate(account_reader):
            if i == 0:
                try:
                    email_index = row.index('Email Address')
                    fullname_index = row.index('Full Name')
                except:
                    logger.info('File does not contain required headers: "Email Address" and "Full Name"')
                    return
            else:
                last_name, first_name = row[fullname_index].split(',')
                res = os.system(base_command % f'{row[email_index]} "{last_name}" "{first_name.strip()}"')
                total_accounts += 0 if res == 2 else res

    logger.info(f'Successfully created {total_accounts} accounts!')
                