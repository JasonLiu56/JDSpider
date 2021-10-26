import loguru

logger = loguru.logger
logger.add('./log.txt', rotation='1 day', retention='1 months')