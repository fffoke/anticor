from bot.app.handlers.start import router as start_router
from bot.app.handlers.profile import router as profile_router
from bot.app.handlers.report import router as report_router
from bot.app.handlers.tips import router as tips_router
from bot.app.handlers.admin import router as admin_router
from bot.app.handlers.sos import router as sos_router

all_handlers = [
    start_router,
    profile_router,
    report_router,
    tips_router,
    admin_router,
    sos_router
]


