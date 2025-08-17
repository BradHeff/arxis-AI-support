from support import SupportBot
import logging

logging.basicConfig(level=logging.DEBUG)
try:
    b = SupportBot()
    print("SupportBot initialized ok")
except Exception as e:
    print("Failed to init SupportBot:", e)
