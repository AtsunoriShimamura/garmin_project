# mailer.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from dotenv import load_dotenv


# このファイルと同じ階層の .env を読む
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def send_weekly_csv(csv_path: str, to_email: str | None = None) -> None:
    """
    週間ランニングレポートのCSVをメールで送信する。

    - 送信元アドレス: GMAIL_ADDRESS（.env）
    - アプリパスワード: GMAIL_APP_PASSWORD（.env）
    - 送信先:
        * 引数 to_email が指定されていればそれを使用
        * None の場合は .env の MAIL_TO を使用（無ければ送信元と同じ）
    """
    sender = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    if to_email is None:
        to_email = os.environ.get("MAIL_TO", sender)

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "週間ランニングレポート（CSV添付）"

    body = "今週のランニング記録を添付します！"
    msg.attach(MIMEText(body, "plain"))

    # 添付ファイル
    csv_file = Path(csv_path)
    part = MIMEBase("application", "octet-stream")
    part.set_payload(csv_file.read_bytes())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={csv_file.name}",
    )
    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.send_message(msg)

    print(f"メール送信完了！ -> {to_email}")
