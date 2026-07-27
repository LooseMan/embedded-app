import os
import logging
import sys

# 環境変数からログレベルを取得（デフォルト: INFO）
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# ログ出力例：
# 2026-07-27 01:42:02,015 [INFO] service.py:13 calc_add() start.
# 2026-07-27 01:42:02,027 [INFO] service.py:16 calc_add() end.
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s() %(message)s",
    # デフォルトは標準エラー出力に出力、container用に標準出力を出力先に設定
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# 汎用ヘルパー関数（stacklevel=2 で呼び出し元を記録）

# ログ出力
def info_log(msg: str):
    logger.info(msg, stacklevel=2)

# デバッグログ出力
# デフォルト非表示、動作確認時に環境変数（ログレベル）を変更して表示する運用を想定
def debug_log(msg: str):
    logger.debug(msg, stacklevel=2)

# エラーログ出力
# 本関数はexceptブロック内で使用すること
# （ログ出力後、自動でスタックトレースが出ます）
def error_log(msg: str):
    logger.error(msg, stacklevel=2, exc_info=True)
