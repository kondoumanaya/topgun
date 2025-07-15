"""Custom exceptions for topgun library"""


class TradingBotError(Exception):
    """Base exception for trading bot errors"""
    pass


class ConfigurationError(TradingBotError):
    """Configuration related errors"""
    pass


class APIError(TradingBotError):
    """API related errors"""
    pass


class DatabaseError(TradingBotError):
    """Database related errors"""
    pass


class NotificationError(TradingBotError):
    """Notification related errors"""
    pass
