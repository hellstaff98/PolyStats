import logging
from typing import Optional, TYPE_CHECKING

#from fastapi_cache import FastAPICache
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
)
from fastapi_users.db import BaseUserDatabase

from core.config import settings
from core.types.user_id import UserIdType
from core.models import User, Subject
from services.unversity import uni_service

#from mailing.send_email_confirmed import send_email_confirmed
#from mailing.send_verification_email import send_verification_email
#from utils.webhooks.user import send_new_user_notification


from fastapi import Request, BackgroundTasks
from fastapi_users.password import PasswordHelperProtocol

log = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    def __init__(
        self,
        user_db: BaseUserDatabase[User, UserIdType],
        password_helper: Optional["PasswordHelperProtocol"] = None,
        background_tasks: Optional["BackgroundTasks"] = None,
    ):
        super().__init__(user_db, password_helper)
        self.background_tasks = background_tasks

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        session = self.user_db.session
        try:
            # 1. Получаем ID группы (возвращает int)
            ext_group_id = await uni_service.get_group_id_by_number(user.group_name)

            # 2. Сохраняем ID как строку (чтобы не было конфликта типов в БД)
            user.group_id = str(ext_group_id)
            session.add(user)

            # 3. Получаем список уникальных предметов
            subjects_names = await uni_service.get_subjects_list(ext_group_id)

            # 4. Создаем записи в таблице subjects
            for name in subjects_names:
                new_subject = Subject(
                    name=name,
                    user_id=user.id
                )
                session.add(new_subject)

            await session.commit()

        except Exception as e:
            await session.rollback()
            print(f"Registration sync error: {e}")

    # async def on_after_forgot_password(
    #     self,
    #     user: User,
    #     token: str,
    #     request: Optional["Request"] = None,
    # ):
    #     log.warning(
    #         "User %r has forgot their password. Reset token: %r",
    #         user.id,
    #         token,
    #     )
    #
    # async def on_after_request_verify(
    #     self,
    #     user: User,
    #     token: str,
    #     request: Optional["Request"] = None,
    # ):
    #     log.warning(
    #         "Verification requested for user %r. Verification token: %r",
    #         user.id,
    #         token,
    #     )
    #     verification_link = request.url_for("verify_email").replace_query_params(
    #         token=token
    #     )
    #     self.background_tasks.add_task(
    #         send_verification_email,
    #         user=user,
    #         verification_link=str(verification_link),
    #     )
    #
    # async def on_after_verify(
    #     self,
    #     user: User,
    #     request: Optional["Request"] = None,
    # ):
    #     log.warning(
    #         "User %r has been verified",
    #         user.id,
    #     )
    #
    #     self.background_tasks.add_task(
    #         send_email_confirmed,
    #         user=user,
    #     )