from telegrambot.models import UserProfile, UserSettings, MessageFromUser
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from telegrambot.bot_send import send_telegram_chat
from telegram.ext.handler import Handler
from telegrambot.wizard import SYMBOL_WIZARD
from telegram import ChatAction


class PreprocessHandler(Handler):
    def __init__(self,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(PreprocessHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)
        self.pass_groups = pass_groups
        self.pass_group_dict = pass_groupdict

    def check_update(self, update):
        return True

    def handle_update(self, update, dispatcher):
        print("PreProcess")
        print(update)
        if hasattr(update, 'message') and update.message:
            dispatcher.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
            if hasattr(update.message, 'chat') and update.message.chat.type == 'private':
                profile, new_user = verify_user(update.message.chat.id,
                                                update.message.chat.first_name,
                                                update.message.chat.last_name,
                                                update.message.chat.username,
                                                'private')
                update.message.chat.up = profile
                if new_user:
                    welcome(dispatcher, update)
                    x = update.message.text
                    update.message.text = '/symbols'
                    if SYMBOL_WIZARD.check_update(update):
                        SYMBOL_WIZARD.handle_update(update, dispatcher)
                    update.ignore = 'True'
                    update.message.text = x

            if hasattr(update.message, "from_user"):
                profile, new_user = verify_user(update.message.chat.id,
                                                update.message.chat.first_name,
                                                update.message.chat.last_name,
                                                update.message.chat.username,
                                                'from_user')
                update.message.from_user.up = profile

        if hasattr(update, 'callback_query') and update.callback_query:
            # dispatcher.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
            profile, new_user = verify_user(update.callback_query.from_user.id,
                                            update.callback_query.from_user.first_name,
                                            update.callback_query.from_user.last_name,
                                            update.callback_query.from_user.username,
                                            'callback')
            update.callback_query.from_user.up = profile

            if hasattr(update.callback_query, 'message') and update.callback_query.message.chat.type == 'private':
                profile, new_user = verify_user(update.callback_query.message.chat.id,
                                                update.callback_query.message.chat.first_name,
                                                update.callback_query.message.chat.last_name,
                                                update.callback_query.message.chat.username,
                                                'private')
                update.callback_query.message.chat.up = profile

                # if True:
                #     up.last_chat = timezone.now()
                #     up.activated = True
                #     if not up.user_settings:
                #         up.user_settings = UserSettings.objects.create()
                #
                #     up.save()
        log(update)
        print("End-PreProcess")


def log(update):
    if hasattr(update, 'message') and update.message:
        MessageFromUser.objects.create(user=update.message.chat.up.user,
                                       message_id=update.message.message_id,
                                       chat_id=update.message.chat_id,
                                       type=1,
                                       message=update.message.text)

    if hasattr(update, 'callback_query') and update.callback_query:
        MessageFromUser.objects.create(user=update.callback_query.from_user.up.user,
                                       chat_id=update.callback_query.from_user.id,
                                       type=3,
                                       message=update.callback_query.data)


def verify_user(telegram_id, first_name, last_name, username, type_update='private'):
    try:
        up = UserProfile.objects.get(telegram_id=telegram_id)
        if type_update == 'private' and not up.private:
            up.private = True
            up.save()
            return up, True
        return up, False
    except ObjectDoesNotExist:
        if len(username) == 0:
            username = telegram_id

        user = User.objects.create_user(username=username,
                                        first_name=first_name,
                                        last_name=last_name)

        user_setting = UserSettings.objects.create()
        up = UserProfile.objects.create(user=user,
                                        telegram_id=telegram_id,
                                        user_settings=user_setting,
                                        last_chat=timezone.now())
        if not type_update == 'private':
            up.private = False
        elif type_update == 'private':
            up.private = True
        up.save()
        return up, True


def welcome(dispatcher, update):
    text = '''
        سلام  %s %s
        به سرویس هوشمند %s خوش آمدید.
        ''' % (update.message.chat.first_name, "✌", settings.PROJECT_FA_NAME)

    send_telegram_chat(dispatcher.bot, update.message.chat.id, text, ps=False)
