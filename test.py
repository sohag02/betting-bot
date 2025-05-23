import logging
from src.utils import save_daily_report, is_daily_report_generated, save_summary, generate_graphs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-[%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)


# save_daily_report()
# print(is_daily_report_generated())
save_summary()
# generate_graphs()