import pygame
import logging

logger = logging.getLogger(__name__)

class DebugTools:
    @staticmethod
    def log_keyboard_mapping():
        """打印键盘映射调试信息"""
        logger.debug("键盘映射测试:")
        logger.debug(f"标准E键码(pygame.K_e): {pygame.K_e}")
        logger.debug(f"E键名称: {pygame.key.name(pygame.K_e)}")
        
        for key in [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_RETURN]:
            logger.debug(f"键码 {key} 对应名称: {pygame.key.name(key)}")