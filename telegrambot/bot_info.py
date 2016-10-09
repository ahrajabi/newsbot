from django.conf import settings
from telegram.emoji import Emoji

commands = '''
help - راهنما
list - لیست عبارات شما
live - مشاهده‌ی زنده‌ی اخبار شما
stop - متوقف کردن بات
start - شروع کار با بات یا رفع توقف
'''

Description = '''
خبرِمن تمام آن‌چه به زبان فارسی منتشر می‌شود را دنبال می‌کند و آن چه به سلیقه‌ی شما نزدیک باشد را برای شما پالایش می‌کند.
💰 بورس
📱 تکنولوژی
🏅 ورزشی
👥 اجتماعی
🎶 موسیقی
🎞 سینما
💡 کارآفرینی
و...
پس "start" 👇را لمس کنید تا شروع کنیم.


ℹ
 ️روبات تلگرام تنها به نام، نام‌خانوادگی و نام‌کاربری شما دسترسی دارد. و هیچ گونه اطلاعات دیگری از شما قابل دریافت نیست. برای اطلاعات بیشتر به سایت رسمی تلگرام مراجعه نمایید.

'''

About = '''
🌟خبرِمن به شما کمک می‌کند تا اخبار تمام خبرگزاری‌ها را آن‌طور که می‌خواهید مدیریت کنید. همین الان شروع کنید ...
'''

botpromote = Emoji.VICTORY_HAND
botpromote += 'دستیار هوشمند خبری شما   '
botpromote += '\n'
botpromote += settings.BOT_NAME

help = '''
🕴         اگر میخواهید اخبار مرتبط با شغل خود را ببیند (مثلا بورس)
🎻 یا خبرهای خواننده یا ورزشکار مورد علاقه خود را دنبال کنید (مثلا محسن چاوشی )
🏅 یا از اخبار پیرامون حادثه ای خاص مطلع شوید (مثلا المپیک)
 یا هر خبر دیگری

کلمه دلخواهتان را بنویسیدتا اخبار مرتبط با آن را ببینید و
اگر به موضوع علاقه مند هستید دسته های پیشنهادی را انتخاب کنید تا از این پس خبر های مرتبط به صورت برخط برای شما ارسال شود.

پس شروع کنید و کلمه مورد نظرتان را از طریق کادر پایین ارسال کنید %s

'''

next = '''
🕴         اگر میخواهید اخبار مرتبط با شغل خود را ببیند (مثلا بورس)
🎻 یا خبرهای خواننده یا ورزشکار مورد علاقه خود را دنبال کنید (مثلا محسن چاوشی )
🏅 یا از اخبار پیرامون حادثه ای خاص مطلع شوید (مثلا المپیک)
 یا هر خبر دیگری کلمه دلخواهتان را بنویسیدتا اخبار مرتبط با آن را ببینید و
اگر به موضوع علاقه مند هستید دسته های پیشنهادی را انتخاب کرده و به لیست خود اضافه کنید تا انطور که میخواهید انها را دریافت کنید.
▶ اگر دکمه اخبار زنده را بزنید این امکان برای شما فعال می شود که اخبار مربوط به دسته های خود را به صورت بر خط دریافت کنید
⏹ و هر زمان که بخواهید با فشردن دکمه توقف اخبار زنده میتوانید دریافت لحظه ای اخبار را متوقف کنید.
📢 با زدن دکمه لیست خبرها ، لیستی از عناوین خبر های مرتبط با دسته های خود که انها را هنوز مطالعه نکرده اید دریافت میکنید.
🌟 با فشردن دکمه خبر ويژه یک خبر از از خبرهای روز برای شما ارسال میشود و اگر تمایل داشته باشید با استفاده از تنظیماتی که برایتان ارسال میشود میتوانید اخبار حوزه خبری خاص را برای ارسال انتخاب کنید.
پس شروع کنید ... %s
'''
